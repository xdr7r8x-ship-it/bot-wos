# Transparent overlay for Dream Memory
from typing import List
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor, QFont
from PyQt6.QtWidgets import QWidget

import config
from models import DetectedObject


class TransparentOverlay(QWidget):
    """Transparent, click-through overlay window."""

    def __init__(self, x: int = 0, y: int = 0, width: int = 800, height: int = 600):
        super().__init__()

        # Store geometry
        self.overlay_x = x
        self.overlay_y = y
        self.overlay_width = width
        self.overlay_height = height

        # State
        self.marks: List[DetectedObject] = []
        self.status = config.STATUS_WAITING
        self.visible = True

        # Window setup
        self._setup_window()

        # Timer for status
        self._status_timer = QTimer(self)
        self._status_timer.timeout.connect(self._clear_temp_status)

    def _setup_window(self):
        """Setup overlay window properties."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        # Set geometry at real position
        self.move_to(self.overlay_x, self.overlay_y, self.overlay_width, self.overlay_height)

    def move_to(self, x: int, y: int, width: int, height: int):
        """Move and resize overlay to position."""
        self.overlay_x = x
        self.overlay_y = y
        self.overlay_width = width
        self.overlay_height = height
        self.setGeometry(x, y, width, height)

    def update_geometry(self, x: int, y: int, width: int, height: int):
        """Update overlay geometry."""
        self.move_to(x, y, width, height)

    def update_marks(self, marks: List[DetectedObject]):
        """Update displayed marks."""
        self.marks = marks
        self.update()

    def update_status(self, status: str):
        """Update status text."""
        self.status = status
        self.update()

    def set_temp_status(self, status: str, duration_ms: int = 3000):
        """Show temporary status."""
        self.status = status
        self.update()
        self._status_timer.start(duration_ms)

    def _clear_temp_status(self):
        """Clear temporary status."""
        self._status_timer.stop()
        if self.status in [config.STATUS_ANALYZING, config.STATUS_API_ERROR]:
            self.status = config.STATUS_LIVE
        self.update()

    def show_overlay(self):
        """Show overlay."""
        self.show()
        self.visible = True

    def hide_overlay(self):
        """Hide overlay."""
        self.hide()
        self.visible = False

    def toggle_overlay(self):
        """Toggle overlay visibility."""
        if self.visible:
            self.hide_overlay()
        else:
            self.show_overlay()

    def paintEvent(self, event):
        """Draw overlay."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate scene height (TOP part, above request bar)
        scene_height = int(self.overlay_height * (1 - config.REQUEST_BAR_HEIGHT_RATIO))

        # Draw semi-transparent background
        painter.fillRect(self.rect(), QColor(0, 0, 0, 15))

        # Draw marks
        for i, mark in enumerate(self.marks):
            # Convert relative coordinates (0-1000) to screen pixels
            # Coordinates are relative to scene only (NOT including request bar)
            x = int((mark.x / 1000) * self.overlay_width)
            y = int((mark.y / 1000) * scene_height)

            # Color based on confidence
            if mark.confidence >= 80:
                color = QColor(0, 255, 0)  # Green
            elif mark.confidence >= 60:
                color = QColor(255, 255, 0)  # Yellow
            else:
                color = QColor(255, 100, 100)  # Red/Pink

            # Draw circle
            pen = QPen(color, 3)
            painter.setPen(pen)
            painter.drawEllipse(x - 15, y - 15, 30, 30)

            # Draw label
            font = QFont("Arial", 11, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QPen(QColor(255, 255, 255)))
            text = f"{i + 1}. {mark.name}"
            painter.drawText(x + 20, y + 5, text)

        # Draw status bar
        self._draw_status(painter)

    def _draw_status(self, painter):
        """Draw status information."""
        # Background
        painter.fillRect(5, 5, 280, 80, QColor(0, 0, 0, 180))

        # Status text
        font = QFont("Consolas", 12, QFont.Weight.Bold)
        painter.setFont(font)

        if self.status == config.STATUS_LIVE:
            color = QColor(0, 255, 0)
        elif self.status == config.STATUS_ANALYZING:
            color = QColor(255, 255, 0)
        elif self.status in [config.STATUS_API_ERROR, config.STATUS_NO_MARKS]:
            color = QColor(255, 100, 100)
        else:
            color = QColor(200, 200, 200)

        painter.setPen(QPen(color))
        painter.drawText(15, 28, f"STATUS: {self.status}")

        # Objects count
        font2 = QFont("Consolas", 11)
        painter.setFont(font2)
        painter.setPen(QPen(QColor(200, 200, 200)))
        painter.drawText(15, 50, f"OBJECTS: {len(self.marks)}")

        # Controls
        font3 = QFont("Consolas", 9)
        painter.setFont(font3)
        painter.setPen(QPen(QColor(150, 150, 150)))
        painter.drawText(15, 70, "F8:Toggle F10:Analyze ESC:Exit")
