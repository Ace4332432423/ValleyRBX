"""
Graphics Renderer & Environment Variables Panel for Studio Strapper.
Handles selecting renderer backends (D3D11 DXVK, Vulkan, OpenGL, D3D12) and managing environment variables.
"""

from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from studio_strapper.core.config import ConfigManager
from studio_strapper.ui.widgets.card import Card
from studio_strapper.ui.widgets.toggle_switch import ToggleSwitch


class GraphicsEnvPanel(QWidget):
    """Panel for configuring graphic renderer, Gamescope, and environment variables."""

    def __init__(self, config_mgr: ConfigManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config_mgr = config_mgr
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # 1. Renderer Selector Card
        renderer_card = Card("Graphics Renderer", "Select the graphics API translation layer used by Roblox Studio")
        renderer_layout = QVBoxLayout()

        self.renderer_group = QButtonGroup(self)
        self.r_d3d11 = QRadioButton("Direct3D 11 (DXVK) — Recommended")
        self.r_vulkan = QRadioButton("Vulkan — Native Roblox Studio Backend")
        self.r_opengl = QRadioButton("OpenGL — Legacy Compatibility Fallback")
        self.r_d3d12 = QRadioButton("Direct3D 12 (VKD3D) — Experimental")

        self.renderer_group.addButton(self.r_d3d11)
        self.renderer_group.addButton(self.r_vulkan)
        self.renderer_group.addButton(self.r_opengl)
        self.renderer_group.addButton(self.r_d3d12)

        cur_renderer = self.config_mgr.get("renderer", "Vulkan")
        if "DXVK" in cur_renderer or "D3D11" in cur_renderer:
            self.r_d3d11.setChecked(True)
        elif "OpenGL" in cur_renderer:
            self.r_opengl.setChecked(True)
        elif "D3D12" in cur_renderer or "VKD3D" in cur_renderer:
            self.r_d3d12.setChecked(True)
        else:
            self.r_vulkan.setChecked(True)

        self.renderer_group.buttonClicked.connect(self._on_renderer_selected)

        renderer_layout.addWidget(self.r_d3d11)
        renderer_layout.addWidget(self.r_vulkan)
        renderer_layout.addWidget(self.r_opengl)
        renderer_layout.addWidget(self.r_d3d12)

        renderer_card.add_layout(renderer_layout)
        layout.addWidget(renderer_card)

        # 2. Environment Variables Manager Card
        env_card = Card("Environment Variables", "Set custom runtime variables passed to Wine & Roblox Studio")
        env_layout = QVBoxLayout()

        # Table of active env variables
        self.env_table = QTableWidget()
        self.env_table.setColumnCount(3)
        self.env_table.setHorizontalHeaderLabels(["Variable Name", "Value", "Action"])
        self.env_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.env_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.env_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.env_table.setMinimumHeight(180)
        self.populate_env_table()
        env_layout.addWidget(self.env_table)

        # Add new env variable row
        add_row = QHBoxLayout()
        self.txt_key = QLineEdit()
        self.txt_key.setPlaceholderText("KEY (e.g. MESA_VK_DEVICE_SELECT)")
        add_row.addWidget(self.txt_key)

        self.txt_val = QLineEdit()
        self.txt_val.setPlaceholderText("VALUE (e.g. 10de:2487)")
        add_row.addWidget(self.txt_val)

        btn_add = QPushButton("➕ Add Variable")
        btn_add.clicked.connect(self._add_env_var)
        add_row.addWidget(btn_add)

        env_layout.addLayout(add_row)
        env_card.add_layout(env_layout)
        layout.addWidget(env_card)

        # 3. Gamescope Configuration Card (Wayland)
        gs_card = Card("Wayland Gamescope Wrapper", "Isolates mouse grab and fixes XWayland cursor escape issues")
        gs_grid = QGridLayout()
        gs_grid.setSpacing(12)

        gs_toggle_box = QHBoxLayout()
        self.gs_toggle = ToggleSwitch(checked=self.config_mgr.get("use_gamescope", False))
        self.gs_toggle.toggled.connect(self._on_gs_toggle)
        gs_toggle_box.addWidget(self.gs_toggle)
        gs_toggle_box.addWidget(QLabel("Enable Gamescope wrapper on Studio launch"))
        gs_toggle_box.addStretch()
        gs_grid.addLayout(gs_toggle_box, 0, 0, 1, 2)

        gs_grid.addWidget(QLabel("Gamescope Parameters:"), 1, 0)
        self.txt_gs_args = QLineEdit(self.config_mgr.get("gamescope_args", "-W 1920 -H 1080 -f --force-grab-cursor"))
        self.txt_gs_args.textChanged.connect(lambda t: self.config_mgr.set("gamescope_args", t))
        gs_grid.addWidget(self.txt_gs_args, 1, 1)

        gs_card.add_layout(gs_grid)
        layout.addWidget(gs_card)

        layout.addStretch()

    def populate_env_table(self) -> None:
        self.env_table.setRowCount(0)
        env_vars = self.config_mgr.get("env_vars", {})
        for row, (k, v) in enumerate(env_vars.items()):
            self.env_table.insertRow(row)
            self.env_table.setItem(row, 0, QTableWidgetItem(k))
            self.env_table.setItem(row, 1, QTableWidgetItem(str(v)))

            del_btn = QPushButton("Remove")
            del_btn.setProperty("class", "dangerButton")
            del_btn.clicked.connect(lambda _, key=k: self._remove_env_var(key))
            self.env_table.setCellWidget(row, 2, del_btn)

    def _add_env_var(self) -> None:
        k = self.txt_key.text().strip()
        v = self.txt_val.text().strip()
        if k:
            env = self.config_mgr.get("env_vars", {})
            env[k] = v
            self.config_mgr.set("env_vars", env)
            self.txt_key.clear()
            self.txt_val.clear()
            self.populate_env_table()

    def _remove_env_var(self, key: str) -> None:
        env = self.config_mgr.get("env_vars", {})
        if key in env:
            del env[key]
            self.config_mgr.set("env_vars", env)
            self.populate_env_table()

    def _on_renderer_selected(self, btn: QRadioButton) -> None:
        if btn == self.r_d3d11:
            self.config_mgr.set("renderer", "D3D11 (DXVK)")
        elif btn == self.r_opengl:
            self.config_mgr.set("renderer", "OpenGL")
        elif btn == self.r_d3d12:
            self.config_mgr.set("renderer", "D3D12 (VKD3D)")
        else:
            self.config_mgr.set("renderer", "Vulkan")

    def _on_gs_toggle(self, checked: bool) -> None:
        self.config_mgr.set("use_gamescope", checked)
