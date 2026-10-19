"""
FastFlags (ClientAppSettings.json) Engine for Studio Strapper.
Handles Roblox's official FastFlag allowlist, curated presets, and CEF toggle flags.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ALLOWLISTED_FLAGS = [
    {
        "name": "DFFlagDisableDPIScale",
        "type": "bool",
        "default": True,
        "description": "Disable DPI scaling to fix window misalignments and blurred UI on Linux/Wayland.",
        "category": "Display",
    },
    {
        "name": "FFlagHandleAltEnterFullscreenManually",
        "type": "bool",
        "default": True,
        "description": "Prevent Wine window focus lockups when toggling fullscreen via Alt+Enter.",
        "category": "Display",
    },
    {
        "name": "DFIntCSGLevelOfDetailSwitchingDistance",
        "type": "int",
        "default": 200,
        "description": "CSG / Union rendering distance. Lower values drastically improve viewport FPS.",
        "category": "Performance",
    },
    {
        "name": "FIntFRMMaxGrassDistance",
        "type": "int",
        "default": 0,
        "description": "Maximum grass rendering distance. Set to 0 to disable grass rendering.",
        "category": "Performance",
    },
    {
        "name": "DFFlagTextureQualityOverrideEnabled",
        "type": "bool",
        "default": True,
        "description": "Enables manual texture quality level override.",
        "category": "Graphics",
    },
    {
        "name": "DFIntTextureQualityOverride",
        "type": "int",
        "default": 2,
        "description": "Manual texture quality level (1 = lowest/fastest, 3 = highest fidelity).",
        "category": "Graphics",
    },
    {
        "name": "FIntDebugForceMSAASamples",
        "type": "int",
        "default": 0,
        "description": "Force MSAA anti-aliasing sample count (0 = off, 2 = 2x, 4 = 4x).",
        "category": "Graphics",
    },
    {
        "name": "DFIntDebugFRMQualityLevelOverride",
        "type": "int",
        "default": 0,
        "description": "Force studio viewport render quality level (0 = auto, 1-21 manual).",
        "category": "Graphics",
    },
    {
        "name": "FFlagDebugSkyGray",
        "type": "bool",
        "default": False,
        "description": "Render a neutral gray skybox for lighting debugging and lower GPU overhead.",
        "category": "Debug",
    },
    {
        "name": "DFFlagDebugPauseVoxelizer",
        "type": "bool",
        "default": False,
        "description": "Pauses voxel light updates to save CPU cycles.",
        "category": "Debug",
    },
]

PRESETS: Dict[str, Dict[str, Any]] = {
    "Performance": {
        "DFFlagDisableDPIScale": True,
        "FFlagHandleAltEnterFullscreenManually": True,
        "DFIntCSGLevelOfDetailSwitchingDistance": 150,
        "FIntFRMMaxGrassDistance": 0,
        "DFFlagTextureQualityOverrideEnabled": True,
        "DFIntTextureQualityOverride": 1,
        "FIntDebugForceMSAASamples": 0,
    },
    "High Quality": {
        "DFFlagDisableDPIScale": True,
        "FFlagHandleAltEnterFullscreenManually": True,
        "DFIntCSGLevelOfDetailSwitchingDistance": 800,
        "FIntFRMMaxGrassDistance": 1500,
        "DFFlagTextureQualityOverrideEnabled": True,
        "DFIntTextureQualityOverride": 3,
        "FIntDebugForceMSAASamples": 4,
        "DFIntDebugFRMQualityLevelOverride": 21,
    },
    "Stability": {
        "DFFlagDisableDPIScale": True,
        "FFlagHandleAltEnterFullscreenManually": True,
    },
}


class FastFlagManager:
    """Manages reading, merging, and writing ClientAppSettings.json across Vinegar overlay and Studio versions."""

    def __init__(self) -> None:
        self.overlay_path = Path.home() / ".config/vinegar/overlay/studio/ClientSettings/ClientAppSettings.json"

    def get_cef_flags(self, cef_mode: str) -> Dict[str, Any]:
        """Returns FastFlags corresponding to the selected CEF (web pages) mode."""
        flags: Dict[str, Any] = {}
        if cef_mode == "disabled":
            flags["FFlagStudioBrowserEnabled"] = False
            flags["FFlagStudioDisableCEF"] = True
            flags["FFlagDebugDisableCef"] = True
            flags["DFFlagDisableCEFWindowCapture"] = True
        elif cef_mode == "software":
            flags["FFlagStudioCEFGPUDisabled"] = True
            flags["FFlagDebugDisableCefGPU"] = True
        elif cef_mode == "external":
            flags["FFlagStudioBrowserEnabled"] = False
            flags["FFlagStudioUseSystemWebBrowser"] = True
        return flags

    def apply_flags(
        self,
        user_flags: Dict[str, Any],
        cef_mode: str = "disabled",
        extra_locations: Optional[List[Path]] = None,
    ) -> List[Path]:
        """
        Merges flags and writes them to:
        1. Vinegar overlay: ~/.config/vinegar/overlay/studio/ClientSettings/ClientAppSettings.json
        2. Installed Studio versions in ~/.local/share/vinegar/versions/*/ClientSettings/
        3. Any extra locations specified.
        """
        cef_flags = self.get_cef_flags(cef_mode)
        combined: Dict[str, Any] = {}
        combined.update(user_flags)
        combined.update(cef_flags)

        written_paths = []

        # 1. Vinegar overlay
        try:
            self.overlay_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.overlay_path, "w", encoding="utf-8") as f:
                json.dump(combined, f, indent=4)
            written_paths.append(self.overlay_path)
        except Exception as e:
            print(f"[FastFlags] Failed to write to overlay: {e}")

        # 2. Studio versions in ~/.local/share/vinegar/versions/
        versions_dir = Path.home() / ".local/share/vinegar/versions"
        if versions_dir.exists():
            for v_dir in versions_dir.iterdir():
                if v_dir.is_dir() and (v_dir / "RobloxStudioBeta.exe").exists():
                    target = v_dir / "ClientSettings" / "ClientAppSettings.json"
                    try:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with open(target, "w", encoding="utf-8") as f:
                            json.dump(combined, f, indent=4)
                        written_paths.append(target)
                    except Exception as e:
                        print(f"[FastFlags] Failed to write to version dir: {e}")

        # 3. Extra locations
        if extra_locations:
            for loc in extra_locations:
                try:
                    loc.parent.mkdir(parents=True, exist_ok=True)
                    with open(loc, "w", encoding="utf-8") as f:
                        json.dump(combined, f, indent=4)
                    written_paths.append(loc)
                except Exception as e:
                    print(f"[FastFlags] Failed to write to extra loc {loc}: {e}")

        return written_paths
