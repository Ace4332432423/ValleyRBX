"""
Configuration management for Studio Strapper.
Handles persisting settings, syncing with Vinegar's config.toml, and managing presets.
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any, Dict, List

CONFIG_DIR = Path.home() / ".config" / "studio-strapper"
CONFIG_FILE = CONFIG_DIR / "config.json"
VINEGAR_CONFIG_FILE = Path.home() / ".config" / "vinegar" / "config.toml"
DEFAULT_PREFIX = Path.home() / ".local/share/vinegar/prefixes/studio"
DEFAULT_KOMBUCHA = Path.home() / ".local/share/vinegar/kombucha"

DEFAULT_CONFIG: Dict[str, Any] = {
    "active_prefix": str(DEFAULT_PREFIX),
    "known_prefixes": [str(DEFAULT_PREFIX)],
    "runner_path": str(DEFAULT_KOMBUCHA),
    "renderer": "Vulkan",  # "D3D11 (DXVK)", "Vulkan", "OpenGL", "D3D12 (VKD3D)"
    "cef_mode": "disabled",  # "standard", "software", "disabled", "external"
    "use_gamescope": False,
    "gamescope_args": "-W 1920 -H 1080 -f --force-grab-cursor",
    "env_vars": {
        "WINEFSYNC": "1",
        "DXVK_ASYNC": "1",
        "WINE_LARGE_ADDRESS_AWARE": "1",
        "__GL_THREADED_OPTIMIZATION": "1",
        "DXVK_HUD": "0",
    },
    "fastflags": {
        "DFFlagDisableDPIScale": True,
        "FFlagHandleAltEnterFullscreenManually": True,
        "DFIntCSGLevelOfDetailSwitchingDistance": 200,
        "FIntFRMMaxGrassDistance": 0,
        "DFFlagTextureQualityOverrideEnabled": True,
        "DFIntTextureQualityOverride": 2,
    },
    "theme": "catppuccin-mocha",
    "discord_rpc": True,
    "use_gamemode": True,
    "debug_logs": False,
    "override_version": "",
    "override_channel": "",
}


class ConfigManager:
    """Manages application state and configuration file."""

    def __init__(self, config_path: Path = CONFIG_FILE) -> None:
        self.config_path = config_path
        self.config_dir = config_path.parent
        self.data: Dict[str, Any] = dict(DEFAULT_CONFIG)
        self.load()

    def load(self) -> None:
        """Load configuration from disk, falling back to defaults and importing Vinegar config if present."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
            except Exception as e:
                print(f"[Config] Error loading {self.config_path}: {e}")

        # Check for existing Vinegar settings to import
        self.import_from_vinegar()

        # Ensure active_prefix exists in known_prefixes
        active = self.data.get("active_prefix")
        if active and active not in self.data["known_prefixes"]:
            self.data["known_prefixes"].append(active)

    def save(self) -> None:
        """Save configuration to disk."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
            self.sync_to_vinegar()
        except Exception as e:
            print(f"[Config] Error saving config: {e}")

    def import_from_vinegar(self) -> None:
        """Import settings from Vinegar's config.toml if it exists."""
        if not VINEGAR_CONFIG_FILE.exists():
            return
        try:
            import tomllib
            with open(VINEGAR_CONFIG_FILE, "rb") as f:
                vinegar_data = tomllib.load(f)
            studio_sec = vinegar_data.get("studio", {})
            if "renderer" in studio_sec:
                self.data["renderer"] = studio_sec["renderer"]
            if "discord_rpc" in studio_sec:
                self.data["discord_rpc"] = bool(studio_sec["discord_rpc"])
            if "wineroot" in studio_sec:
                self.data["runner_path"] = studio_sec["wineroot"]
            if "env" in studio_sec and isinstance(studio_sec["env"], dict):
                self.data["env_vars"].update(studio_sec["env"])
        except Exception as e:
            print(f"[Config] Note: Could not import vinegar config: {e}")

    def sync_to_vinegar(self) -> None:
        """Sync relevant settings back to ~/.config/vinegar/config.toml for compatibility."""
        try:
            VINEGAR_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            lines = ["[studio]\n"]
            lines.append(f'renderer = "{self.data.get("renderer", "Vulkan")}"\n')
            lines.append(f'discord_rpc = {str(self.data.get("discord_rpc", False)).lower()}\n')
            if self.data.get("runner_path"):
                lines.append(f'wineroot = "{self.data["runner_path"]}"\n')
            lines.append("\n[studio.env]\n")
            for k, v in self.data.get("env_vars", {}).items():
                lines.append(f'{k} = "{v}"\n')

            with open(VINEGAR_CONFIG_FILE, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except Exception as e:
            print(f"[Config] Error syncing to vinegar config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
        self.save()
