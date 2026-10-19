"""
Web Pages (CEF / WebView2) Management Panel for Studio Strapper.
Handles enabling/disabling web pages, configuring software rendering, and setting up host browser redirects.
"""

from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from studio_strapper.core.config import ConfigManager
from studio_strapper.ui.widgets.card import Card
from studio_strapper.ui.widgets.status_badge import StatusBadge


class CefWebPanel(QWidget):
    """Panel dedicated to configuring Chromium Embedded Framework (CEF) and Studio web features."""

    def __init__(self, config_mgr: ConfigManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config_mgr = config_mgr
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # 1. CEF Mode Selector Card
        mode_card = Card(
            "Roblox Studio Web Pages & Embedded Browser",
            "Configure how Chromium Embedded Framework (CEF) and WebView2 windows are handled under Wine",
        )
        mode_layout = QVBoxLayout()
        mode_layout.setSpacing(14)

        self.btn_group = QButtonGroup(self)

        # Option 1: Disabled
        self.r_disabled = QRadioButton("Disable Web Pages / CEF (Recommended — Prevents Crashes)")
        self.r_disabled.setToolTip("Disables Start Page, Toolbox web view, and CEF helper processes to avoid Wine rendering freezes.")
        self.btn_group.addButton(self.r_disabled)
        mode_layout.addWidget(self.r_disabled)

        desc_disabled = QLabel("↳ Injects FFlagStudioDisableCEF and prevents white-screen lockups on Linux.")
        desc_disabled.setStyleSheet("color: #a6adc8; margin-left: 24px; font-size: 12px;")
        mode_layout.addWidget(desc_disabled)

        # Option 2: Software Rendered
        self.r_software = QRadioButton("Software Rendered CEF (CPU Rendered)")
        self.r_software.setToolTip("Keeps web panels open but disables GPU acceleration for CEF (--disable-gpu).")
        self.btn_group.addButton(self.r_software)
        mode_layout.addWidget(self.r_software)

        desc_software = QLabel("↳ Solves GPU-process IPC crashes while keeping Start Page & Toolbox available.")
        desc_software.setStyleSheet("color: #a6adc8; margin-left: 24px; font-size: 12px;")
        mode_layout.addWidget(desc_software)

        # Option 3: Standard CEF
        self.r_standard = QRadioButton("Standard CEF (Full Hardware Accelerated)")
        self.r_standard.setToolTip("Uses Vinegar Kombucha's built-in CEF child-window patches.")
        self.btn_group.addButton(self.r_standard)
        mode_layout.addWidget(self.r_standard)

        desc_standard = QLabel("↳ Relies directly on Kombucha Wine patches for native-like CEF rendering.")
        desc_standard.setStyleSheet("color: #a6adc8; margin-left: 24px; font-size: 12px;")
        mode_layout.addWidget(desc_standard)

        # Option 4: External Browser
        self.r_external = QRadioButton("External Browser Redirect")
        self.r_external.setToolTip("Redirects all studio web links to your default Linux web browser via xdg-open.")
        self.btn_group.addButton(self.r_external)
        mode_layout.addWidget(self.r_external)

        desc_external = QLabel("↳ Keeps Studio lean and opens asset URLs in Firefox / Chromium / Brave.")
        desc_external.setStyleSheet("color: #a6adc8; margin-left: 24px; font-size: 12px;")
        mode_layout.addWidget(desc_external)

        cur_mode = self.config_mgr.get("cef_mode", "disabled")
        if cur_mode == "software":
            self.r_software.setChecked(True)
        elif cur_mode == "standard":
            self.r_standard.setChecked(True)
        elif cur_mode == "external":
            self.r_external.setChecked(True)
        else:
            self.r_disabled.setChecked(True)

        self.btn_group.buttonClicked.connect(self._on_mode_changed)

        mode_card.add_layout(mode_layout)
        layout.addWidget(mode_card)

        # 2. Status & Details Card
        info_card = Card("Why does CEF matter on Linux?", "Understanding Roblox Studio's browser components")
        info_layout = QVBoxLayout()

        p1 = QLabel(
            "Roblox Studio utilizes Chromium Embedded Framework (CEF) and Microsoft WebView2 for its Start Page, "
            "Toolbox, Asset Manager, and Marketplace. Under Wine, CEF spawns multiple sub-processes that require "
            "specific child-window handle permissions that often crash or deadlock standard Wine."
        )
        p1.setWordWrap(True)
        p1.setStyleSheet("color: #cdd6f4; font-size: 13px; line-height: 1.4;")
        info_layout.addWidget(p1)

        p2 = QLabel(
            "• If Studio fails to open, freezes on a grey/white screen, or crashes on startup: Select 'Disable Web Pages'.\n"
            "• Vinegar's Kombucha Wine runner includes custom patches designed specifically to help CEF survive on Linux."
        )
        p2.setWordWrap(True)
        p2.setStyleSheet("color: #89b4fa; font-size: 12px; margin-top: 8px;")
        info_layout.addWidget(p2)

        info_card.add_layout(info_layout)
        layout.addWidget(info_card)

        layout.addStretch()

    def _on_mode_changed(self, btn: QRadioButton) -> None:
        if btn == self.r_software:
            self.config_mgr.set("cef_mode", "software")
        elif btn == self.r_standard:
            self.config_mgr.set("cef_mode", "standard")
        elif btn == self.r_external:
            self.config_mgr.set("cef_mode", "external")
        else:
            self.config_mgr.set("cef_mode", "disabled")
