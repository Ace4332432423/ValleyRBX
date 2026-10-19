"""
Discord Rich Presence integration for ValleyRBX / Roblox Studio.
Pure Python, zero external dependencies (direct UNIX IPC socket communication).
Optimized for Linux, CachyOS, Flatpak Discord, Vesktop, WebCord, and Discord Canary.
"""

from __future__ import annotations
import glob
import json
import os
import socket
import struct
import threading
import time
import urllib.request
from typing import Any, Dict, List, Optional
import uuid

DEFAULT_CLIENT_ID = "1159891020956323923"  # Official Roblox Studio Discord Application ID


class DiscordIPCClient:
    """Manages raw IPC connection to local Discord client."""

    def __init__(self, client_id: str = DEFAULT_CLIENT_ID) -> None:
        self.client_id = client_id
        self.sock: Optional[socket.socket] = None
        self.connected = False

    @staticmethod
    def find_ipc_socket() -> Optional[str]:
        """Locates the Discord IPC UNIX socket across system and flatpak locations."""
        uid = os.getuid()
        runtime_dir = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{uid}")

        candidate_patterns = [
            f"{runtime_dir}/discord-ipc-[0-9]",
            f"{runtime_dir}/app/*/discord-ipc-[0-9]",
            f"{runtime_dir}/snap.discord/discord-ipc-[0-9]",
            "/tmp/discord-ipc-[0-9]",
        ]

        for pattern in candidate_patterns:
            matches = sorted(glob.glob(pattern))
            for path in matches:
                if os.path.exists(path):
                    return path
        return None

    def connect(self) -> bool:
        """Connects to the Discord IPC socket and sends the initial handshake."""
        sock_path = self.find_ipc_socket()
        if not sock_path:
            return False

        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.settimeout(2.5)
            self.sock.connect(sock_path)

            # Opcode 0: HANDSHAKE
            handshake_payload = {"v": 1, "client_id": self.client_id}
            self._send(0, handshake_payload)

            # Read initial response
            op, resp = self._receive()
            if op == 1 and resp.get("cmd") == "DISPATCH" and resp.get("evt") == "READY":
                self.connected = True
                return True
            elif op == 1:
                self.connected = True
                return True
        except Exception:
            self.close()
        return False

    def _send(self, opcode: int, payload: Dict[str, Any]) -> None:
        """Encodes and sends an IPC frame: <opcode: uint32 LE> <length: uint32 LE> <payload>."""
        if not self.sock:
            raise ConnectionError("Socket not open")
        data = json.dumps(payload).encode("utf-8")
        header = struct.pack("<II", opcode, len(data))
        self.sock.sendall(header + data)

    def _receive(self) -> tuple[int, Dict[str, Any]]:
        """Receives and decodes an IPC frame."""
        if not self.sock:
            raise ConnectionError("Socket not open")
        header = self.sock.recv(8)
        if len(header) < 8:
            raise ConnectionError("Incomplete header")
        opcode, length = struct.unpack("<II", header)
        buf = bytearray()
        while len(buf) < length:
            chunk = self.sock.recv(min(length - len(buf), 4096))
            if not chunk:
                break
            buf.extend(chunk)
        payload = json.loads(buf.decode("utf-8"))
        return opcode, payload

    def set_activity(self, activity: Dict[str, Any]) -> bool:
        """Sends SET_ACTIVITY command."""
        if not self.connected or not self.sock:
            return False
        try:
            payload = {
                "cmd": "SET_ACTIVITY",
                "args": {
                    "pid": os.getpid(),
                    "activity": activity,
                },
                "nonce": str(uuid.uuid4()),
            }
            self._send(1, payload)
            # Read response without blocking indefinitely
            self.sock.settimeout(1.0)
            try:
                self._receive()
            except socket.timeout:
                pass
            return True
        except Exception:
            self.close()
            return False

    def close(self) -> None:
        """Closes the socket cleanly."""
        self.connected = False
        if self.sock:
            try:
                # Opcode 2: CLOSE
                self._send(2, {})
            except Exception:
                pass
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None


class DiscordRPCManager:
    """
    High-level manager for Roblox Studio Rich Presence.
    Runs in a background thread, maintains connection, parses logs, and updates presence.
    """

    def __init__(self, client_id: str = DEFAULT_CLIENT_ID) -> None:
        self.client = DiscordIPCClient(client_id)
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.start_time = int(time.time())

        # Presence State
        self.current_place_id: Optional[int] = None
        self.place_name: Optional[str] = None
        self.universe_id: Optional[int] = None
        self.doc_state: str = "Developing a place"  # "Idling", "Developing a place", "Editing Script"
        self.doc_detail: str = "ValleyRBX"
        self.needs_update = True
        self.lock = threading.Lock()

    def start(self) -> None:
        """Starts the RPC background worker."""
        if self.running:
            return
        self.running = True
        self.start_time = int(time.time())
        self.thread = threading.Thread(target=self._worker_loop, daemon=True, name="DiscordRPCWorker")
        self.thread.start()

    def stop(self) -> None:
        """Stops the RPC worker and closes the connection."""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        self.client.close()

    def handle_log_line(self, line: str) -> None:
        """
        Parses Studio log output for status changes matching Vinegar's exact triggers:
        - [FLog::CloseDataModel] Setting place ID <id>
        - [FLog::RobloxDocManager] Setting current doc to type <type>
        """
        stripped = line.strip()

        # Place ID detection
        place_entry = "[FLog::CloseDataModel] Setting place ID "
        if place_entry in stripped:
            idx = stripped.find(place_entry)
            id_str = stripped[idx + len(place_entry):].split()[0]
            try:
                place_id = int(id_str)
                with self.lock:
                    if self.current_place_id != place_id:
                        self.current_place_id = place_id
                        self.place_name = None
                        self.needs_update = True
                # Fetch place metadata in separate thread
                threading.Thread(target=self._fetch_place_details, args=(place_id,), daemon=True).start()
            except ValueError:
                pass

        # Document / View detection
        doc_entry = "[FLog::RobloxDocManager] Setting current doc to type "
        if doc_entry in stripped:
            idx = stripped.find(doc_entry)
            doc_type = stripped[idx + len(doc_entry):].split()[0]
            with self.lock:
                if doc_type == "-1":
                    self.doc_state = "Idling"
                    self.doc_detail = "In Main Menu"
                elif doc_type == "0":
                    self.doc_state = "Developing a place"
                    if self.place_name:
                        self.doc_detail = self.place_name
                    elif self.current_place_id:
                        self.doc_detail = f"Place ID {self.current_place_id}"
                    else:
                        self.doc_detail = "Roblox Studio"
                elif doc_type == "2":
                    self.doc_state = "Editing Script"
                    if self.place_name:
                        self.doc_detail = self.place_name
                    elif self.current_place_id:
                        self.doc_detail = f"Place ID {self.current_place_id}"
                self.needs_update = True

    def _fetch_place_details(self, place_id: int) -> None:
        """Queries Roblox API for the Place name."""
        try:
            url = f"https://games.roblox.com/v1/games/multiget-place-details?placeIds={place_id}"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "ValleyRBX/1.0 (Linux; CachyOS)"},
            )
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    if data and isinstance(data, list) and len(data) > 0:
                        name = data[0].get("name")
                        universe = data[0].get("universeId")
                        with self.lock:
                            if name:
                                self.place_name = name
                            if universe:
                                self.universe_id = universe
                            self.needs_update = True
        except Exception:
            pass

    def _build_activity(self) -> Dict[str, Any]:
        """Builds Discord Rich Presence activity object."""
        with self.lock:
            details = self.doc_detail if self.doc_detail else "Roblox Studio"
            state = self.doc_state if self.doc_state else "Developing"

            small_img = ""
            small_text = ""
            if self.doc_state == "Editing Script":
                small_img = "script"
                small_text = "Writing Code"
            elif self.doc_state == "Developing a place":
                small_img = "place"
                small_text = "Building & Testing"

            activity: Dict[str, Any] = {
                "details": details,
                "state": state,
                "timestamps": {
                    "start": self.start_time,
                },
                "assets": {
                    "large_image": "studio",
                    "large_text": "Roblox Studio (ValleyRBX)",
                },
            }

            if small_img:
                activity["assets"]["small_image"] = small_img
                activity["assets"]["small_text"] = small_text

            return activity

    def _worker_loop(self) -> None:
        """Background thread loop to keep connection alive and send presence updates."""
        retry_delay = 5.0
        last_activity_push = 0.0

        while self.running:
            now = time.time()

            # Connect if not connected
            if not self.client.connected:
                ok = self.client.connect()
                if not ok:
                    time.sleep(retry_delay)
                    continue
                else:
                    self.needs_update = True

            # Send presence updates
            if self.needs_update or (now - last_activity_push > 15.0):
                activity = self._build_activity()
                ok = self.client.set_activity(activity)
                if ok:
                    self.needs_update = False
                    last_activity_push = now
                else:
                    self.client.close()

            time.sleep(1.0)

        self.client.close()
