"""
Desktop Battery Widget
A small, always-on-top, draggable overlay showing battery percentage.
"""

from PyQt6.QtCore import Qt, QPoint, QRectF, pyqtSignal
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QLinearGradient, QPen,
    QRadialGradient, QMouseEvent,
)
from PyQt6.QtWidgets import QWidget


def _color_for(percent: int) -> str:
    if percent < 50:
        return "#ef4444"
    elif percent <= 80:
        return "#f59e0b"
    else:
        return "#22c55e"


class DesktopWidget(QWidget):
    """Transparent, frameless battery widget for the desktop."""

    clicked = pyqtSignal()  # emitted when the widget is clicked
    SIZE = 120  # px

    def __init__(self, parent=None):
        super().__init__(parent)
        self._percent = 0
        self._charging = False
        self._drag_pos: QPoint | None = None
        self._moved = False  # Track if a drag occurred

        # Frameless + transparent + bottom (desktop level) + tool window (no taskbar)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnBottomHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(self.SIZE, self.SIZE)

        # Start in bottom-right of primary screen
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(geo.right() - self.SIZE - 24,
                      geo.bottom() - self.SIZE - 24)

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------
    def set_values(self, percent: int, charging: bool):
        self._percent = percent
        self._charging = charging
        self.update()

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        s = self.SIZE
        cx, cy = s / 2, s / 2
        r = s / 2 - 4

        # Background circle — semi-transparent dark
        bg_grad = QRadialGradient(cx, cy, r)
        bg_grad.setColorAt(0, QColor(15, 23, 42, 210))
        bg_grad.setColorAt(1, QColor(15, 23, 42, 180))
        p.setBrush(bg_grad)
        p.setPen(QPen(QColor(148, 163, 184, 40), 1.5))
        p.drawEllipse(4, 4, int(r * 2), int(r * 2))

        # Progress arc
        color = QColor(_color_for(self._percent))
        pen = QPen(color, 6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        arc_r = r - 8
        span = int(-360 * (self._percent / 100) * 16)
        p.drawArc(
            int(cx - arc_r), int(cy - arc_r),
            int(arc_r * 2), int(arc_r * 2),
            90 * 16, span,
        )

        # Percentage text
        p.setPen(QColor("#f8fafc"))
        font = QFont("Segoe UI", 26, QFont.Weight.Bold)
        p.setFont(font)
        p.drawText(self.rect().adjusted(0, -6, 0, 0),
                   Qt.AlignmentFlag.AlignCenter,
                   str(self._percent))

        # "%" subscript
        p.setPen(QColor("#94a3b8"))
        small = QFont("Segoe UI", 10)
        p.setFont(small)
        p.drawText(self.rect().adjusted(0, 30, 0, 0),
                   Qt.AlignmentFlag.AlignCenter, "%")

        # Charging indicator
        if self._charging:
            p.setPen(QColor("#fbbf24"))
            bolt = QFont("Segoe UI Emoji", 14)
            p.setFont(bolt)
            p.drawText(self.rect().adjusted(0, 52, 0, 0),
                       Qt.AlignmentFlag.AlignCenter, "⚡")

        p.end()

    # ------------------------------------------------------------------
    # Dragging and Clicking
    # ------------------------------------------------------------------
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.pos()
            self._moved = False
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            self._moved = True
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self._moved:
                self.clicked.emit()
        self._drag_pos = None
