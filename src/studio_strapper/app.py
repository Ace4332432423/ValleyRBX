"""
Application initialization for ValleyRBX.
Supports both Direct Launch mode (with cinematic splash) and Management GUI mode.
"""

from __future__ import annotations
import argparse
from pathlib import Path
import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QFontDatabase, QIcon, QPalette
from PySide6.QtWidgets import QApplication

from studio_strapper.core.config import ConfigManager
from studio_strapper.core.studio_launcher import StudioLauncher
from studio_strapper.ui.main_window import MainWindow
from studio_strapper.ui.styles import THEME_QSS
from studio_strapper.ui.widgets.splash import CinematicSplash

ICON_PATH = "/home/ace/Downloads/2026_10_04_0jq_Kleki.png"


def create_app() -> QApplication:
    """Creates and configures the QApplication instance."""
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    app.setStyle("Fusion")  # Force Fusion so QSS fully controls all widgets incl. floating popups

    # Dark Fusion palette — ensures popup/dropdown windows use dark colors as base
    # (QSS on floating top-level widgets like QComboBox popups requires app-level palette)
    dark = QPalette()
    dark.setColor(QPalette.ColorRole.Window,          QColor(6,  13, 26))
    dark.setColor(QPalette.ColorRole.WindowText,      QColor(241, 245, 249))
    dark.setColor(QPalette.ColorRole.Base,            QColor(10, 22, 45))
    dark.setColor(QPalette.ColorRole.AlternateBase,   QColor(13, 26, 51))
    dark.setColor(QPalette.ColorRole.Text,            QColor(248, 250, 252))
    dark.setColor(QPalette.ColorRole.BrightText,      QColor(255, 255, 255))
    dark.setColor(QPalette.ColorRole.Button,          QColor(13, 29, 58))
    dark.setColor(QPalette.ColorRole.ButtonText,      QColor(241, 245, 249))
    dark.setColor(QPalette.ColorRole.Highlight,       QColor(2, 132, 199))
    dark.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    dark.setColor(QPalette.ColorRole.ToolTipBase,     QColor(10, 22, 45))
    dark.setColor(QPalette.ColorRole.ToolTipText,     QColor(248, 250, 252))
    dark.setColor(QPalette.ColorRole.Link,            QColor(56, 189, 248))
    app.setPalette(dark)

    # Apply QSS at app level so floating top-level widgets (combobox popups, menus) are themed
    app.setStyleSheet(THEME_QSS)

    app.setApplicationName("ValleyRBX")
    app.setOrganizationName("ValleyRBX")
    app.setApplicationDisplayName("ValleyRBX")

    if Path(ICON_PATH).exists():
        app.setWindowIcon(QIcon(ICON_PATH))

    # Load 2018 Roblox Source Sans font
    font_file = Path(__file__).resolve().parent / "resources" / "fonts" / "SourceSans3.ttf"
    if font_file.exists():
        QFontDatabase.addApplicationFont(str(font_file))

    # Font setup
    font = app.font()
    font.setFamily("Source Sans 3, Source Sans Pro, Segoe UI, Open Sans, sans-serif")
    font.setPointSize(10)
    app.setFont(font)

    return app


def launch_direct(app: QApplication, config_mgr: ConfigManager) -> int:
    """Launches Roblox Studio directly with a cinematic splash banner."""
    splash = CinematicSplash()
    splash.show()
    app.processEvents()

    launcher = StudioLauncher()

    prefix = Path(config_mgr.get("active_prefix"))
    runner = Path(config_mgr.get("runner_path"))
    renderer = config_mgr.get("renderer", "Vulkan")
    cef_mode = config_mgr.get("cef_mode", "disabled")
    env_vars = config_mgr.get("env_vars", {})
    fastflags = config_mgr.get("fastflags", {})
    use_gamescope = config_mgr.get("use_gamescope", False)
    gs_args = config_mgr.get("gamescope_args", "")

    discord_rpc = bool(config_mgr.get("discord_rpc", False))
    use_gamemode = bool(config_mgr.get("use_gamemode", True))
    debug_logs = bool(config_mgr.get("debug_logs", False))
    override_version = str(config_mgr.get("override_version", ""))
    override_channel = str(config_mgr.get("override_channel", ""))

    splash.set_status("Applying FastFlags & Web/CEF overrides...", 35)
    app.processEvents()

    splash.set_status("Initializing Kombucha Wine Sandbox...", 65)
    app.processEvents()

    def _on_exit(code: int):
        QTimer.singleShot(0, lambda: app.quit())

    splash.set_status("⚡ Igniting Roblox Studio...", 90)
    app.processEvents()

    ok = launcher.launch(
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
        on_exit=_on_exit,
    )

    # After launching, close splash after a brief pause so user sees confirmation
    QTimer.singleShot(1800, lambda: splash.close())

    if not ok:
        splash.set_status("❌ Launch failed. Exiting...", 100)
        QTimer.singleShot(2500, lambda: app.quit())

    return app.exec()


def main() -> int:
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="ValleyRBX - Cinematic Roblox Studio Runtime")
    parser.add_argument("--launch", "--direct-launch", action="store_true", help="Launch Roblox Studio directly using configured profile")
    parser.add_argument("--manage", action="store_true", help="Open the ValleyRBX configuration and management GUI")
    args, unknown = parser.parse_known_args()

    app = create_app()
    config_mgr = ConfigManager()

    if args.launch:
        return launch_direct(app, config_mgr)

    # Management / Bootstrapper mode
    window = MainWindow(config_mgr)
    window.show()
    return app.exec()
