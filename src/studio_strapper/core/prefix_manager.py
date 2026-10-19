"""
Wine Prefix Management for Studio Strapper.
Handles listing, creating, validating, cloning, and inspecting Wine prefixes.
"""

from __future__ import annotations
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class PrefixManager:
    """Manages Wine prefix operations and inspections."""

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        self.base_dir = base_dir or Path.home() / ".local/share/studio-strapper/prefixes"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_prefix_info(self, prefix_path: Path) -> Dict[str, str]:
        """Returns metadata regarding a Wine prefix."""
        prefix_path = prefix_path.expanduser().resolve()
        exists = prefix_path.exists()
        drive_c = prefix_path / "drive_c"
        has_drive_c = drive_c.exists()
        is_valid = exists and has_drive_c

        size_str = "0 MB"
        created_str = "Unknown"
        if exists:
            try:
                # Get folder size approximation
                total_bytes = sum(f.stat().st_size for f in prefix_path.glob("**/*") if f.is_file())
                size_str = f"{total_bytes / (1024 * 1024):.1f} MB" if total_bytes < 1024 * 1024 * 1024 else f"{total_bytes / (1024 * 1024 * 1024):.2f} GB"
                stat = prefix_path.stat()
                created_str = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            except Exception:
                size_str = "Calculating..."

        return {
            "path": str(prefix_path),
            "name": prefix_path.name,
            "exists": str(exists),
            "is_valid": str(is_valid),
            "size": size_str,
            "modified": created_str,
            "arch": "win64",
        }

    def open_in_file_manager(self, prefix_path: Path) -> bool:
        """Opens the prefix directory or its drive_c in the desktop file manager."""
        target = prefix_path / "drive_c" if (prefix_path / "drive_c").exists() else prefix_path
        try:
            subprocess.Popen(["xdg-open", str(target)])
            return True
        except Exception as e:
            print(f"[PrefixManager] Failed to open in file manager: {e}")
            return False

    def clone_prefix(self, src: Path, dest_name: str) -> Optional[Path]:
        """
        Clones a prefix into base_dir using --reflink=auto for instant btrfs copy-on-write.
        """
        dest = self.base_dir / dest_name
        if dest.exists():
            raise FileExistsError(f"Target prefix '{dest_name}' already exists at {dest}")

        cmd = ["cp", "-a", "--reflink=auto", str(src), str(dest)]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Failed to clone prefix: {res.stderr}")
        return dest

    def delete_prefix(self, prefix_path: Path) -> bool:
        """Safely removes a prefix directory."""
        if not prefix_path.exists():
            return False
        shutil.rmtree(prefix_path)
        return True
