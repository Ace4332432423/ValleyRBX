"""
Dashboard Panel for ValleyRBX.
Cinematic hero card with glowing launch button, quick selectors, toggles, and system status badges.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from studio_strapper.core.config import ConfigManager
from studio_strapper.ui.widgets.card import Card
from studio_strapper.ui.widgets.status_badge import StatusBadge
from studio_strapper.ui.widgets.toggle_switch import ToggleSwitch

ICON_PATH = "/home/ace/Downloads/rounded-image.png"


class DashboardPanel(QWidget):
    """Primary overview and launch control panel."""

    launch_requested = Signal()
    stop_requested = Signal()
    navigate_to_tab = Signal(int)

    def __init__(self, config_mgr: ConfigManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config_mgr = config_mgr
        self.is_running = False
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(18)

        # 1. Hero Card: Cinematic Launch Control
        hero_card = Card()
        hero_card.setStyleSheet("""
            .Card {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(28, 22, 60, 0.85), stop:0.5 rgba(17, 21, 46, 0.8), stop:1 rgba(38, 14, 52, 0.85));
                border: 1px solid rgba(168, 85, 247, 0.4);
                border-radius: 20px;
                padding: 24px;
            }
        """)
        hero_layout = QHBoxLayout()
        hero_layout.setSpacing(20)

        # Hero Icon
        if Path(ICON_PATH).exists():
            hero_icon = QLabel()
            pix = QPixmap(ICON_PATH).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            hero_icon.setPixmap(pix)
            hero_layout.addWidget(hero_icon)

        # Status indicator
        status_box = QVBoxLayout()
        status_box.setSpacing(3)

        app_badge = QLabel("VALLEY RBX RUNTIME")
        app_badge.setStyleSheet("color: #c084fc; font-size: 11px; font-weight: 800; letter-spacing: 1.5px;")
        status_box.addWidget(app_badge)

        self.status_title = QLabel("Roblox Studio is Ready")
        self.status_title.setStyleSheet("font-size: 22px; font-weight: 900; color: #ffffff; letter-spacing: 0.5px;")
        
        self.status_desc = QLabel("Wine prefix initialized • Vinegar Kombucha runner primed • FastFlags synchronized")
        self.status_desc.setStyleSheet("color: #cbd5e1; font-size: 12px;")
        
        status_box.addWidget(self.status_title)
        status_box.addWidget(self.status_desc)

        hero_layout.addLayout(status_box)
        hero_layout.addStretch()

        # Big Cinematic Launch Button
        self.launch_btn = QPushButton("⚡  LAUNCH STUDIO")
        self.launch_btn.setObjectName("launchButton")
        self.launch_btn.setMinimumHeight(56)
        self.launch_btn.setMinimumWidth(220)
        self.launch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.launch_btn.clicked.connect(self._on_launch_clicked)
        hero_layout.addWidget(self.launch_btn)

        hero_card.add_layout(hero_layout)
        layout.addWidget(hero_card)

        # 2. Quick Settings Card
        settings_card = Card("Runtime Configuration", "Active execution environment parameters")
        grid = QGridLayout()
        grid.setSpacing(14)

        # Row 0: Prefix & Runner
        grid.addWidget(QLabel("Wine Prefix:"), 0, 0)
        self.prefix_combo = QComboBox()
        for p in self.config_mgr.get("known_prefixes", []):
            self.prefix_combo.addItem(p)
        self.prefix_combo.setCurrentText(self.config_mgr.get("active_prefix", ""))
        self.prefix_combo.currentTextChanged.connect(self._on_prefix_changed)
        grid.addWidget(self.prefix_combo, 0, 1)

        manage_prefix_btn = QPushButton("Manage...")
        manage_prefix_btn.clicked.connect(lambda: self.navigate_to_tab.emit(1))
        grid.addWidget(manage_prefix_btn, 0, 2)

        # Row 1: Renderer
        grid.addWidget(QLabel("Graphics API:"), 1, 0)
        self.renderer_combo = QComboBox()
        self.renderer_combo.addItems(["D3D11 (DXVK)", "Vulkan", "OpenGL", "D3D12 (VKD3D)"])
        self.renderer_combo.setCurrentText(self.config_mgr.get("renderer", "Vulkan"))
        self.renderer_combo.currentTextChanged.connect(self._on_renderer_changed)
        grid.addWidget(self.renderer_combo, 1, 1)

        gfx_settings_btn = QPushButton("Renderer & Env...")
        gfx_settings_btn.clicked.connect(lambda: self.navigate_to_tab.emit(2))
        grid.addWidget(gfx_settings_btn, 1, 2)

        # Row 2: CEF Mode
        grid.addWidget(QLabel("Web Pages / CEF:"), 2, 0)
        self.cef_combo = QComboBox()
        self.cef_combo.addItems([
            "disabled (Recommended — Crash Prevention)",
            "software (CPU Rendered)",
            "standard (Embedded Hardware CEF)",
            "external (System Browser Redirect)",
        ])
        cur_cef = self.config_mgr.get("cef_mode", "disabled")
        for i in range(self.cef_combo.count()):
            if self.cef_combo.itemText(i).startswith(cur_cef):
                self.cef_combo.setCurrentIndex(i)
                break
        self.cef_combo.currentIndexChanged.connect(self._on_cef_changed)
        grid.addWidget(self.cef_combo, 2, 1)

        cef_help_btn = QPushButton("Web Config...")
        cef_help_btn.clicked.connect(lambda: self.navigate_to_tab.emit(3))
        grid.addWidget(cef_help_btn, 2, 2)

        settings_card.add_layout(grid)
        layout.addWidget(settings_card)

        # 3. Quick Toggles Card
        toggles_card = Card("Performance & Precision Toggles", "Hardware-accelerated synchronization and Wayland isolation")
        toggles_layout = QHBoxLayout()
        toggles_layout.setSpacing(28)

        # Fsync
        fsync_box = QHBoxLayout()
        self.fsync_switch = ToggleSwitch(checked=self.config_mgr.get("env_vars", {}).get("WINEFSYNC") == "1")
        self.fsync_switch.toggled.connect(self._toggle_fsync)
        fsync_box.addWidget(self.fsync_switch)
        fsync_box.addWidget(QLabel("WINEFSYNC (futex_waitv)"))
        toggles_layout.addLayout(fsync_box)

        # DXVK Async
        async_box = QHBoxLayout()
        self.async_switch = ToggleSwitch(checked=self.config_mgr.get("env_vars", {}).get("DXVK_ASYNC") == "1")
        self.async_switch.toggled.connect(self._toggle_async)
        async_box.addWidget(self.async_switch)
        async_box.addWidget(QLabel("DXVK Async Pipeline"))
        toggles_layout.addLayout(async_box)

        # Gamescope
        gs_box = QHBoxLayout()
        self.gs_switch = ToggleSwitch(checked=self.config_mgr.get("use_gamescope", False))
        self.gs_switch.toggled.connect(self._toggle_gamescope)
        gs_box.addWidget(self.gs_switch)
        gs_box.addWidget(QLabel("Wayland Gamescope"))
        toggles_layout.addLayout(gs_box)

        toggles_layout.addStretch()
        toggles_card.add_layout(toggles_layout)
        layout.addWidget(toggles_card)

        # 4. System Status Summary Badges
        status_card = Card("Platform Diagnostics", "CachyOS environment & GPU status")
        badge_layout = QHBoxLayout()
        badge_layout.setSpacing(12)

        self.b_os = StatusBadge("CachyOS Kernel", "ok")
        self.b_gpu = StatusBadge("NVIDIA RTX 3060", "ok")
        self.b_runner = StatusBadge("Vinegar Kombucha Patched", "ok")
        self.b_wayland = StatusBadge("Wayland Active", "warning")

        badge_layout.addWidget(self.b_os)
        badge_layout.addWidget(self.b_gpu)
        badge_layout.addWidget(self.b_runner)
        badge_layout.addWidget(self.b_wayland)
        badge_layout.addStretch()

        view_diag_btn = QPushButton("Platform Audit...")
        view_diag_btn.clicked.connect(lambda: self.navigate_to_tab.emit(5))
        badge_layout.addWidget(view_diag_btn)

        status_card.add_layout(badge_layout)
        layout.addWidget(status_card)

        layout.addStretch()

    def _on_launch_clicked(self) -> None:
        if self.is_running:
            self.stop_requested.emit()
        else:
            self.launch_requested.emit()

    def set_running_state(self, running: bool) -> None:
        self.is_running = running
        if running:
            self.launch_btn.setText("⏹️  TERMINATE STUDIO")
            self.launch_btn.setObjectName("dangerButton")
            self.status_title.setText("Roblox Studio is Active")
            self.status_title.setStyleSheet("font-size: 22px; font-weight: 900; color: #a855f7; letter-spacing: 0.5px;")
            self.status_desc.setText("Process is active. Logs streaming to the Console tab.")
        else:
            self.launch_btn.setText("⚡  LAUNCH STUDIO")
            self.launch_btn.setObjectName("launchButton")
            self.status_title.setText("Roblox Studio is Ready")
            self.status_title.setStyleSheet("font-size: 22px; font-weight: 900; color: #ffffff; letter-spacing: 0.5px;")
            self.status_desc.setText("Wine prefix initialized • Vinegar Kombucha runner primed • FastFlags synchronized")

        self.launch_btn.style().unpolish(self.launch_btn)
        self.launch_btn.style().polish(self.launch_btn)

    def _on_prefix_changed(self, text: str) -> None:
        if text:
            self.config_mgr.set("active_prefix", text)

    def _on_renderer_changed(self, text: str) -> None:
        self.config_mgr.set("renderer", text)

    def _on_cef_changed(self, idx: int) -> None:
        modes = ["disabled", "software", "standard", "external"]
        if 0 <= idx < len(modes):
            self.config_mgr.set("cef_mode", modes[idx])

    def _toggle_fsync(self, checked: bool) -> None:
        env = self.config_mgr.get("env_vars", {})
        env["WINEFSYNC"] = "1" if checked else "0"
        self.config_mgr.set("env_vars", env)

    def _toggle_async(self, checked: bool) -> None:
        env = self.config_mgr.get("env_vars", {})
        env["DXVK_ASYNC"] = "1" if checked else "0"
        self.config_mgr.set("env_vars", env)

    def _toggle_gamescope(self, checked: bool) -> None:
        self.config_mgr.set("use_gamescope", checked)
