"""
Modal editing dialogs for Environment Variables and FastFlags.
Styled with frosted glass and 2018 Roblox Source Sans typography.
"""

from __future__ import annotations
from typing import Any, Optional, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class EnvVarEditDialog(QDialog):
    """Dialog for creating or editing an environment variable."""

    def __init__(
        self,
        parent: QWidget | None = None,
        key: str = "",
        value: str = "",
        is_new: bool = True,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("New Environment Variable" if is_new else "Edit Environment Variable")
        self.setFixedWidth(460)
        self.setModal(True)

        self.deleted = False
        self.saved_key = key
        self.saved_value = value

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Title Header
        title_lbl = QLabel("➕ Add Environment Variable" if is_new else f"✎ Edit Variable: {key}", self)
        title_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #f8fafc;")
        layout.addWidget(title_lbl)

        # Variable Name
        lbl_k = QLabel("Variable Name:", self)
        lbl_k.setStyleSheet("font-size: 12px; font-weight: 600; color: #cbd5e1;")
        self.txt_key = QLineEdit(key, self)
        self.txt_key.setPlaceholderText("e.g. MESA_VK_DEVICE_SELECT or DXVK_HUD")
        layout.addWidget(lbl_k)
        layout.addWidget(self.txt_key)

        # Variable Value
        lbl_v = QLabel("Variable Value:", self)
        lbl_v.setStyleSheet("font-size: 12px; font-weight: 600; color: #cbd5e1;")
        self.txt_val = QLineEdit(value, self)
        self.txt_val.setPlaceholderText("e.g. 1 or compiler,fps")
        layout.addWidget(lbl_v)
        layout.addWidget(self.txt_val)

        layout.addSpacing(6)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        if not is_new:
            self.btn_del = QPushButton("Delete", self)
            self.btn_del.setObjectName("dangerButton")
            self.btn_del.clicked.connect(self._on_delete)
            btn_layout.addWidget(self.btn_del)

        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancel", self)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_save = QPushButton("Add Variable" if is_new else "Save Changes", self)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0284c7, stop:1 #0369a1);
                color: #ffffff;
                font-weight: 700;
                border: 1px solid #38bdf8;
                border-radius: 8px;
                padding: 7px 18px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #38bdf8, stop:1 #0284c7);
                border: 1px solid #7dd3fc;
            }
        """)
        self.btn_save.clicked.connect(self._on_save)
        btn_layout.addWidget(self.btn_save)

        layout.addLayout(btn_layout)

    def _on_save(self) -> None:
        key = self.txt_key.text().strip()
        val = self.txt_val.text().strip()
        if not key:
            return
        self.saved_key = key
        self.saved_value = val
        self.accept()

    def _on_delete(self) -> None:
        self.deleted = True
        self.accept()


class FastFlagEditDialog(QDialog):
    """Dialog for creating or editing a FastFlag with type awareness."""

    def __init__(
        self,
        parent: QWidget | None = None,
        name: str = "",
        value: Any = None,
        is_new: bool = True,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("New Fast Flag" if is_new else "Edit Fast Flag")
        self.setFixedWidth(500)
        self.setModal(True)

        self.deleted = False
        self.saved_name = name
        self.saved_value: Any = value

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header Title
        title_lbl = QLabel("🚩 Add Fast Flag" if is_new else f"✎ Edit Flag: {name}", self)
        title_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #f8fafc;")
        layout.addWidget(title_lbl)

        # Flag Name
        lbl_n = QLabel("Flag Name:", self)
        lbl_n.setStyleSheet("font-size: 12px; font-weight: 600; color: #cbd5e1;")
        self.txt_name = QLineEdit(name, self)
        self.txt_name.setPlaceholderText("e.g. DFFlagDisableDPIScale or DFIntCSGLevelOfDetailSwitchingDistance")
        self.txt_name.textChanged.connect(self._on_name_changed)
        layout.addWidget(lbl_n)
        layout.addWidget(self.txt_name)

        # Value Type
        lbl_t = QLabel("Value Type:", self)
        lbl_t.setStyleSheet("font-size: 12px; font-weight: 600; color: #cbd5e1;")
        self.combo_type = QComboBox(self)
        self.combo_type.addItems(["Boolean (True / False)", "Integer (Number)", "String (Text)"])
        self.combo_type.currentIndexChanged.connect(self._on_type_changed)
        layout.addWidget(lbl_t)
        layout.addWidget(self.combo_type)

        # Value Inputs Container
        self.input_container = QWidget(self)
        self.input_layout = QVBoxLayout(self.input_container)
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        self.input_layout.setSpacing(4)

        lbl_val = QLabel("Flag Value:", self.input_container)
        lbl_val.setStyleSheet("font-size: 12px; font-weight: 600; color: #cbd5e1;")
        self.input_layout.addWidget(lbl_val)

        # Boolean combo
        self.combo_bool = QComboBox(self.input_container)
        self.combo_bool.addItems(["True", "False"])
        self.input_layout.addWidget(self.combo_bool)

        # Text/Integer line edit
        self.txt_val = QLineEdit(self.input_container)
        self.txt_val.setPlaceholderText("Enter flag value")
        self.input_layout.addWidget(self.txt_val)

        layout.addWidget(self.input_container)

        # Set initial value state
        if isinstance(value, bool):
            self.combo_type.setCurrentIndex(0)
            self.combo_bool.setCurrentText("True" if value else "False")
        elif isinstance(value, int):
            self.combo_type.setCurrentIndex(1)
            self.txt_val.setText(str(value))
        elif value is not None:
            self.combo_type.setCurrentIndex(2)
            self.txt_val.setText(str(value))
        else:
            self.combo_type.setCurrentIndex(0)
            self.combo_bool.setCurrentText("True")

        self._update_input_visibility()

        layout.addSpacing(6)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        if not is_new:
            self.btn_del = QPushButton("Delete", self)
            self.btn_del.setObjectName("dangerButton")
            self.btn_del.clicked.connect(self._on_delete)
            btn_layout.addWidget(self.btn_del)

        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancel", self)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_save = QPushButton("Add Fast Flag" if is_new else "Save Changes", self)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0284c7, stop:1 #0369a1);
                color: #ffffff;
                font-weight: 700;
                border: 1px solid #38bdf8;
                border-radius: 8px;
                padding: 7px 18px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #38bdf8, stop:1 #0284c7);
                border: 1px solid #7dd3fc;
            }
        """)
        self.btn_save.clicked.connect(self._on_save)
        btn_layout.addWidget(self.btn_save)

        layout.addLayout(btn_layout)

    def _on_name_changed(self, text: str) -> None:
        t = text.strip()
        if t.startswith(("DFInt", "FInt")):
            self.combo_type.setCurrentIndex(1)
        elif t.startswith(("DFString", "FString")):
            self.combo_type.setCurrentIndex(2)
        elif t.startswith(("DFFlag", "FFlag")):
            self.combo_type.setCurrentIndex(0)

    def _on_type_changed(self, idx: int) -> None:
        self._update_input_visibility()

    def _update_input_visibility(self) -> None:
        idx = self.combo_type.currentIndex()
        if idx == 0:  # Boolean
            self.combo_bool.setVisible(True)
            self.txt_val.setVisible(False)
        else:  # Integer or String
            self.combo_bool.setVisible(False)
            self.txt_val.setVisible(True)
            if idx == 1:
                self.txt_val.setPlaceholderText("e.g. 60, 200, 0")
            else:
                self.txt_val.setPlaceholderText("e.g. Custom String Value")

    def _on_save(self) -> None:
        name = self.txt_name.text().strip()
        if not name:
            return
        self.saved_name = name
        idx = self.combo_type.currentIndex()
        if idx == 0:
            self.saved_value = self.combo_bool.currentText() == "True"
        elif idx == 1:
            raw = self.txt_val.text().strip()
            try:
                self.saved_value = int(raw)
            except ValueError:
                self.saved_value = 0
        else:
            self.saved_value = self.txt_val.text().strip()

        self.accept()

    def _on_delete(self) -> None:
        self.deleted = True
        self.accept()
