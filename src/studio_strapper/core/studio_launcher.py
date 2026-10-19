"""
Roblox Studio Launcher for Studio Strapper.
Handles process execution, environment variable construction, DLL overrides,
Gamescope integration, and log streaming.
"""

from __future__ import annotations
import os
import shutil
import subprocess
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from PySide6.QtCore import QObject, Signal

from studio_strapper.core.discord_rpc import DiscordRPCManager
from studio_strapper.core.fastflags import FastFlagManager
from studio_strapper.core.wine_runner import WineRunner


class StudioLauncher(QObject):
    """Manages launching Roblox Studio with all configured overrides and monitoring output."""

    process_started = Signal(int)  # PID
    process_exited = Signal(int)   # Exit code
    log_emitted = Signal(str)      # Real-time log line

    def __init__(self) -> None:
        super().__init__()
        self.active_process: Optional[subprocess.Popen] = None
        self.log_callbacks: List[Callable[[str], None]] = []
        self.flag_manager = FastFlagManager()
        self.wine_runner = WineRunner()
        self.discord_rpc: Optional[DiscordRPCManager] = None

    def is_running(self) -> bool:
        """Returns True if Studio process is actively running."""
        return self.active_process is not None and self.active_process.poll() is None

    def add_log_listener(self, callback: Callable[[str], None]) -> None:
        """Register a callback for streaming log lines."""
        self.log_callbacks.append(callback)

    def log(self, message: str) -> None:
        """Broadcast log message to all registered listeners."""
        for cb in self.log_callbacks:
            try:
                cb(message)
            except Exception:
                pass

    def find_studio_executable(self, prefix: Path) -> Optional[Path]:
        """Finds RobloxStudioBeta.exe in installed versions or Wine prefix."""
        # 1. Check ~/.local/share/vinegar/versions/
        versions_dir = Path.home() / ".local/share/vinegar/versions"
        if versions_dir.exists():
            for v_dir in sorted(versions_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
                exe = v_dir / "RobloxStudioBeta.exe"
                if exe.exists():
                    return exe

        # 2. Check inside the prefix drive_c
        appdata_roblox = prefix / "drive_c" / "users"
        if appdata_roblox.exists():
            for p in appdata_roblox.glob("**/RobloxStudioBeta.exe"):
                if p.is_file():
                    return p

        return None

    def build_dll_overrides(self, renderer: str) -> str:
        """Constructs WINEDLLOVERRIDES based on renderer choice."""
        if "DXVK" in renderer or "D3D11" in renderer:
            return "d3d11,dxgi=n,b"
        elif "D3D12" in renderer or "VKD3D" in renderer:
            return "d3d12,dxgi=n,b"
        elif "OpenGL" in renderer:
            return "d3d11=d;dxgi=d"
        return ""

    def launch(
        self,
        prefix_path: Path,
        runner_path: Path,
        renderer: str,
        cef_mode: str,
        env_vars: Dict[str, str],
        user_fastflags: Dict[str, Any],
        use_gamescope: bool = False,
        gamescope_args: str = "",
        discord_rpc: bool = False,
        use_gamemode: bool = True,
        debug_logs: bool = False,
        override_version: str = "",
        override_channel: str = "",
        on_exit: Optional[Callable[[int], None]] = None,
    ) -> bool:
        """Launches Roblox Studio with complete environment setup, Discord RPC, GameMode, and asynchronous log streaming."""
        self.log("=" * 60)
        self.log(f"🚀 Initializing Studio Strapper Launch Pipeline...")
        self.log(f"Prefix: {prefix_path}")
        self.log(f"Runner: {runner_path}")
        self.log(f"Renderer: {renderer} | CEF Mode: {cef_mode}")
        if discord_rpc:
            self.log("✨ Feature: Discord Rich Presence active")
        if use_gamemode:
            self.log("⚡ Feature: GameMode enabled")
        if debug_logs:
            self.log("🐞 Feature: Debug logging active")
        if override_version:
            self.log(f"📌 Deployment Version Override: {override_version}")
        if override_channel:
            self.log(f"🌐 Update Channel Override: {override_channel}")

        # 1. Apply FastFlags and CEF configuration
        self.log("Applying FastFlags and Web/CEF overrides...")
        written = self.flag_manager.apply_flags(user_fastflags, cef_mode=cef_mode)
        for w in written:
            self.log(f" -> Synchronized flags to {w}")

        # 2. Check if Vinegar CLI is available as preferred launcher
        vinegar_bin = shutil.which("vinegar")
        studio_exe = self.find_studio_executable(prefix_path)

        # Build full environment
        run_env = self.wine_runner.build_env(prefix_path, runner_path, env_vars)

        # DLL overrides for renderer
        dll_overrides = self.build_dll_overrides(renderer)
        if dll_overrides:
            existing_overrides = run_env.get("WINEDLLOVERRIDES", "")
            run_env["WINEDLLOVERRIDES"] = f"{dll_overrides};{existing_overrides}".strip(";")

        # Set CEF helper sandbox environment if needed
        if cef_mode == "disabled":
            run_env["WINE_CEF_DISABLE"] = "1"
        elif cef_mode == "software":
            run_env["WINE_CEF_ARGS"] = "--disable-gpu"

        # Apply Debug mode environment
        if debug_logs:
            run_env["WINEDEBUG"] = "warn+all,fixme-all"
            run_env["ROBLOX_LOG_LEVEL"] = "debug"
        else:
            run_env.setdefault("WINEDEBUG", "-all")

        # Apply Deployment Version & Update Channel Overrides
        if override_version:
            run_env["VINEGAR_STUDIO_VERSION"] = override_version
            run_env["ROBLOX_VERSION"] = override_version
        if override_channel:
            run_env["VINEGAR_STUDIO_CHANNEL"] = override_channel
            run_env["ROBLOX_CHANNEL"] = override_channel

        # Construct command
        binaries = self.wine_runner.get_binaries(runner_path)
        wine_bin = binaries["wine"]

        cmd: List[str] = []

        # GameMode wrapping
        if use_gamemode and shutil.which("gamemoderun"):
            self.log("Wrapping execution with Feral GameMode (gamemoderun)...")
            cmd.append("gamemoderun")

        # Gamescope wrapping
        if use_gamescope and shutil.which("gamescope"):
            self.log(f"Wrapping in Gamescope ({gamescope_args})...")
            cmd.append("gamescope")
            if gamescope_args:
                cmd.extend(gamescope_args.split())
            cmd.append("--")

        if studio_exe and wine_bin:
            cmd.extend([str(wine_bin), str(studio_exe)])
        elif vinegar_bin:
            self.log("Launching via Vinegar bootstrapper command...")
            cmd.extend([vinegar_bin, "studio"])
        else:
            self.log("❌ Error: Could not locate RobloxStudioBeta.exe or vinegar binary!")
            return False

        self.log(f"Command: {' '.join(cmd)}")

        # Initialize Discord RPC if requested
        if discord_rpc:
            try:
                self.discord_rpc = DiscordRPCManager()
                self.discord_rpc.start()
                self.log("📡 Connected to Discord Rich Presence pipeline.")
            except Exception as e:
                self.log(f"⚠️ Failed to initialize Discord RPC: {e}")
                self.discord_rpc = None
        else:
            self.discord_rpc = None

        def _runner():
            try:
                proc = subprocess.Popen(
                    cmd,
                    env=run_env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                self.active_process = proc
                self.log(f"✅ Process started (PID: {proc.pid})")
                self.process_started.emit(proc.pid)

                # Stream stdout and update Discord RPC in real-time
                if proc.stdout:
                    for line in iter(proc.stdout.readline, ""):
                        if line:
                            clean_line = line.rstrip()
                            self.log(clean_line)
                            if self.discord_rpc:
                                self.discord_rpc.handle_log_line(clean_line)
                    proc.stdout.close()

                ret = proc.wait()
                self.log(f"⏹️ Roblox Studio exited with code {ret}")
                self.process_exited.emit(ret)
                if on_exit:
                    try:
                        on_exit(ret)
                    except Exception:
                        pass
            except Exception as e:
                self.log(f"❌ Execution error: {e}")
                self.process_exited.emit(-1)
                if on_exit:
                    try:
                        on_exit(-1)
                    except Exception:
                        pass
            finally:
                if self.discord_rpc:
                    self.discord_rpc.stop()
                    self.discord_rpc = None
                self.active_process = None

        thread = threading.Thread(target=_runner, daemon=True)
        thread.start()
        return True

    def terminate(self) -> None:
        """Kills active studio process if running and shuts down Discord RPC."""
        if self.discord_rpc:
            try:
                self.discord_rpc.stop()
            except Exception:
                pass
            self.discord_rpc = None

        if self.active_process and self.active_process.poll() is None:
            self.log("⚠️ Terminating active Roblox Studio process...")
            try:
                self.active_process.terminate()
                self.active_process.wait(timeout=1.5)
            except Exception:
                try:
                    self.active_process.kill()
                except Exception:
                    pass

        self.active_process = None
        self.process_exited.emit(0)
