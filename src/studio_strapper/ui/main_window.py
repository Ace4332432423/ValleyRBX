"""
Main Application Window for ValleyRBX.
Matches Vinegar's full layout with circular icon, window controls, and cinematic glass styling.
"""

from __future__ import annotations
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QPoint, QRectF, QSize, Qt, QTimer
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QKeySequence, QLinearGradient, QPainter, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from studio_strapper.core.config import ConfigManager
from studio_strapper.core.diagnostics import SystemAuditor
from studio_strapper.core.fastflags import ALLOWLISTED_FLAGS, PRESETS, FastFlagManager
from studio_strapper.core.prefix_manager import PrefixManager
from studio_strapper.core.studio_launcher import StudioLauncher
from studio_strapper.core.wine_runner import WineRunner
from studio_strapper.ui.dialogs import EnvVarEditDialog, FastFlagEditDialog
from studio_strapper.ui.styles import THEME_QSS
from studio_strapper.ui.widgets.cinematic_canvas import CinematicCanvas
from studio_strapper.ui.widgets.circular_icon import CircularIcon
from studio_strapper.ui.widgets.preference_group import PreferenceGroup, PreferenceRow, SectionHeader
from studio_strapper.ui.widgets.reflective_button import ReflectiveCircleButton, ReflectivePillButton
from studio_strapper.ui.widgets.status_badge import StatusBadge
from studio_strapper.ui.widgets.toggle_switch import ToggleSwitch

ICON_PATH = str(Path(__file__).resolve().parents[3] / "assets" / "icon.png") if (Path(__file__).resolve().parents[3] / "assets" / "icon.png").exists() else ""


class MainWindow(QMainWindow):
    """Cinematic ValleyRBX window matching Vinegar's centered preferences hierarchy."""

    def __init__(self, config_mgr: ConfigManager) -> None:
        super().__init__()
        self.config_mgr = config_mgr
        self.launcher = StudioLauncher()
        self.prefix_mgr = PrefixManager()
        self.wine_runner = WineRunner()
        self.flag_mgr = FastFlagManager()
        self.auditor = SystemAuditor()

        self.setWindowTitle("ValleyRBX")
        self.resize(860, 840)
        self.setMinimumSize(720, 640)

        if Path(ICON_PATH).exists():
            self.setWindowIcon(QIcon(ICON_PATH))

        self.setStyleSheet(THEME_QSS)

        self._init_ui()
        self._wire_signals()

    def _init_ui(self) -> None:
        # Root Canvas with Cinematic Ambient Spotlight
        self.canvas = CinematicCanvas(self)
        self.setCentralWidget(self.canvas)

        root_layout = QVBoxLayout(self.canvas)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ---------------------------------------------------------
        # 1. TOP BAR (Circular Icon + Centered Title + Window Controls)
        # ---------------------------------------------------------
        top_bar = QWidget(self.canvas)
        top_bar.setFixedHeight(54)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(18, 10, 18, 10)

        # Left: Circular App Icon
        self.circular_logo = CircularIcon(ICON_PATH, size=28, parent=top_bar)
        top_layout.addWidget(self.circular_logo)

        top_layout.addStretch()

        # Center: Window Title
        self.title_lbl = QLabel("ValleyRBX", top_bar)
        self.title_lbl.setStyleSheet("""
            font-family: 'Source Sans 3', 'Source Sans Pro', 'Segoe UI', sans-serif;
            font-size: 15px;
            font-weight: 700;
            color: #f8fafc;
            letter-spacing: 0.5px;
        """)
        top_layout.addWidget(self.title_lbl)

        top_layout.addStretch()

        # Right: Window Controls (☰ Menu + ✕ Close Button)
        right_box = QHBoxLayout()
        right_box.setSpacing(8)

        # Hamburger Menu
        self.btn_hamburger = QPushButton("☰", top_bar)
        self.btn_hamburger.setFixedSize(30, 30)
        self.btn_hamburger.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                color: #cbd5e1;
                font-size: 13px;
                padding: 0;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.14);
                color: #ffffff;
            }
        """)
        self.btn_hamburger.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hamburger.clicked.connect(self._show_hamburger_menu)
        right_box.addWidget(self.btn_hamburger)

        # Close Window Button (✕)
        self.btn_close = QPushButton("✕", top_bar)
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                color: #cbd5e1;
                font-size: 12px;
                font-weight: 700;
                padding: 0;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.25);
                border: 1px solid rgba(239, 68, 68, 0.5);
                color: #fca5a5;
            }
        """)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(self.close)
        right_box.addWidget(self.btn_close)

        top_layout.addLayout(right_box)
        root_layout.addWidget(top_bar)

        # ---------------------------------------------------------
        # 2. SCROLLABLE PREFERENCE HIERARCHY
        # ---------------------------------------------------------
        scroll = QScrollArea(self.canvas)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(24, 10, 24, 36)
        scroll_layout.setSpacing(16)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Centered column (max width 660px matching Vinegar screenshot)
        content_column = QWidget()
        content_column.setMaximumWidth(660)
        content_column.setSizePolicy(content_column.sizePolicy().horizontalPolicy(), content_column.sizePolicy().verticalPolicy())
        col_layout = QVBoxLayout(content_column)
        col_layout.setContentsMargins(0, 0, 0, 0)
        col_layout.setSpacing(16)

        # ---------------------------------------------------------
        # HERO SECTION: RUN STUDIO & OPTIONS CIRCLE
        # ---------------------------------------------------------
        hero_widget = QWidget()
        hero_layout = QHBoxLayout(hero_widget)
        hero_layout.setContentsMargins(0, 6, 0, 14)
        hero_layout.setSpacing(12)
        hero_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Reflective Pill Button (Warm amber with 3D glass highlight)
        self.btn_run = ReflectivePillButton("Run Studio", hero_widget, gold_theme=True)
        self.btn_run.clicked.connect(self._toggle_launch)
        hero_layout.addWidget(self.btn_run)

        # Circular Options Button (⋮)
        self.btn_options = ReflectiveCircleButton("⋮", hero_widget)
        self.btn_options.clicked.connect(self._show_options_menu)
        hero_layout.addWidget(self.btn_options)

        col_layout.addWidget(hero_widget)

        # ---------------------------------------------------------
        # SECTION: COMPONENTS
        # ---------------------------------------------------------
        col_layout.addWidget(SectionHeader("Components", "⚙", self))

        group_components = PreferenceGroup(self)

        # Row 1: Web Pages
        self.switch_web = ToggleSwitch(checked=self.config_mgr.get("cef_mode") != "disabled")
        self.switch_web.toggled.connect(self._on_web_pages_toggled)

        self.btn_web_expand = QPushButton("⌄")
        self.btn_web_expand.setFixedSize(26, 26)
        self.btn_web_expand.setStyleSheet("background: transparent; border: none; color: #94a3b8; font-size: 14px;")
        self.btn_web_expand.setCursor(Qt.CursorShape.PointingHandCursor)

        web_controls = QWidget()
        web_ctl_layout = QHBoxLayout(web_controls)
        web_ctl_layout.setContentsMargins(0, 0, 0, 0)
        web_ctl_layout.setSpacing(6)
        web_ctl_layout.addWidget(self.switch_web)
        web_ctl_layout.addWidget(self.btn_web_expand)

        self.row_web = PreferenceRow(
            "Web Pages",
            "May be used for UI elements and logging in",
            web_controls,
            group_components,
        )

        web_drawer = QWidget()
        web_drawer_layout = QVBoxLayout(web_drawer)
        web_drawer_layout.setContentsMargins(18, 0, 18, 12)
        web_drawer_layout.setSpacing(6)

        lbl_cef = QLabel("CEF Engine Mode:", web_drawer)
        lbl_cef.setStyleSheet("color: #cbd5e1; font-weight: 600; font-size: 12px;")
        self.combo_cef = QComboBox(web_drawer)
        self.combo_cef.addItems([
            "disabled (Recommended — Prevents Studio Crashes)",
            "software (CPU Rendered)",
            "standard (Embedded Hardware CEF)",
            "external (System Browser Redirect)",
        ])
        cur_cef = self.config_mgr.get("cef_mode", "disabled")
        for i in range(self.combo_cef.count()):
            if self.combo_cef.itemText(i).startswith(cur_cef):
                self.combo_cef.setCurrentIndex(i)
                break
        self.combo_cef.currentIndexChanged.connect(self._on_cef_combo_changed)
        web_drawer_layout.addWidget(lbl_cef)
        web_drawer_layout.addWidget(self.combo_cef)

        self.row_web.set_expandable_content(web_drawer)
        self.btn_web_expand.clicked.connect(self.row_web.toggle_expand)
        group_components.add_row(self.row_web)

        # Row 2: Wine Installation
        runner_controls = QWidget()
        rc_layout = QHBoxLayout(runner_controls)
        rc_layout.setContentsMargins(0, 0, 0, 0)
        rc_layout.setSpacing(6)

        btn_runner_switch = QPushButton("↹")
        btn_runner_switch.setToolTip("Switch Wine runner")
        btn_runner_switch.setFixedSize(28, 28)
        btn_runner_switch.setStyleSheet("background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 6px; color: #cbd5e1;")
        btn_runner_switch.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_runner_folder = QPushButton("📁")
        btn_runner_folder.setToolTip("Open runner folder")
        btn_runner_folder.setFixedSize(28, 28)
        btn_runner_folder.setStyleSheet("background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 6px; color: #cbd5e1;")
        btn_runner_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_runner_folder.clicked.connect(self._open_runner_folder)

        rc_layout.addWidget(btn_runner_switch)
        rc_layout.addWidget(btn_runner_folder)

        runner_sub = str(self.config_mgr.get("runner_path", "/home/ace/.local/share/vinegar/kombucha"))
        self.row_runner = PreferenceRow(
            "Wine Installation",
            runner_sub,
            runner_controls,
            group_components,
        )

        runner_drawer = QWidget()
        rd_layout = QVBoxLayout(runner_drawer)
        rd_layout.setContentsMargins(18, 0, 18, 12)
        rd_layout.setSpacing(6)

        self.combo_runner = QComboBox(runner_drawer)
        discovered = self.wine_runner.discover_runners()
        for label, rtype, p in discovered:
            self.combo_runner.addItem(f"{label} [{p}]", str(p))
        for i in range(self.combo_runner.count()):
            if self.combo_runner.itemData(i) == self.config_mgr.get("runner_path"):
                self.combo_runner.setCurrentIndex(i)
                break
        self.combo_runner.currentIndexChanged.connect(self._on_runner_selected)
        rd_layout.addWidget(self.combo_runner)

        self.row_runner.set_expandable_content(runner_drawer)
        btn_runner_switch.clicked.connect(self.row_runner.toggle_expand)
        group_components.add_row(self.row_runner)

        # Row 3: Advanced Wine Settings
        btn_winecfg = QPushButton("Wine Settings", self)
        btn_winecfg.setFixedSize(120, 30)
        btn_winecfg.setStyleSheet("""background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 6px;
    color: #38bdf8;
    font-size: 13px;
    padding: 4px;""")
        btn_winecfg.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_winecfg.setToolTip("Launch winecfg for the active Wine prefix")
        btn_winecfg.clicked.connect(lambda: self._run_wine_tool("winecfg"))

        self.row_adv_wine = PreferenceRow(
            "Advanced Wine Settings",
            "Opens winecfg for the active prefix",
            btn_winecfg,
            group_components,
        )
        group_components.add_row(self.row_adv_wine)

        col_layout.addWidget(group_components)

        # ---------------------------------------------------------
        # SECTION: DISPLAY
        # ---------------------------------------------------------
        col_layout.addWidget(SectionHeader("Display", "", self))

        group_display = PreferenceGroup(self)

        # Row 4: Renderer
        self.combo_renderer = QComboBox()
        self.combo_renderer.addItems(["Vulkan", "D3D11 (DXVK)", "OpenGL", "D3D12 (VKD3D)"])
        self.combo_renderer.setCurrentText(self.config_mgr.get("renderer", "Vulkan"))
        self.combo_renderer.currentTextChanged.connect(lambda text: self.config_mgr.set("renderer", text))

        row_renderer = PreferenceRow(
            "Renderer",
            "Studio's Graphics Mode",
            self.combo_renderer,
            group_display,
        )
        group_display.add_row(row_renderer)

        # Row 5: Virtual Desktops / Gamescope
        self.switch_gamescope = ToggleSwitch(checked=self.config_mgr.get("use_gamescope", False))
        self.switch_gamescope.toggled.connect(lambda chk: self.config_mgr.set("use_gamescope", chk))

        btn_gs_expand = QPushButton("⌄")
        btn_gs_expand.setFixedSize(26, 26)
        btn_gs_expand.setStyleSheet("background: transparent; border: none; color: #94a3b8; font-size: 14px;")
        btn_gs_expand.setCursor(Qt.CursorShape.PointingHandCursor)

        gs_controls = QWidget()
        gs_c_layout = QHBoxLayout(gs_controls)
        gs_c_layout.setContentsMargins(0, 0, 0, 0)
        gs_c_layout.setSpacing(6)
        gs_c_layout.addWidget(self.switch_gamescope)
        gs_c_layout.addWidget(btn_gs_expand)

        self.row_gamescope = PreferenceRow(
            "Virtual Desktops",
            "Create an isolated window for each Studio instance",
            gs_controls,
            group_display,
        )

        gs_drawer = QWidget()
        gs_d_layout = QVBoxLayout(gs_drawer)
        gs_d_layout.setContentsMargins(18, 0, 18, 12)
        gs_d_layout.setSpacing(6)

        lbl_gs_args = QLabel("Launcher Command Parameters (ex. gamescope):", gs_drawer)
        lbl_gs_args.setStyleSheet("color: #cbd5e1; font-size: 12px; font-weight: 600;")
        self.txt_gs_args = QLineEdit(self.config_mgr.get("gamescope_args", "-W 1920 -H 1080 -f --force-grab-cursor"))
        self.txt_gs_args.textChanged.connect(lambda t: self.config_mgr.set("gamescope_args", t))
        gs_d_layout.addWidget(lbl_gs_args)
        gs_d_layout.addWidget(self.txt_gs_args)

        self.row_gamescope.set_expandable_content(gs_drawer)
        btn_gs_expand.clicked.connect(self.row_gamescope.toggle_expand)
        group_display.add_row(self.row_gamescope)

        col_layout.addWidget(group_display)

        # ---------------------------------------------------------
        # SECTION: BEHAVIOR
        # ---------------------------------------------------------
        col_layout.addWidget(SectionHeader("Behavior", "", self))

        group_behavior = PreferenceGroup(self)

        # Row: Launcher Command
        btn_cmd_edit = QPushButton("✎")
        btn_cmd_edit.setFixedSize(26, 26)
        btn_cmd_edit.setStyleSheet("background: transparent; border: none; color: #94a3b8; font-size: 14px;")
        btn_cmd_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cmd_edit.clicked.connect(self.row_gamescope.toggle_expand)

        row_launcher_cmd = PreferenceRow(
            "Launcher Command (ex. gamescope)",
            "",
            btn_cmd_edit,
            group_behavior,
        )
        group_behavior.add_row(row_launcher_cmd)

        # Row: Share Activity on Discord
        self.switch_discord = ToggleSwitch(checked=bool(self.config_mgr.get("discord_rpc", False)))
        self.switch_discord.toggled.connect(lambda chk: self.config_mgr.set("discord_rpc", chk))

        row_discord = PreferenceRow(
            "Share Activity on Discord",
            "Display your development status on your Discord profile",
            self.switch_discord,
            group_behavior,
        )
        group_behavior.add_row(row_discord)

        # Row: GameMode
        self.switch_gamemode = ToggleSwitch(checked=bool(self.config_mgr.get("use_gamemode", True)))
        self.switch_gamemode.toggled.connect(lambda chk: self.config_mgr.set("use_gamemode", chk))

        row_gamemode = PreferenceRow(
            "GameMode",
            "Apply system optimizations. May improve performance.",
            self.switch_gamemode,
            group_behavior,
        )
        group_behavior.add_row(row_gamemode)

        # Row: Debug
        self.switch_debug = ToggleSwitch(checked=bool(self.config_mgr.get("debug_logs", False)))
        self.switch_debug.toggled.connect(lambda chk: self.config_mgr.set("debug_logs", chk))

        row_debug = PreferenceRow(
            "Debug",
            "Output Studio logs and Web API requests",
            self.switch_debug,
            group_behavior,
        )
        group_behavior.add_row(row_debug)

        col_layout.addWidget(group_behavior)

        # ---------------------------------------------------------
        # SECTION: ENVIRONMENT (With + action)
        # ---------------------------------------------------------
        sec_env = SectionHeader("Environment", "+", self)
        sec_env.action_clicked.connect(self._prompt_add_env_var)
        col_layout.addWidget(sec_env)

        self.group_env = PreferenceGroup(self)
        self._populate_env_rows()
        col_layout.addWidget(self.group_env)

        # ---------------------------------------------------------
        # SECTION: FAST FLAGS (With + action)
        # ---------------------------------------------------------
        sec_fflags = SectionHeader("Fast Flags", "+", self)
        sec_fflags.action_clicked.connect(self._prompt_add_fflag)
        col_layout.addWidget(sec_fflags)

        self.group_fflags = PreferenceGroup(self)
        self._populate_fflag_rows()
        col_layout.addWidget(self.group_fflags)

        # ---------------------------------------------------------
        # SECTION: DEPLOYMENT OVERRIDES
        # ---------------------------------------------------------
        col_layout.addWidget(SectionHeader("Deployment Overrides", "", self))

        group_deploy = PreferenceGroup(self)

        btn_ver_edit = QPushButton("✎")
        btn_ver_edit.setFixedSize(26, 26)
        btn_ver_edit.setStyleSheet("background: transparent; border: none; color: #94a3b8; font-size: 14px;")
        btn_ver_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ver_edit.clicked.connect(self._prompt_edit_version)

        self.row_ver = PreferenceRow(
            "Studio Deployment Version",
            str(self.config_mgr.get("override_version", "")),
            btn_ver_edit,
            group_deploy,
        )
        group_deploy.add_row(self.row_ver)

        btn_chan_edit = QPushButton("✎")
        btn_chan_edit.setFixedSize(26, 26)
        btn_chan_edit.setStyleSheet("background: transparent; border: none; color: #94a3b8; font-size: 14px;")
        btn_chan_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_chan_edit.clicked.connect(self._prompt_edit_channel)

        self.row_chan = PreferenceRow(
            "Studio Update Channel",
            str(self.config_mgr.get("override_channel", "")),
            btn_chan_edit,
            group_deploy,
        )
        group_deploy.add_row(self.row_chan)

        col_layout.addWidget(group_deploy)

        # Add centered content column to scroll layout
        scroll_layout.addWidget(content_column)
        scroll.setWidget(scroll_content)
        root_layout.addWidget(scroll)

    def _wire_signals(self) -> None:
        self.launcher.process_started.connect(self._on_studio_started)
        self.launcher.process_exited.connect(self._on_studio_exited)

        # GUI Watchdog timer to ensure button text always stays in sync
        self._watchdog = QTimer(self)
        self._watchdog.timeout.connect(self._check_studio_process)
        self._watchdog.start(800)

    def _on_studio_started(self, pid: int) -> None:
        self.btn_run.setText("Stop Studio")
        self.title_lbl.setText("ValleyRBX — Studio Running")

    def _on_studio_exited(self, code: int) -> None:
        self.btn_run.setText("Run Studio")
        self.title_lbl.setText("ValleyRBX")

    def _check_studio_process(self) -> None:
        if not self.launcher.is_running() and self.btn_run.text() != "Run Studio":
            self.btn_run.setText("Run Studio")
            self.title_lbl.setText("ValleyRBX")

    # -------------------------------------------------------------
    # ENVIRONMENT ROWS (KEY / VAL with ✎ and ⊗)
    # -------------------------------------------------------------
    def _populate_env_rows(self) -> None:
        while self.group_env.group_layout.count():
            item = self.group_env.group_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        env_vars = self.config_mgr.get("env_vars", {})
        for k, v in list(env_vars.items()):
            actions_box = QWidget()
            actions_box.setFixedSize(62, 28)
            a_layout = QHBoxLayout(actions_box)
            a_layout.setContentsMargins(0, 0, 0, 0)
            a_layout.setSpacing(6)

            btn_edit = QPushButton("✎", actions_box)
            btn_edit.setFixedSize(26, 26)
            btn_edit.setStyleSheet("""
                QPushButton {
                    background: rgba(56, 189, 248, 0.12);
                    border: 1px solid rgba(56, 189, 248, 0.35);
                    border-radius: 6px;
                    color: #38bdf8;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 0px;
                }
                QPushButton:hover {
                    background: rgba(56, 189, 248, 0.28);
                    border: 1px solid #38bdf8;
                    color: #ffffff;
                }
            """)
            btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_edit.setToolTip("Edit Environment Variable")
            btn_edit.clicked.connect(lambda _, key=k, val=v: self._edit_env_var(key, val))

            btn_del = QPushButton("⊗", actions_box)
            btn_del.setFixedSize(26, 26)
            btn_del.setStyleSheet("""
                QPushButton {
                    background: rgba(239, 68, 68, 0.12);
                    border: 1px solid rgba(239, 68, 68, 0.35);
                    border-radius: 6px;
                    color: #f87171;
                    font-size: 15px;
                    font-weight: bold;
                    padding: 0px;
                }
                QPushButton:hover {
                    background: rgba(239, 68, 68, 0.28);
                    border: 1px solid #ef4444;
                    color: #ffffff;
                }
            """)
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setToolTip("Delete Environment Variable")
            btn_del.clicked.connect(lambda _, key=k: self._remove_env_var(key))

            a_layout.addWidget(btn_edit)
            a_layout.addWidget(btn_del)

            row = PreferenceRow(k, str(v), actions_box, self.group_env)
            self.group_env.add_row(row)

    def _prompt_add_env_var(self) -> None:
        dlg = EnvVarEditDialog(self, key="", value="", is_new=True)
        if dlg.exec():
            env = self.config_mgr.get("env_vars", {})
            env[dlg.saved_key] = dlg.saved_value
            self.config_mgr.set("env_vars", env)
            self._populate_env_rows()

    def _edit_env_var(self, key: str, current_val: any) -> None:
        dlg = EnvVarEditDialog(self, key=key, value=str(current_val), is_new=False)
        if dlg.exec():
            env = self.config_mgr.get("env_vars", {})
            if dlg.deleted:
                if key in env:
                    del env[key]
            else:
                if dlg.saved_key != key and key in env:
                    del env[key]
                env[dlg.saved_key] = dlg.saved_value
            self.config_mgr.set("env_vars", env)
            self._populate_env_rows()

    def _remove_env_var(self, key: str) -> None:
        env = self.config_mgr.get("env_vars", {})
        if key in env:
            del env[key]
            self.config_mgr.set("env_vars", env)
            self._populate_env_rows()

    # -------------------------------------------------------------
    # FAST FLAGS ROWS (Display all, editable, deletable, add new)
    # -------------------------------------------------------------
    def _populate_fflag_rows(self) -> None:
        while self.group_fflags.group_layout.count():
            item = self.group_fflags.group_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        flags = self.config_mgr.get("fastflags", {})
        for k, v in list(flags.items()):
            actions_box = QWidget()
            actions_box.setFixedSize(62, 28)
            a_layout = QHBoxLayout(actions_box)
            a_layout.setContentsMargins(0, 0, 0, 0)
            a_layout.setSpacing(6)

            btn_edit = QPushButton("✎", actions_box)
            btn_edit.setFixedSize(26, 26)
            btn_edit.setStyleSheet("""
                QPushButton {
                    background: rgba(56, 189, 248, 0.12);
                    border: 1px solid rgba(56, 189, 248, 0.35);
                    border-radius: 6px;
                    color: #38bdf8;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 0px;
                }
                QPushButton:hover {
                    background: rgba(56, 189, 248, 0.28);
                    border: 1px solid #38bdf8;
                    color: #ffffff;
                }
            """)
            btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_edit.setToolTip("Edit Fast Flag")
            btn_edit.clicked.connect(lambda _, key=k, val=v: self._edit_fflag(key, val))

            btn_del = QPushButton("⊗", actions_box)
            btn_del.setFixedSize(26, 26)
            btn_del.setStyleSheet("""
                QPushButton {
                    background: rgba(239, 68, 68, 0.12);
                    border: 1px solid rgba(239, 68, 68, 0.35);
                    border-radius: 6px;
                    color: #f87171;
                    font-size: 15px;
                    font-weight: bold;
                    padding: 0px;
                }
                QPushButton:hover {
                    background: rgba(239, 68, 68, 0.28);
                    border: 1px solid #ef4444;
                    color: #ffffff;
                }
            """)
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setToolTip("Delete Fast Flag")
            btn_del.clicked.connect(lambda _, key=k: self._remove_fflag(key))

            a_layout.addWidget(btn_edit)
            a_layout.addWidget(btn_del)

            row = PreferenceRow(k, f"Value: {v}", actions_box, self.group_fflags)
            self.group_fflags.add_row(row)

    def _prompt_add_fflag(self) -> None:
        dlg = FastFlagEditDialog(self, name="", value=True, is_new=True)
        if dlg.exec():
            flags = self.config_mgr.get("fastflags", {})
            flags[dlg.saved_name] = dlg.saved_value
            self.config_mgr.set("fastflags", flags)
            self.flag_mgr.apply_flags(flags, cef_mode=self.config_mgr.get("cef_mode", "disabled"))
            self._populate_fflag_rows()

    def _edit_fflag(self, key: str, current_val: any) -> None:
        dlg = FastFlagEditDialog(self, name=key, value=current_val, is_new=False)
        if dlg.exec():
            flags = self.config_mgr.get("fastflags", {})
            if dlg.deleted:
                if key in flags:
                    del flags[key]
            else:
                if dlg.saved_name != key and key in flags:
                    del flags[key]
                flags[dlg.saved_name] = dlg.saved_value
            self.config_mgr.set("fastflags", flags)
            self.flag_mgr.apply_flags(flags, cef_mode=self.config_mgr.get("cef_mode", "disabled"))
            self._populate_fflag_rows()

    def _remove_fflag(self, key: str) -> None:
        flags = self.config_mgr.get("fastflags", {})
        if key in flags:
            del flags[key]
            self.config_mgr.set("fastflags", flags)
            self.flag_mgr.apply_flags(flags, cef_mode=self.config_mgr.get("cef_mode", "disabled"))
            self._populate_fflag_rows()

    def _prompt_edit_version(self) -> None:
        val, ok = QInputDialog.getText(self, "Deployment Version", "Studio Deployment Version override:", text=str(self.config_mgr.get("override_version", "")))
        if ok:
            clean = val.strip()
            self.config_mgr.set("override_version", clean)
            if hasattr(self, "row_ver"):
                self.row_ver.set_subtitle(clean)

    def _prompt_edit_channel(self) -> None:
        val, ok = QInputDialog.getText(self, "Update Channel", "Studio Update Channel override:", text=str(self.config_mgr.get("override_channel", "")))
        if ok:
            clean = val.strip()
            self.config_mgr.set("override_channel", clean)
            if hasattr(self, "row_chan"):
                self.row_chan.set_subtitle(clean)

    # -------------------------------------------------------------
    # ACTION HANDLERS
    # -------------------------------------------------------------
    def _toggle_launch(self) -> None:
        if self.launcher.is_running():
            self.launcher.terminate()
            self.btn_run.setText("Run Studio")
            self.title_lbl.setText("ValleyRBX")
        else:
            self.btn_run.setText("Starting...")
            self.title_lbl.setText("ValleyRBX — Starting Studio...")

            prefix = Path(self.config_mgr.get("active_prefix"))
            runner = Path(self.config_mgr.get("runner_path"))
            renderer = self.config_mgr.get("renderer", "Vulkan")
            cef_mode = self.config_mgr.get("cef_mode", "disabled")
            env_vars = self.config_mgr.get("env_vars", {})
            fastflags = self.config_mgr.get("fastflags", {})
            use_gamescope = self.config_mgr.get("use_gamescope", False)
            gs_args = self.config_mgr.get("gamescope_args", "")
            discord_rpc = bool(self.config_mgr.get("discord_rpc", False))
            use_gamemode = bool(self.config_mgr.get("use_gamemode", True))
            debug_logs = bool(self.config_mgr.get("debug_logs", False))
            override_version = str(self.config_mgr.get("override_version", ""))
            override_channel = str(self.config_mgr.get("override_channel", ""))

            ok = self.launcher.launch(
                prefix_path=prefix,
                runner_path=runner,
                renderer=renderer,
                cef_mode=cef_mode,
                env_vars=env_vars,
                user_fastflags=fastflags,
                use_gamescope=use_gamescope,
                gamescope_args=gs_args,
                discord_rpc=discord_rpc,
                use_gamemode=use_gamemode,
                debug_logs=debug_logs,
                override_version=override_version,
                override_channel=override_channel,
            )

            if ok:
                self.btn_run.setText("Stop Studio")
                self.title_lbl.setText("ValleyRBX — Studio Running")
            else:
                self.btn_run.setText("Run Studio")
                self.title_lbl.setText("ValleyRBX")

    def _show_options_menu(self) -> None:
        menu = QMenu(self)
        act_winecfg = menu.addAction("🍷  Edit Prefix (winecfg)")
        act_regedit = menu.addAction("📝  Registry Editor (regedit)")
        act_winetricks = menu.addAction("🛠️  Winetricks")
        act_browse = menu.addAction("📂  Browse drive_c Folder")
        menu.addSeparator()
        act_clone = menu.addAction("📋  Clone Prefix (btrfs reflink)")
        act_kill = menu.addAction("⚠️  Kill Wineserver")
        menu.addSeparator()
        act_audit = menu.addAction("🔍  CachyOS System Audit")
        act_logs = menu.addAction("📜  Live Execution Logs")

        action = menu.exec(self.btn_options.mapToGlobal(QPoint(0, self.btn_options.height() + 4)))

        if action == act_winecfg:
            self._run_wine_tool("winecfg")
        elif action == act_regedit:
            self._run_wine_tool("regedit")
        elif action == act_winetricks:
            self._run_wine_tool("winetricks")
        elif action == act_browse:
            self._open_prefix_folder()
        elif action == act_clone:
            self._clone_prefix()
        elif action == act_kill:
            self._kill_wineserver()
        elif action == act_audit:
            self._show_audit_dialog()
        elif action == act_logs:
            self._show_logs_dialog()

    def _show_hamburger_menu(self) -> None:
        menu = QMenu(self)
        act_audit = menu.addAction("🔍  Platform Diagnostics")
        act_logs = menu.addAction("📜  Console Logs")
        menu.addSeparator()
        act_about = menu.addAction("ℹ️  About ValleyRBX")

        action = menu.exec(self.btn_hamburger.mapToGlobal(QPoint(-120, self.btn_hamburger.height() + 4)))
        if action == act_audit:
            self._show_audit_dialog()
        elif action == act_logs:
            self._show_logs_dialog()
        elif action == act_about:
            QMessageBox.information(
                self,
                "About ValleyRBX",
                "ValleyRBX 1.0\nCinematic Roblox Studio Environment Manager\n"
                "Optimized for CachyOS & Vinegar Kombucha Wine Handler."
            )

    def _on_web_pages_toggled(self, checked: bool) -> None:
        if checked:
            self.config_mgr.set("cef_mode", "standard")
            self.combo_cef.setCurrentIndex(2)
        else:
            self.config_mgr.set("cef_mode", "disabled")
            self.combo_cef.setCurrentIndex(0)

    def _on_cef_combo_changed(self, idx: int) -> None:
        modes = ["disabled", "software", "standard", "external"]
        if 0 <= idx < len(modes):
            mode = modes[idx]
            self.config_mgr.set("cef_mode", mode)
            self.switch_web.setChecked(mode != "disabled", animate=True)

    def _on_runner_selected(self, idx: int) -> None:
        p = self.combo_runner.itemData(idx)
        if p:
            self.config_mgr.set("runner_path", p)
            self.row_runner.lbl_sub.setText(str(p))

    def _open_runner_folder(self) -> None:
        p = Path(self.config_mgr.get("runner_path", ""))
        if p.exists():
            subprocess.Popen(["xdg-open", str(p)])

    def _open_prefix_folder(self) -> None:
        p = Path(self.config_mgr.get("active_prefix", ""))
        self.prefix_mgr.open_in_file_manager(p)

    def _run_wine_tool(self, tool_name: str) -> None:
        prefix = Path(self.config_mgr.get("active_prefix"))
        runner = Path(self.config_mgr.get("runner_path"))
        self.wine_runner.run_tool(tool_name, prefix, runner, self.config_mgr.get("env_vars", {}))

    def _kill_wineserver(self) -> None:
        prefix = Path(self.config_mgr.get("active_prefix"))
        runner = Path(self.config_mgr.get("runner_path"))
        ok = self.wine_runner.kill_wineserver(prefix, runner)
        if ok:
            QMessageBox.information(self, "Wineserver", "Wineserver process terminated successfully.")
        else:
            QMessageBox.warning(self, "Wineserver", "Failed to terminate wineserver or no process was running.")

    def _browse_prefix(self) -> None:
        chosen = QFileDialog.getExistingDirectory(self, "Select Wine Prefix Directory", str(Path.home()))
        if chosen:
            known = self.config_mgr.get("known_prefixes", [])
            if chosen not in known:
                known.append(chosen)
                self.config_mgr.set("known_prefixes", known)
                self.combo_prefix.addItem(chosen)
            self.combo_prefix.setCurrentText(chosen)

    def _on_prefix_changed(self, text: str) -> None:
        if text:
            self.config_mgr.set("active_prefix", text)

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
                self.combo_prefix.addItem(chosen)
                self.combo_prefix.setCurrentText(chosen)
                QMessageBox.information(self, "Success", f"Prefix successfully cloned to:\n{dest}")
            except Exception as e:
                QMessageBox.critical(self, "Clone Error", f"Failed to clone prefix:\n{e}")

    def _show_audit_dialog(self) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle("CachyOS Platform Audit")
        dlg.resize(580, 480)
        dlg.setStyleSheet(THEME_QSS)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("CachyOS Platform Diagnostics", dlg)
        title.setStyleSheet("font-size: 16px; font-weight: 800; color: #f8fafc;")
        layout.addWidget(title)

        results = self.auditor.run_full_audit()
        for res in results:
            row = QHBoxLayout()
            badge = StatusBadge(res["title"], res["status"])
            badge.setMinimumWidth(200)
            row.addWidget(badge)

            detail = QLabel(res["details"])
            detail.setWordWrap(True)
            detail.setStyleSheet("color: #cbd5e1; font-size: 12px;")
            row.addWidget(detail)
            layout.addLayout(row)

        layout.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(dlg.accept)
        layout.addWidget(btn_close)
        dlg.exec()

    def _show_logs_dialog(self) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle("ValleyRBX Console Logs")
        dlg.resize(680, 520)
        dlg.setStyleSheet(THEME_QSS)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        from PySide6.QtWidgets import QPlainTextEdit
        console = QPlainTextEdit(dlg)
        console.setReadOnly(True)
        console.setPlainText("ValleyRBX Real-time Process Output:\n" + "=" * 50 + "\n")
        layout.addWidget(console)

        self.launcher.add_log_listener(console.appendPlainText)

        btn_row = QHBoxLayout()
        btn_clear = QPushButton("Clear Console")
        btn_clear.clicked.connect(console.clear)
        btn_row.addWidget(btn_clear)
        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(dlg.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

        dlg.exec()
