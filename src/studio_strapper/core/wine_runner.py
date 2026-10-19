"""
Wine Runner Integration for Studio Strapper.
Handles discovering and running Vinegar's custom Kombucha Wine build,
managing wineserver, and launching prefix maintenance tools (winecfg, regedit, winetricks).
"""

from __future__ import annotations
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class WineRunner:
    """Manages Wine runner discovery, prefix tools execution, and process lifecycle."""

    def __init__(self, custom_runner_path: Optional[str] = None) -> None:
        self.custom_runner_path = Path(custom_runner_path) if custom_runner_path else None

    def discover_runners(self) -> List[Tuple[str, str, Path]]:
        """
        Discovers all available Wine runners.
        Returns a list of (label, runner_type, base_path).
        """
        runners = []

        # 1. Custom runner if specified
        if self.custom_runner_path and self.custom_runner_path.exists():
            runners.append(("Custom Path", "custom", self.custom_runner_path))

        # 2. Vinegar's native Kombucha runner
        vinegar_kombucha = Path.home() / ".local/share/vinegar/kombucha"
        if vinegar_kombucha.exists():
            resolved = vinegar_kombucha.resolve()
            version_name = resolved.name
            runners.append((f"Vinegar Kombucha ({version_name})", "kombucha", resolved))

        # Check for multiple kombucha versions in ~/.local/share/vinegar/
        vinegar_share = Path.home() / ".local/share/vinegar"
        if vinegar_share.exists():
            for p in vinegar_share.iterdir():
                if p.is_dir() and p.name.startswith("kombucha-") and p != vinegar_kombucha.resolve():
                    runners.append((f"Kombucha Archive ({p.name})", "kombucha", p))

        # 3. Flatpak Vinegar Kombucha runner
        flatpak_kombucha = Path.home() / ".var/app/org.vinegarhq.Vinegar/data/vinegar/kombucha"
        if flatpak_kombucha.exists():
            runners.append(("Flatpak Vinegar Kombucha", "flatpak-kombucha", flatpak_kombucha.resolve()))

        # 4. System Wine
        system_wine = shutil.which("wine")
        if system_wine:
            system_bin_dir = Path(system_wine).parent
            runners.append(("System Wine (/usr/bin/wine)", "system", system_bin_dir.parent))

        return runners

    def get_active_runner_path(self, preferred_path: Optional[str] = None) -> Path:
        """Determines the active runner directory based on preference or best available."""
        if preferred_path:
            p = Path(preferred_path)
            if p.exists():
                return p.resolve()

        discovered = self.discover_runners()
        if discovered:
            return discovered[0][2]

        # Fallback to system /usr
        return Path("/usr")

    def get_binaries(self, runner_root: Path) -> Dict[str, Optional[Path]]:
        """Resolves wine and wineserver executables from the runner directory."""
        bin_dir = runner_root / "bin"
        if not bin_dir.exists():
            bin_dir = runner_root

        wine_bin = bin_dir / "wine"
        wineserver_bin = bin_dir / "wineserver"
        winecfg_bin = bin_dir / "winecfg"
        regedit_bin = bin_dir / "regedit"

        return {
            "wine": wine_bin if wine_bin.exists() else Path(shutil.which("wine") or "wine"),
            "wineserver": wineserver_bin if wineserver_bin.exists() else Path(shutil.which("wineserver") or "wineserver"),
            "winecfg": winecfg_bin if winecfg_bin.exists() else None,
            "regedit": regedit_bin if regedit_bin.exists() else None,
            "winetricks": Path(shutil.which("winetricks") or "/usr/bin/winetricks"),
        }

    def build_env(self, prefix: Path, runner_root: Path, extra_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Constructs the complete process environment for executing wine commands."""
        env = dict(os.environ)
        env["WINEPREFIX"] = str(prefix)
        env["WINEARCH"] = "win64"

        # Prepend runner bin and lib to PATH and LD_LIBRARY_PATH
        runner_bin = str(runner_root / "bin")
        runner_lib = str(runner_root / "lib")
        runner_lib64 = str(runner_root / "lib64")

        cur_path = env.get("PATH", "")
        env["PATH"] = f"{runner_bin}:{cur_path}"

        cur_ld = env.get("LD_LIBRARY_PATH", "")
        env["LD_LIBRARY_PATH"] = f"{runner_lib64}:{runner_lib}:{cur_ld}".strip(":")

        if extra_env:
            env.update(extra_env)

        return env

    def run_tool(
        self,
        tool_name: str,
        prefix: Path,
        runner_root: Path,
        extra_env: Optional[Dict[str, str]] = None,
    ) -> subprocess.Popen:
        """Launches a Wine tool (winecfg, regedit, winetricks, wineboot, etc.) asynchronously."""
        binaries = self.get_binaries(runner_root)
        env = self.build_env(prefix, runner_root, extra_env)

        if tool_name == "winecfg":
            cmd = [str(binaries["wine"]), "winecfg"]
        elif tool_name == "regedit":
            cmd = [str(binaries["wine"]), "regedit"]
        elif tool_name == "winetricks":
            cmd = [str(binaries["winetricks"])]
        elif tool_name == "wineboot":
            cmd = [str(binaries["wine"]), "wineboot", "--init"]
        elif tool_name == "kill":
            cmd = [str(binaries["wineserver"]), "-k"]
        else:
            cmd = [str(binaries["wine"]), tool_name]

        print(f"[WineRunner] Launching {tool_name}: {' '.join(cmd)}")
        return subprocess.Popen(cmd, env=env)

    def is_wineserver_running(self, prefix: Path, runner_root: Path) -> bool:
        """Checks if a wineserver is currently running for the target prefix."""
        binaries = self.get_binaries(runner_root)
        env = self.build_env(prefix, runner_root)
        try:
            res = subprocess.run(
                [str(binaries["wineserver"]), "-k=0"],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            # returncode 0 means server is running
            return res.returncode == 0
        except Exception:
            return False

    def kill_wineserver(self, prefix: Path, runner_root: Path) -> bool:
        """Terminates any active wineserver processes in the target prefix."""
        binaries = self.get_binaries(runner_root)
        env = self.build_env(prefix, runner_root)
        try:
            subprocess.run([str(binaries["wineserver"]), "-k"], env=env, check=False)
            return True
        except Exception as e:
            print(f"[WineRunner] Failed to kill wineserver: {e}")
            return False
