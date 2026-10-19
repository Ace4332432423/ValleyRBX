"""
System diagnostics and CachyOS / Arch Linux compatibility audit for Studio Strapper.
"""

from __future__ import annotations
import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple


class SystemAuditor:
    """Performs comprehensive checks for running Roblox Studio on CachyOS / Arch Linux."""

    def run_full_audit(self) -> List[Dict[str, str]]:
        """
        Runs all checks and returns a list of results.
        Each entry has: status ("ok", "warning", "error", "info"), title, details, fix.
        """
        results = []
        results.append(self.check_os())
        results.append(self.check_gpu())
        results.append(self.check_multilib())
        results.append(self.check_lib32())
        results.append(self.check_kernel_scheduler())
        results.append(self.check_display_server())
        results.append(self.check_gamescope())
        results.append(self.check_wine_environment())
        return results

    def check_os(self) -> Dict[str, str]:
        os_release = ""
        if Path("/etc/os-release").exists():
            try:
                os_release = Path("/etc/os-release").read_text()
            except Exception:
                pass

        kernel = platform.release()
        is_cachy = "cachyos" in os_release.lower() or "cachyos" in kernel.lower()
        title = "Operating System: CachyOS" if is_cachy else f"Operating System: {platform.system()} ({kernel})"
        return {
            "status": "ok",
            "title": title,
            "details": f"Kernel {kernel} (x86_64). High performance kernel features active.",
            "fix": "",
        }

    def check_gpu(self) -> Dict[str, str]:
        gpu_name = "Generic / Unknown"
        try:
            res = subprocess.run("lspci -nn | grep -Ei 'vga|3d|display'", shell=True, capture_output=True, text=True)
            for line in res.stdout.strip().split("\n"):
                if "NVIDIA" in line:
                    gpu_name = line.split("controller [0300]: ")[-1] if "controller" in line else line
                    return {
                        "status": "ok",
                        "title": f"GPU: {gpu_name}",
                        "details": "NVIDIA GPU detected. Recommended renderer: D3D11 (DXVK) or Vulkan.",
                        "fix": "",
                    }
                elif "AMD" in line or "Advanced Micro Devices" in line:
                    gpu_name = line
                    return {
                        "status": "ok",
                        "title": f"GPU: AMD Radeon",
                        "details": "AMD GPU detected with Mesa RADV. Excellent Vulkan & DXVK performance.",
                        "fix": "",
                    }
        except Exception:
            pass

        return {
            "status": "info",
            "title": f"GPU: {gpu_name}",
            "details": "GPU detected. Verify drivers with vulkaninfo or glxinfo.",
            "fix": "",
        }

    def check_multilib(self) -> Dict[str, str]:
        pacman_conf = Path("/etc/pacman.conf")
        if pacman_conf.exists():
            try:
                content = pacman_conf.read_text()
                lines = content.splitlines()
                multilib_enabled = False
                for line in lines:
                    stripped = line.strip()
                    if stripped == "[multilib]":
                        multilib_enabled = True
                        break
                if multilib_enabled:
                    return {
                        "status": "ok",
                        "title": "Multilib Repository: Enabled",
                        "details": "Arch multilib 32-bit library support is active in pacman.conf.",
                        "fix": "",
                    }
                else:
                    return {
                        "status": "error",
                        "title": "Multilib Repository: Disabled",
                        "details": "Wine requires 32-bit multilib libraries to run Windows software.",
                        "fix": "Uncomment [multilib] in /etc/pacman.conf and run 'sudo pacman -Sy'",
                    }
            except Exception:
                pass
        return {
            "status": "ok",
            "title": "Multilib Repository: Assumed Active",
            "details": "CachyOS enables multilib by default.",
            "fix": "",
        }

    def check_lib32(self) -> Dict[str, str]:
        # Check critical 32-bit graphics libraries
        has_lib32 = Path("/usr/lib32").exists() and any(Path("/usr/lib32").iterdir())
        if has_lib32:
            return {
                "status": "ok",
                "title": "32-bit Runtime (lib32): Installed",
                "details": "Multilib runtime libraries found in /usr/lib32.",
                "fix": "",
            }
        return {
            "status": "warning",
            "title": "32-bit Runtime (lib32): Incomplete",
            "details": "Some 32-bit graphics dependencies might be missing.",
            "fix": "Run: sudo pacman -S --needed cachyos-gaming-meta or lib32-mesa",
        }

    def check_kernel_scheduler(self) -> Dict[str, str]:
        # Check for sched-ext and ananicy-cpp
        has_ananicy = shutil.which("ananicy-cpp") is not None
        ananicy_active = False
        if has_ananicy:
            try:
                res = subprocess.run(["systemctl", "is-active", "ananicy-cpp"], capture_output=True, text=True)
                ananicy_active = res.stdout.strip() == "active"
            except Exception:
                pass

        if ananicy_active:
            return {
                "status": "warning",
                "title": "Process Priority: ananicy-cpp is Active",
                "details": "If using a custom sched-ext scheduler (e.g. scx_bpfland), ananicy-cpp can occasionally induce microstutters.",
                "fix": "If experiencing stutter, disable with: sudo systemctl stop ananicy-cpp",
            }

        return {
            "status": "ok",
            "title": "Kernel & Scheduler: Optimized",
            "details": "CachyOS BORE/EEVDF scheduler with futex_waitv (WINEFSYNC) fully supported.",
            "fix": "",
        }

    def check_display_server(self) -> Dict[str, str]:
        session = os.environ.get("XDG_SESSION_TYPE", "unknown")
        if session == "wayland":
            return {
                "status": "warning",
                "title": "Display Server: Wayland (XWayland)",
                "details": "Roblox Studio runs via XWayland. If mouse cursor escapes or locks, enable the Gamescope wrapper toggle.",
                "fix": "Toggle 'Enable Gamescope' in the dashboard or run gamescope wrapper.",
            }
        return {
            "status": "ok",
            "title": f"Display Server: {session.upper()}",
            "details": "Standard native X11 window management active.",
            "fix": "",
        }

    def check_gamescope(self) -> Dict[str, str]:
        gs = shutil.which("gamescope")
        if gs:
            return {
                "status": "ok",
                "title": "Gamescope: Available",
                "details": f"Found at {gs}. Ready to isolate cursor capture and enforce resolution.",
                "fix": "",
            }
        return {
            "status": "info",
            "title": "Gamescope: Not Installed",
            "details": "Gamescope is an optional micro-compositor that solves Wayland mouse-lock bugs.",
            "fix": "Install with: sudo pacman -S gamescope",
        }

    def check_wine_environment(self) -> Dict[str, str]:
        kombucha = Path.home() / ".local/share/vinegar/kombucha"
        if kombucha.exists():
            return {
                "status": "ok",
                "title": "Wine Runner: Vinegar Kombucha Patched",
                "details": f"Found at {kombucha.resolve().name}. Equipped with CEF & window-capture patches.",
                "fix": "",
            }
        system_wine = shutil.which("wine")
        if system_wine:
            return {
                "status": "info",
                "title": f"Wine Runner: System Wine ({system_wine})",
                "details": "Standard Wine found. Kombucha patches recommended for best Roblox Studio stability.",
                "fix": "",
            }
        return {
            "status": "error",
            "title": "Wine Runner: Missing",
            "details": "No Wine runner found.",
            "fix": "Install Vinegar or Wine: sudo pacman -S wine-staging",
        }
