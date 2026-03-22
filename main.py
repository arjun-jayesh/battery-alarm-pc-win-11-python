"""
Battery Alarm — Main Entry Point
Initialises Qt application, system tray, desktop widget, and wires all components.
"""

import sys
import os
import ctypes

from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QIcon, QAction, QFont, QColor, QPixmap, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QMessageBox,
)

from core.battery_monitor import BatteryMonitor
from core.alarm_manager import AlarmManager
from core.config_manager import load_config, save_config
from core.startup_manager import set_startup, create_desktop_shortcut
from ui.main_window import MainWindow
from ui.desktop_widget import DesktopWidget


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _asset_path(name: str) -> str:
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "assets", name)


def _make_tray_icon(percent: int, charging: bool) -> QIcon:
    """Dynamically paint a tiny tray icon showing battery percent."""
    size = 64
    pix = QPixmap(size, size)
    pix.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Background circle
    if percent < 50:
        bg = QColor("#ef4444")
    elif percent <= 80:
        bg = QColor("#f59e0b")
    else:
        bg = QColor("#22c55e")

    painter.setBrush(bg)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, size - 4, size - 4)

    # Text
    painter.setPen(QColor("white"))
    font = QFont("Segoe UI", 22 if percent < 100 else 18, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, str(percent))

    # Charging indicator — small lightning bolt dot
    if charging:
        painter.setBrush(QColor("white"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(size - 18, 0, 16, 16)
        painter.setPen(QColor(bg))
        bolt_font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        painter.setFont(bolt_font)
        painter.drawText(QRect(size - 18, 0, 16, 16),
                         Qt.AlignmentFlag.AlignCenter, "⚡")

    painter.end()
    return QIcon(pix)


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

class BatteryAlarmApp:
    """Wires together monitor, alarm, window, widget, and system tray."""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # Windows taskbar icon grouping
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "batteryalarm.v1"
            )
        except Exception:
            pass

        # Config
        self.config = load_config()

        # Core objects
        self.monitor = BatteryMonitor()
        self.alarm = AlarmManager()

        # Window
        self.window = MainWindow(
            self.alarm, self.monitor, self.config, save_config
        )

        # Desktop widget
        self.widget = DesktopWidget()

        # System tray
        self._setup_tray()

        # Connections
        self.monitor.battery_updated.connect(self._on_battery_update)
        self.monitor.battery_not_found.connect(self._on_no_battery)
        self.alarm.alarm_triggered.connect(self._on_alarm_triggered)
        self.window.startup_changed.connect(self._on_startup_changed)
        self.widget.clicked.connect(self._show_window)

        # Apply startup config on launch
        set_startup(self.config.get("start_on_startup", False))

        # Create desktop shortcut on first run
        create_desktop_shortcut()

    # ------------------------------------------------------------------
    # Tray
    # ------------------------------------------------------------------
    def _setup_tray(self):
        icon_path = _asset_path("icon.png")
        fallback_icon = QIcon(icon_path) if os.path.exists(icon_path) \
            else _make_tray_icon(0, False)

        self.tray = QSystemTrayIcon(fallback_icon, self.app)
        self.tray.setToolTip("Battery Alarm — starting…")

        menu = QMenu()

        self._open_action = QAction("Open Battery Alarm")
        self._open_action.triggered.connect(self._show_window)
        menu.addAction(self._open_action)

        menu.addSeparator()

        self._alarm_toggle_action = QAction("Disable Alarm")
        self._alarm_toggle_action.triggered.connect(self._tray_toggle_alarm)
        menu.addAction(self._alarm_toggle_action)

        menu.addSeparator()

        self._widget_toggle_action = QAction("Hide Widget")
        self._widget_toggle_action.triggered.connect(self._toggle_widget)
        menu.addAction(self._widget_toggle_action)

        menu.addSeparator()

        exit_action = QAction("Exit")
        exit_action.triggered.connect(self._quit)
        menu.addAction(exit_action)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------
    def _on_battery_update(self, percent: int, charging: bool):
        # Update window & widget
        self.window.update_battery(percent, charging)
        self.widget.set_values(percent, charging)

        # Update tray
        self.tray.setIcon(_make_tray_icon(percent, charging))
        status = "Charging" if charging else "On Battery"
        self.tray.setToolTip(f"Battery Alarm  —  {percent}%  {status}")

        # Update tray menu labels
        if self.window.alarm_enabled:
            self._alarm_toggle_action.setText("Disable Alarm")
        else:
            self._alarm_toggle_action.setText("Enable Alarm")

        self._widget_toggle_action.setText(
            "Hide Widget" if self.widget.isVisible() else "Show Widget"
        )

        # Auto-stop alarm when charger is unplugged
        if not charging and self.alarm.is_ringing:
            self.alarm.stop()

        # Check alarm
        self.alarm.check_and_trigger(
            percent, charging,
            self.window.target_percent,
            self.window.alarm_enabled,
        )

    def _on_alarm_triggered(self):
        self.tray.showMessage(
            "Battery Alarm ⚡",
            f"Battery has reached {self.window.target_percent}%!",
            QSystemTrayIcon.MessageIcon.Warning,
            5000,
        )

    def _on_no_battery(self):
        QMessageBox.critical(
            None,
            "Battery Alarm",
            "No battery detected on this system.\n"
            "The application will exit.",
        )
        self._quit()

    def _on_startup_changed(self, enabled: bool):
        set_startup(enabled)

    def _show_window(self):
        self.window.showNormal()
        self.window.activateWindow()
        self.window.raise_()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()

    def _tray_toggle_alarm(self):
        self.window._toggle_alarm()

    def _toggle_widget(self):
        if self.widget.isVisible():
            self.widget.hide()
            self._widget_toggle_action.setText("Show Widget")
        else:
            self.widget.show()
            self._widget_toggle_action.setText("Hide Widget")

    def _quit(self):
        self.monitor.stop()
        self.alarm.stop()
        self.tray.hide()
        self.app.quit()

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------
    def run(self) -> int:
        if not self.monitor.start():
            return 1
        self.window.show()
        self.widget.show()
        return self.app.exec()


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------

def main():
    app = BatteryAlarmApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
