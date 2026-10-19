"""
Cinematic Navy Blue & Sapphire Theme for ValleyRBX.
Classic 2018 Roblox typography (Source Sans Pro / Source Sans 3),
frosted glass cards, deep navy gradients, and clear high-contrast controls.
"""

THEME_QSS = """
/* Base Window & Global Typography (2018 Roblox Source Sans) */
QMainWindow, QDialog, QWidget {
    background-color: #060d1a;
    color: #f1f5f9;
    font-family: "Source Sans 3", "Source Sans Pro", "Segoe UI", "Open Sans", sans-serif;
    font-size: 13px;
    letter-spacing: 0.2px;
}

/* Dialogs & Input Prompts */
QDialog, QMessageBox, QInputDialog {
    background-color: #0a162d;
    color: #f8fafc;
    border: 1px solid rgba(56, 189, 248, 0.4);
    border-radius: 14px;
}

QDialog QLabel, QMessageBox QLabel, QInputDialog QLabel {
    color: #f8fafc;
    font-size: 13px;
}

/* Scroll Area & Viewport */
QScrollArea {
    background: transparent;
    border: none;
}

QScrollArea > QWidget > QWidget {
    background: transparent;
}

/* Action Buttons */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(20, 42, 82, 0.9), stop:1 rgba(11, 24, 48, 0.95));
    color: #f1f5f9;
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 8px;
    padding: 7px 15px;
    font-weight: 600;
    font-size: 12px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(30, 64, 122, 0.95), stop:1 rgba(16, 36, 72, 0.98));
    border: 1px solid rgba(56, 189, 248, 0.7);
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #08142b;
}

QPushButton:disabled {
    background-color: #070e1c;
    color: #475569;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

#dangerButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #dc2626, stop:1 #b91c1c);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    font-weight: 600;
    padding: 7px 14px;
}

#dangerButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ef4444, stop:1 #dc2626);
}

/* Inputs & Text Fields */
QLineEdit, QSpinBox {
    background-color: #0b1832;
    color: #f8fafc;
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 8px;
    padding: 7px 12px;
    selection-background-color: #0284c7;
    selection-color: #ffffff;
    font-size: 12px;
}

QLineEdit:focus, QSpinBox:focus {
    border: 1px solid #38bdf8;
    background-color: #0e2042;
}

/* QComboBox Styling */
QComboBox {
    background-color: #0d1d3a;
    color: #f8fafc;
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 8px;
    padding: 7px 14px;
    font-size: 12px;
    font-weight: 600;
}

QComboBox:hover {
    background-color: #122850;
    border: 1px solid rgba(56, 189, 248, 0.65);
}

QComboBox:on {
    background-color: #122850;
    border: 1px solid #38bdf8;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border: none;
}

/* The Popup List View */
QComboBox QAbstractItemView {
    background-color: #0a162d;
    color: #f8fafc;
    border: 1px solid rgba(56, 189, 248, 0.5);
    border-radius: 0px;
    padding: 4px;
    outline: none;
    selection-background-color: #0284c7;
    selection-color: #ffffff;
    alternate-background-color: #0d1a33;
}

QComboBox QAbstractItemView::item {
    background-color: #0a162d;
    color: #f8fafc;
    min-height: 28px;
    padding: 4px 10px;
    border-radius: 0px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: rgba(56, 189, 248, 0.22);
    color: #ffffff;
}

QComboBox QAbstractItemView::item:selected {
    background-color: #0284c7;
    color: #ffffff;
    font-weight: 700;
}

/* Clean Tables */
QTableWidget {
    background-color: #091326;
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 10px;
    gridline-color: rgba(56, 189, 248, 0.1);
    color: #e2e8f0;
    selection-background-color: rgba(2, 132, 199, 0.35);
    selection-color: #ffffff;
}

QHeaderView::section {
    background-color: #0d1a33;
    color: #38bdf8;
    padding: 8px;
    font-weight: 700;
    letter-spacing: 0.5px;
    border: none;
    border-bottom: 1px solid rgba(56, 189, 248, 0.25);
}

/* Scrollbars */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
    border-radius: 3px;
}

QScrollBar::handle:vertical {
    background: rgba(56, 189, 248, 0.35);
    min-height: 24px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(56, 189, 248, 0.7);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Menus */
QMenu {
    background-color: #0a162d;
    color: #f1f5f9;
    border: 1px solid rgba(56, 189, 248, 0.45);
    border-radius: 12px;
    padding: 6px;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 6px;
    font-size: 13px;
}

QMenu::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(2, 132, 199, 0.5), stop:1 rgba(37, 99, 235, 0.5));
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background: rgba(255, 255, 255, 0.08);
    margin: 4px 6px;
}

/* Terminal Console */
QPlainTextEdit, QTextEdit {
    background-color: #050b16;
    color: #38bdf8;
    font-family: "JetBrains Mono", "Cascadia Code", "Fira Code", monospace;
    font-size: 12px;
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 10px;
    padding: 10px;
}

/* Badges */
.BadgeOk {
    background-color: rgba(34, 197, 94, 0.12);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.35);
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 700;
}

.BadgeWarn {
    background-color: rgba(245, 158, 11, 0.12);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.35);
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 700;
}

.BadgeError {
    background-color: rgba(239, 68, 68, 0.12);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.35);
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 700;
}

.BadgeInfo {
    background-color: rgba(56, 189, 248, 0.12);
    color: #38bdf8;
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 700;
}
"""
