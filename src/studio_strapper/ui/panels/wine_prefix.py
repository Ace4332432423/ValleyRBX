"""
Wine & Prefix Management Panel for Studio Strapper.
Handles prefix selection, creating, cloning, browsing, and launching prefix configuration tools.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from studio_strapper.core.config import ConfigManager
from studio_strapper.core.prefix_manager import PrefixManager
from studio_strapper.core.wine_runner import WineRunner
from studio_strapper.ui.widgets.card import Card
from studio_strapper.ui.widgets.status_badge import StatusBadge


class WinePrefixPanel(QWidget):
    """Panel dedicated to Wine prefix selection, editing, and tool execution."""

    prefix_updated = Signal(str)

    def __init__(self, config_mgr: ConfigManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config_mgr = config_mgr
        self.prefix_mgr = PrefixManager()
        self.wine_runner = WineRunner()
        self._init_ui()
        self.refresh_prefix_info()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # 1. Choose Wine Prefix Card
        choose_card = Card("Choose Wine Prefix", "Select an existing Wine prefix or point to a custom directory")
        choose_layout = QHBoxLayout()

        self.prefix_combo = QComboBox()
        self.prefix_combo.setMinimumWidth(360)
        for p in self.config_mgr.get("known_prefixes", []):
            self.prefix_combo.addItem(p)
        self.prefix_combo.setCurrentText(self.config_mgr.get("active_prefix", ""))
        self.prefix_combo.currentTextChanged.connect(self._on_prefix_selected)
        choose_layout.addWidget(self.prefix_combo)

        browse_btn = QPushButton("📁 Browse Path...")
        browse_btn.clicked.connect(self._browse_custom_prefix)
        choose_layout.addWidget(browse_btn)

        new_prefix_btn = QPushButton("➕ Create New...")
        new_prefix_btn.clicked.connect(self._create_new_prefix)
        choose_layout.addWidget(new_prefix_btn)

        choose_layout.addStretch()
        choose_card.add_layout(choose_layout)
        layout.addWidget(choose_card)

        # 2. Prefix Inspection Info Card
        self.info_card = Card("Active Prefix Inspection", "Hardware and filesystem details for current prefix")
        info_grid = QGridLayout()
        info_grid.setSpacing(10)

        info_grid.addWidget(QLabel("Full Path:"), 0, 0)
        self.lbl_path = QLabel()
        self.lbl_path.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        info_grid.addWidget(self.lbl_path, 0, 1)

        info_grid.addWidget(QLabel("Status:"), 1, 0)
        self.badge_status = StatusBadge("Checking...", "info")
        info_grid.addWidget(self.badge_status, 1, 1)

        info_grid.addWidget(QLabel("Disk Usage:"), 2, 0)
        self.lbl_size = QLabel()
        info_grid.addWidget(self.lbl_size, 2, 1)

        info_grid.addWidget(QLabel("Last Modified:"), 3, 0)
        self.lbl_modified = QLabel()
        info_grid.addWidget(self.lbl_modified, 3, 1)

        self.info_card.add_layout(info_grid)
        layout.addWidget(self.info_card)

        # 3. Edit Wine Prefix Card (Tools)
        tools_card = Card("Edit Wine Prefix", "Execute native Wine maintenance and configuration utilities")
        tools_grid = QGridLayout()
        tools_grid.setSpacing(12)

        # Edit Prefix Button (winecfg)
        self.btn_winecfg = QPushButton("🍷  Edit Prefix (winecfg)")
        self.btn_winecfg.setToolTip("Open Wine Configuration dialog to edit Windows version, DLL overrides, graphics, and audio")
        self.btn_winecfg.setMinimumHeight(40)
        self.btn_winecfg.clicked.connect(lambda: self._run_wine_tool("winecfg"))
        tools_grid.addWidget(self.btn_winecfg, 0, 0)

        # Registry Editor
        self.btn_regedit = QPushButton("📝  Registry Editor (regedit)")
        self.btn_regedit.setToolTip("Open Wine Registry Editor for this prefix")
        self.btn_regedit.setMinimumHeight(40)
        self.btn_regedit.clicked.connect(lambda: self._run_wine_tool("regedit"))
        tools_grid.addWidget(self.btn_regedit, 0, 1)

        # Winetricks
        self.btn_winetricks = QPushButton("🛠️  Winetricks")
        self.btn_winetricks.setToolTip("Install Windows libraries, fonts, and runtime components")
        self.btn_winetricks.setMinimumHeight(40)
        self.btn_winetricks.clicked.connect(lambda: self._run_wine_tool("winetricks"))
        tools_grid.addWidget(self.btn_winetricks, 0, 2)

        # Open in File Manager
        self.btn_open_folder = QPushButton("📂  Browse drive_c Folder")
        self.btn_open_folder.setToolTip("Open this prefix's drive_c directory in the system file manager")
        self.btn_open_folder.setMinimumHeight(40)
        self.btn_open_folder.clicked.connect(self._open_in_file_manager)
        tools_grid.addWidget(self.btn_open_folder, 1, 0)

        # Clone Prefix
        self.btn_clone = QPushButton("📋  Clone Prefix (btrfs reflink)")
        self.btn_clone.setToolTip("Clone this prefix instantly using copy-on-write")
        self.btn_clone.setMinimumHeight(40)
        self.btn_clone.clicked.connect(self._clone_prefix)
        tools_grid.addWidget(self.btn_clone, 1, 1)

        # Kill Wineserver
        self.btn_kill = QPushButton("⚠️  Kill Wineserver")
        self.btn_kill.setObjectName("dangerButton")
        self.btn_kill.setToolTip("Terminate any active or stuck wineserver processes for this prefix")
        self.btn_kill.setMinimumHeight(40)
        self.btn_kill.clicked.connect(self._kill_wineserver)
        tools_grid.addWidget(self.btn_kill, 1, 2)

        tools_card.add_layout(tools_grid)
        layout.addWidget(tools_card)

        # 4. Vinegar Runner Info Card
        runner_card = Card("Vinegar Wine Runner Integration", "Patched Kombucha runner providing CEF & input handling")
        runner_layout = QHBoxLayout()

        discovered_runners = self.wine_runner.discover_runners()
        self.runner_combo = QComboBox()
        for label, r_type, path in discovered_runners:
            self.runner_combo.addItem(f"{label} [{path}]", str(path))

        cur_runner = self.config_mgr.get("runner_path")
        for i in range(self.runner_combo.count()):
            if self.runner_combo.itemData(i) == cur_runner:
                self.runner_combo.setCurrentIndex(i)
                break

        self.runner_combo.currentIndexChanged.connect(self._on_runner_changed)
        runner_layout.addWidget(QLabel("Active Runner:"))
        runner_layout.addWidget(self.runner_combo)
        runner_layout.addStretch()

        runner_card.add_layout(runner_layout)
        layout.addWidget(runner_card)

        layout.addStretch()

    def refresh_prefix_info(self) -> None:
        active = Path(self.config_mgr.get("active_prefix", ""))
        info = self.prefix_mgr.get_prefix_info(active)

        self.lbl_path.setText(info["path"])
        self.lbl_size.setText(info["size"])
        self.lbl_modified.setText(info["modified"])

        if info["is_valid"] == "True":
            self.badge_status.set_status("ok", "Valid 64-bit Wine Prefix (drive_c present)")
        elif info["exists"] == "True":
            self.badge_status.set_status("warning", "Directory exists but missing drive_c")
        else:
            self.badge_status.set_status("error", "Directory does not exist")

    def _on_prefix_selected(self, path_str: str) -> None:
        if path_str:
            self.config_mgr.set("active_prefix", path_str)
            self.refresh_prefix_info()
            self.prefix_updated.emit(path_str)

    def _browse_custom_prefix(self) -> None:
        chosen = QFileDialog.getExistingDirectory(self, "Select Wine Prefix Directory", str(Path.home()))
        if chosen:
            known = self.config_mgr.get("known_prefixes", [])
            if chosen not in known:
                known.append(chosen)
                self.config_mgr.set("known_prefixes", known)
                self.prefix_combo.addItem(chosen)
            self.prefix_combo.setCurrentText(chosen)

    def _create_new_prefix(self) -> None:
        name, ok = QInputDialog.getText(self, "Create Wine Prefix", "Enter prefix name:")
        if ok and name.strip():
            new_path = self.prefix_mgr.base_dir / name.strip()
            new_path.mkdir(parents=True, exist_ok=True)
            chosen = str(new_path)
            known = self.config_mgr.get("known_prefixes", [])
            known.append(chosen)
            self.config_mgr.set("known_prefixes", known)
            self.prefix_combo.addItem(chosen)
            self.prefix_combo.setCurrentText(chosen)
            # Run wineboot --init
            self._run_wine_tool("wineboot")

    def _clone_prefix(self) -> None:
        active = Path(self.config_mgr.get("active_prefix", ""))
        name, ok = QInputDialog.getText(self, "Clone Prefix", "Enter name for cloned prefix:", text=f"{active.name}-copy")
        if ok and name.strip():
            try:
                dest = self.prefix_mgr.clone_prefix(active, name.strip())
                chosen = str(dest)
                known = self.config_mgr.get("known_prefixes", [])
                known.append(chosen)
                self.config_mgr.set("known_prefixes", known)
                self.prefix_combo.addItem(chosen)
                self.prefix_combo.setCurrentText(chosen)
                QMessageBox.information(self, "Success", f"Prefix successfully cloned to:\n{dest}")
            except Exception as e:
                QMessageBox.critical(self, "Clone Error", f"Failed to clone prefix:\n{e}")

    def _open_in_file_manager(self) -> None:
        active = Path(self.config_mgr.get("active_prefix", ""))
        self.prefix_mgr.open_in_file_manager(active)

    def _run_wine_tool(self, tool_name: str) -> None:
        active = Path(self.config_mgr.get("active_prefix", ""))
        runner = Path(self.config_mgr.get("runner_path", ""))
        self.wine_runner.run_tool(tool_name, active, runner, self.config_mgr.get("env_vars", {}))

    def _kill_wineserver(self) -> None:
        active = Path(self.config_mgr.get("active_prefix", ""))
        runner = Path(self.config_mgr.get("runner_path", ""))
        ok = self.wine_runner.kill_wineserver(active, runner)
        if ok:
            QMessageBox.information(self, "Wineserver", "Wineserver process terminated.")
        else:
            QMessageBox.warning(self, "Wineserver", "Failed to terminate wineserver or no process was running.")

    def _on_runner_changed(self, idx: int) -> None:
        runner_path = self.runner_combo.itemData(idx)
        if runner_path:
            self.config_mgr.set("runner_path", runner_path)
