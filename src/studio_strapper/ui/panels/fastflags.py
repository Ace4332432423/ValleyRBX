"""
FastFlags Menu & Editor Panel for Studio Strapper.
Search, configure allowlisted flags, load presets, and add custom FastFlags into ClientAppSettings.json.
"""

from __future__ import annotations
from typing import Any, Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from studio_strapper.core.config import ConfigManager
from studio_strapper.core.fastflags import ALLOWLISTED_FLAGS, PRESETS, FastFlagManager
from studio_strapper.ui.widgets.card import Card
from studio_strapper.ui.widgets.toggle_switch import ToggleSwitch


class FastFlagsPanel(QWidget):
    """Panel dedicated to configuring Roblox Studio FastFlags and ClientAppSettings.json."""

    def __init__(self, config_mgr: ConfigManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config_mgr = config_mgr
        self.flag_mgr = FastFlagManager()
        self.custom_widgets: Dict[str, Any] = {}
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # 1. Preset Selector Card
        preset_card = Card("FastFlag Presets", "Apply curated sets of allowlisted performance and stability flags")
        preset_layout = QHBoxLayout()

        preset_layout.addWidget(QLabel("Load Preset:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["Performance", "High Quality", "Stability"])
        preset_layout.addWidget(self.preset_combo)

        btn_apply_preset = QPushButton("✨ Apply Preset")
        btn_apply_preset.clicked.connect(self._apply_preset)
        preset_layout.addWidget(btn_apply_preset)

        preset_layout.addStretch()

        btn_save_all = QPushButton("💾 Save & Sync Flags")
        btn_save_all.setObjectName("launchButton")
        btn_save_all.clicked.connect(self._save_flags)
        preset_layout.addWidget(btn_save_all)

        preset_card.add_layout(preset_layout)
        layout.addWidget(preset_card)

        # 2. Allowlisted FastFlags Table
        flags_card = Card(
            "Allowlisted FastFlags (ClientAppSettings.json)",
            "Confirmed local override flags approved by Roblox",
        )
        flags_layout = QVBoxLayout()

        # Search Bar
        search_box = QHBoxLayout()
        search_box.addWidget(QLabel("🔍 Search Flags:"))
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Filter by flag name or category...")
        self.txt_search.textChanged.connect(self._filter_flags)
        search_box.addWidget(self.txt_search)
        flags_layout.addLayout(search_box)

        # Table
        self.flag_table = QTableWidget()
        self.flag_table.setColumnCount(4)
        self.flag_table.setHorizontalHeaderLabels(["Flag Name", "Category", "Value / Toggle", "Description"])
        self.flag_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.flag_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.flag_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.flag_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.flag_table.setMinimumHeight(240)
        flags_layout.addWidget(self.flag_table)

        self.populate_allowlist_table()
        flags_card.add_layout(flags_layout)
        layout.addWidget(flags_card)

        # 3. Add Custom FastFlag Card
        custom_card = Card("Add Custom FastFlag", "Add custom or experimental flags to ClientAppSettings.json")
        custom_layout = QVBoxLayout()

        add_row = QHBoxLayout()
        self.txt_custom_name = QLineEdit()
        self.txt_custom_name.setPlaceholderText("Flag Name (e.g. FFlagCustomTest)")
        add_row.addWidget(self.txt_custom_name)

        self.combo_custom_type = QComboBox()
        self.combo_custom_type.addItems(["bool", "int", "string"])
        add_row.addWidget(self.combo_custom_type)

        self.txt_custom_val = QLineEdit()
        self.txt_custom_val.setPlaceholderText("Value (e.g. true or 120)")
        add_row.addWidget(self.txt_custom_val)

        btn_add_custom = QPushButton("➕ Add Flag")
        btn_add_custom.clicked.connect(self._add_custom_flag)
        add_row.addWidget(btn_add_custom)

        custom_layout.addLayout(add_row)

        notice = QLabel(
            "⚠️ Notice: Roblox enforces an official allowlist for client flags. "
            "Any custom flag not approved by Roblox will be silently ignored."
        )
        notice.setStyleSheet("color: #f9e2af; font-size: 11px; margin-top: 6px;")
        custom_layout.addWidget(notice)

        custom_card.add_layout(custom_layout)
        layout.addWidget(custom_card)

        layout.addStretch()

    def populate_allowlist_table(self) -> None:
        user_flags = self.config_mgr.get("fastflags", {})
        self.flag_table.setRowCount(len(ALLOWLISTED_FLAGS))

        for row, flag_info in enumerate(ALLOWLISTED_FLAGS):
            name = flag_info["name"]
            cat = flag_info["category"]
            f_type = flag_info["type"]
            val = user_flags.get(name, flag_info["default"])
            desc = flag_info["description"]

            # Col 0: Name
            self.flag_table.setItem(row, 0, QTableWidgetItem(name))

            # Col 1: Category
            self.flag_table.setItem(row, 1, QTableWidgetItem(cat))

            # Col 2: Value Widget
            if f_type == "bool":
                switch = ToggleSwitch(checked=bool(val))
                switch.toggled.connect(lambda chk, n=name: self._update_flag_val(n, chk))
                self.flag_table.setCellWidget(row, 2, switch)
                self.custom_widgets[name] = switch
            elif f_type == "int":
                spin = QSpinBox()
                spin.setRange(0, 10000)
                spin.setValue(int(val))
                spin.valueChanged.connect(lambda v, n=name: self._update_flag_val(n, v))
                self.flag_table.setCellWidget(row, 2, spin)
                self.custom_widgets[name] = spin
            else:
                edit = QLineEdit(str(val))
                edit.textChanged.connect(lambda t, n=name: self._update_flag_val(n, t))
                self.flag_table.setCellWidget(row, 2, edit)
                self.custom_widgets[name] = edit

            # Col 3: Description
            self.flag_table.setItem(row, 3, QTableWidgetItem(desc))

    def _filter_flags(self, text: str) -> None:
        query = text.lower().strip()
        for row in range(self.flag_table.rowCount()):
            name = self.flag_table.item(row, 0).text().lower()
            cat = self.flag_table.item(row, 1).text().lower()
            desc = self.flag_table.item(row, 3).text().lower()
            match = query in name or query in cat or query in desc
            self.flag_table.setRowHidden(row, not match)

    def _update_flag_val(self, name: str, val: Any) -> None:
        flags = self.config_mgr.get("fastflags", {})
        flags[name] = val
        self.config_mgr.set("fastflags", flags)

    def _apply_preset(self) -> None:
        preset_name = self.preset_combo.currentText()
        if preset_name in PRESETS:
            preset_data = PRESETS[preset_name]
            flags = self.config_mgr.get("fastflags", {})
            flags.update(preset_data)
            self.config_mgr.set("fastflags", flags)
            self.populate_allowlist_table()
            QMessageBox.information(self, "Preset Applied", f"Applied '{preset_name}' FastFlag preset.")

    def _add_custom_flag(self) -> None:
        name = self.txt_custom_name.text().strip()
        t = self.combo_custom_type.currentText()
        val_str = self.txt_custom_val.text().strip()

        if not name:
            return

        if t == "bool":
            val = val_str.lower() in ("true", "1", "yes")
        elif t == "int":
            try:
                val = int(val_str)
            except ValueError:
                val = 0
        else:
            val = val_str

        flags = self.config_mgr.get("fastflags", {})
        flags[name] = val
        self.config_mgr.set("fastflags", flags)

        self.txt_custom_name.clear()
        self.txt_custom_val.clear()
        self._save_flags()
        QMessageBox.information(self, "Flag Added", f"Added custom FastFlag:\n{name} = {val}")

    def _save_flags(self) -> None:
        flags = self.config_mgr.get("fastflags", {})
        cef_mode = self.config_mgr.get("cef_mode", "disabled")
        written = self.flag_mgr.apply_flags(flags, cef_mode=cef_mode)
        locations_str = "\n".join(str(p) for p in written)
        QMessageBox.information(self, "FastFlags Synchronized", f"FastFlags written to {len(written)} location(s):\n\n{locations_str}")
