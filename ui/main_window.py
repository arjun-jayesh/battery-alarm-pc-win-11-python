"""
Main Window UI Module
Modern Windows 11 styled battery monitoring interface with PyQt6.
"""

import os
import sys
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QColor, QPainter, QLinearGradient, QPen
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QFrame, QGraphicsDropShadowEffect,
    QMessageBox, QSizePolicy,
)


def _icon_path(name: str) -> str:
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "assets", name)


# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------

def _battery_color(percent: int) -> str:
    """Return a hex color based on battery percentage."""
    if percent < 50:
        return "#ef4444"   # red
    elif percent <= 80:
        return "#f59e0b"   # amber
    else:
        return "#22c55e"   # green


def _battery_gradient(percent: int) -> tuple[str, str]:
    if percent < 50:
        return "#ef4444", "#dc2626"
    elif percent <= 80:
        return "#fbbf24", "#f59e0b"
    else:
        return "#4ade80", "#22c55e"


# ---------------------------------------------------------------------------
# Stylesheet
# ---------------------------------------------------------------------------

WINDOW_STYLE = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #0f172a, stop:1 #1e293b);
}
"""

CARD_STYLE = """
QFrame#card {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(30,41,59,220), stop:1 rgba(15,23,42,240));
    border: 1px solid rgba(148,163,184,0.12);
    border-radius: 18px;
    padding: 24px;
}}
"""

SLIDER_STYLE = """
QSlider::groove:horizontal {{
    height: 8px;
    background: rgba(100,116,139,0.35);
    border-radius: 4px;
}}
QSlider::handle:horizontal {{
    background: {color};
    width: 22px;
    height: 22px;
    margin: -7px 0;
    border-radius: 11px;
    border: 2px solid rgba(255,255,255,0.2);
}}
QSlider::sub-page:horizontal {{
    background: {color};
    border-radius: 4px;
}}
"""

BUTTON_PRIMARY = """
QPushButton {{
    background: {bg};
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 28px;
    font-size: 14px;
    font-weight: 600;
}}
QPushButton:hover {{
    background: {hover};
}}
QPushButton:pressed {{
    background: {pressed};
}}
"""

BUTTON_OUTLINE = """
QPushButton {
    background: transparent;
    color: #94a3b8;
    border: 1px solid rgba(148,163,184,0.25);
    border-radius: 12px;
    padding: 12px 28px;
    font-size: 14px;
    font-weight: 500;
}
QPushButton:hover {
    background: rgba(148,163,184,0.08);
    color: #e2e8f0;
}
"""

TOGGLE_ON = """
QPushButton {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #22c55e, stop:1 #16a34a);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 10px 24px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton:hover { background: #16a34a; }
"""

TOGGLE_OFF = """
QPushButton {
    background: rgba(100,116,139,0.2);
    color: #94a3b8;
    border: 1px solid rgba(148,163,184,0.15);
    border-radius: 12px;
    padding: 10px 24px;
    font-size: 13px;
    font-weight: 500;
}
QPushButton:hover { background: rgba(100,116,139,0.35); color: #e2e8f0; }
"""


# ---------------------------------------------------------------------------
# Custom Battery Widget
# ---------------------------------------------------------------------------

class BatteryGauge(QWidget):
    """Custom-painted circular battery gauge."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._percent = 0
        self._charging = False
        self.setFixedSize(220, 220)

    def set_values(self, percent: int, charging: bool):
        self._percent = percent
        self._charging = charging
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        radius = min(w, h) / 2 - 16

        # Track (background arc)
        pen = QPen(QColor(100, 116, 139, 50))
        pen.setWidth(12)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(
            int(cx - radius), int(cy - radius),
            int(radius * 2), int(radius * 2),
            -225 * 16, -270 * 16,
        )

        # Value arc
        c1, c2 = _battery_gradient(self._percent)
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0, QColor(c1))
        grad.setColorAt(1, QColor(c2))
        pen2 = QPen(grad, 12)
        pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen2)
        span = int(-270 * (self._percent / 100) * 16)
        painter.drawArc(
            int(cx - radius), int(cy - radius),
            int(radius * 2), int(radius * 2),
            -225 * 16, span,
        )

        # Centre text
        painter.setPen(QColor("#f8fafc"))
        font = QFont("Segoe UI", 42, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(self.rect().adjusted(0, -10, 0, 0),
                         Qt.AlignmentFlag.AlignCenter,
                         f"{self._percent}")

        # "%" subscript
        small = QFont("Segoe UI", 16, QFont.Weight.Normal)
        painter.setFont(small)
        painter.setPen(QColor("#94a3b8"))
        painter.drawText(self.rect().adjusted(0, 44, 0, 0),
                         Qt.AlignmentFlag.AlignCenter, "%")

        painter.end()


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    """The primary application window."""

    startup_changed = pyqtSignal(bool)  # emitted when startup toggle changes

    def __init__(self, alarm_manager, battery_monitor, config, save_fn,
                 parent=None):
        super().__init__(parent)
        self._alarm = alarm_manager
        self._monitor = battery_monitor
        self._config = config
        self._save_config = save_fn

        self.setWindowTitle("Battery Alarm")
        self.setFixedSize(460, 620)
        self.setStyleSheet(WINDOW_STYLE)

        icon_file = _icon_path("icon.png")
        if os.path.exists(icon_file):
            self.setWindowIcon(QIcon(icon_file))

        # Pre-initialise so _persist() doesn't crash when slider fires
        self._alarm_enabled = config.get("alarm_enabled", True)
        self._startup_enabled = config.get("start_on_startup", False)

        self._build_ui()
        self._apply_config()

        # Connections
        self._alarm.alarm_triggered.connect(self._on_alarm)
        self._alarm.alarm_stopped.connect(self._on_alarm_stopped)

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 28, 24, 24)
        root.setSpacing(0)

        # Header
        header = QLabel("Battery Alarm")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header.setStyleSheet("color: #f8fafc;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(header)

        tagline = QLabel("Charge smart. Battery lasts longer.")
        tagline.setFont(QFont("Segoe UI", 11))
        tagline.setStyleSheet("color: #64748b; margin-bottom: 8px;")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(tagline)

        root.addSpacing(12)

        # Card
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(CARD_STYLE.format())
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 80))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 12, 0, 12)
        card_layout.setSpacing(8)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Battery gauge
        self._gauge = BatteryGauge()
        card_layout.addWidget(self._gauge, alignment=Qt.AlignmentFlag.AlignCenter)

        # Charging status
        self._status_label = QLabel("Checking…")
        self._status_label.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        self._status_label.setStyleSheet("color: #94a3b8;")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self._status_label)

        root.addWidget(card)
        root.addSpacing(20)

        # Target selector
        target_header = QLabel("Alarm Target")
        target_header.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        target_header.setStyleSheet("color: #cbd5e1;")
        root.addWidget(target_header)
        root.addSpacing(6)

        slider_row = QHBoxLayout()
        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(50, 100)
        self._slider.setSingleStep(5)
        self._slider.setPageStep(10)
        self._slider.setTickInterval(10)
        self._slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._slider.setStyleSheet(SLIDER_STYLE.format(color="#3b82f6"))
        self._slider.valueChanged.connect(self._on_target_changed)
        slider_row.addWidget(self._slider)

        self._target_label = QLabel("80 %")
        self._target_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self._target_label.setStyleSheet("color: #f8fafc; min-width: 52px;")
        self._target_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        slider_row.addWidget(self._target_label)
        root.addLayout(slider_row)

        root.addSpacing(18)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self._toggle_btn = QPushButton("Alarm ON")
        self._toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_btn.clicked.connect(self._toggle_alarm)
        btn_row.addWidget(self._toggle_btn)

        self._stop_btn = QPushButton("Stop Alarm")
        self._stop_btn.setStyleSheet(
            BUTTON_PRIMARY.format(bg="#ef4444", hover="#dc2626", pressed="#b91c1c"))
        self._stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._stop_btn.clicked.connect(self._alarm.stop)
        self._stop_btn.setVisible(False)
        btn_row.addWidget(self._stop_btn)

        self._snooze_btn = QPushButton("Snooze 5 min")
        self._snooze_btn.setStyleSheet(BUTTON_OUTLINE)
        self._snooze_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._snooze_btn.clicked.connect(self._alarm.snooze)
        self._snooze_btn.setVisible(False)
        btn_row.addWidget(self._snooze_btn)

        root.addLayout(btn_row)
        root.addSpacing(14)

        # Startup toggle row
        startup_row = QHBoxLayout()
        startup_row.setSpacing(12)

        startup_label = QLabel("Run on Startup")
        startup_label.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        startup_label.setStyleSheet("color: #cbd5e1;")
        startup_row.addWidget(startup_label)
        startup_row.addStretch()

        self._startup_btn = QPushButton("OFF")
        self._startup_btn.setFixedWidth(80)
        self._startup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._startup_btn.clicked.connect(self._toggle_startup)
        startup_row.addWidget(self._startup_btn)

        root.addLayout(startup_row)
        root.addStretch()

    # ------------------------------------------------------------------
    # Config helpers
    # ------------------------------------------------------------------
    def _apply_config(self):
        target = self._config.get("target_percent", 80)
        enabled = self._config.get("alarm_enabled", True)
        startup = self._config.get("start_on_startup", False)
        
        self._slider.blockSignals(True)
        self._slider.setValue(target)
        self._slider.blockSignals(False)
        
        self._target_label.setText(f"{target} %")
        self._alarm_enabled = enabled
        self._startup_enabled = startup
        self._update_toggle_style()
        self._update_startup_style()

    def _persist(self):
        self._config["target_percent"] = self._slider.value()
        self._config["alarm_enabled"] = self._alarm_enabled
        self._config["start_on_startup"] = self._startup_enabled
        self._save_config(self._config)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------
    def update_battery(self, percent: int, charging: bool):
        """Called by the monitor signal."""
        self._gauge.set_values(percent, charging)

        if charging:
            self._status_label.setText("⚡  Charging")
            self._status_label.setStyleSheet(
                f"color: {_battery_color(percent)}; font-size: 14px;")
        else:
            self._status_label.setText("🔋  On Battery")
            self._status_label.setStyleSheet("color: #94a3b8; font-size: 14px;")

    def _on_target_changed(self, value: int):
        self._target_label.setText(f"{value} %")
        self._alarm.reset()
        self._persist()

    def _toggle_alarm(self):
        self._alarm_enabled = not self._alarm_enabled
        self._update_toggle_style()
        if not self._alarm_enabled:
            self._alarm.reset()
        self._persist()

    @property
    def alarm_enabled(self) -> bool:
        return self._alarm_enabled

    @property
    def target_percent(self) -> int:
        return self._slider.value()

    def _update_toggle_style(self):
        if self._alarm_enabled:
            self._toggle_btn.setText("Alarm ON")
            self._toggle_btn.setStyleSheet(TOGGLE_ON)
        else:
            self._toggle_btn.setText("Alarm OFF")
            self._toggle_btn.setStyleSheet(TOGGLE_OFF)

    def _toggle_startup(self):
        self._startup_enabled = not self._startup_enabled
        self._update_startup_style()
        self._persist()
        self.startup_changed.emit(self._startup_enabled)

    def _update_startup_style(self):
        if self._startup_enabled:
            self._startup_btn.setText("ON")
            self._startup_btn.setStyleSheet(TOGGLE_ON)
        else:
            self._startup_btn.setText("OFF")
            self._startup_btn.setStyleSheet(TOGGLE_OFF)

    @property
    def startup_enabled(self) -> bool:
        return self._startup_enabled

    def _on_alarm(self):
        self._stop_btn.setVisible(True)
        self._snooze_btn.setVisible(True)
        # Bring to front
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _on_alarm_stopped(self):
        self._stop_btn.setVisible(False)
        self._snooze_btn.setVisible(False)

    # ------------------------------------------------------------------
    # Overrides
    # ------------------------------------------------------------------
    def closeEvent(self, event):
        """Minimize to tray instead of closing."""
        event.ignore()
        self.hide()
