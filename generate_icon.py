"""
Generate a simple app icon (PNG) for tray and taskbar.
"""
import os
import math
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import (
    QImage, QPainter, QLinearGradient, QColor, QFont, QPen,
    QRadialGradient,
)
from PyQt6.QtWidgets import QApplication
import sys


def generate_icon(path: str, size: int = 256):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Need a QApplication for QPainter on QImage
    _app = QApplication.instance() or QApplication(sys.argv)

    img = QImage(size, size, QImage.Format.Format_ARGB32)
    img.fill(QColor(0, 0, 0, 0))

    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Background gradient circle
    grad = QRadialGradient(size / 2, size / 2, size / 2)
    grad.setColorAt(0, QColor("#22c55e"))
    grad.setColorAt(1, QColor("#15803d"))
    p.setBrush(grad)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(8, 8, size - 16, size - 16)

    # Inner subtle shadow
    inner = QRadialGradient(size / 2, size * 0.38, size * 0.45)
    inner.setColorAt(0, QColor(255, 255, 255, 30))
    inner.setColorAt(1, QColor(0, 0, 0, 0))
    p.setBrush(inner)
    p.drawEllipse(8, 8, size - 16, size - 16)

    # Lightning bolt ⚡
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("white"))
    font = QFont("Segoe UI Emoji", int(size * 0.42), QFont.Weight.Bold)
    p.setFont(font)
    p.setPen(QColor("white"))
    p.drawText(QRect(0, -int(size * 0.02), size, size),
               Qt.AlignmentFlag.AlignCenter, "⚡")

    p.end()
    img.save(path, "PNG")


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "assets", "icon.png")
    generate_icon(out)
    print(f"Generated → {out}")
