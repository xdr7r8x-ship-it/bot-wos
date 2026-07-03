"""
Dream Memory Zero-Data Overlay - Overlay Window
Transparent click-through overlay for displaying object markers.
"""

from typing import List, Optional

from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics
from PyQt6.QtWidgets import QWidget

from config import (
    OVERLAY_CIRCLE_RADIUS,
    OVERLAY_CIRCLE_COLOR,
    OVERLAY_TEXT_COLOR,
    OVERLAY_FONT_SIZE,
    OVERLAY_LINE_WIDTH,
    STATUS_LIVE,
    STATUS_ANALYZING,
    STATUS_NO_MARKS,
    STATUS_API_ERROR,
    STATUS_WAITING,
    STATUS_STALE,
    STATUS_STOPPED
)


class TransparentOverlay(QWidget):
    """
    Transparent, click-through, always-on-top overlay window.
    Draws circles and labels at specified coordinates.
    """

    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__()

        self.overlay_x = x
        self.overlay_y = y
        self.overlay_width = width
        self.overlay_height = height
        self.marks: List[dict] = []
        self.status = STATUS_WAITING
        self.visible = True

        # Calculate overlay position (fullscreen on primary monitor)
        self._setup_window()

        # Timer for status updates
        self._status_timer = QTimer(self)
        self._status_timer.timeout.connect(self._clear_temp_status)

        # Colors
        self.circle_color = QColor(*OVERLAY_CIRCLE_COLOR)
        self.text_color = QColor(*OVERLAY_TEXT_COLOR)

        # Font
        self.font = QFont("Segoe UI", OVERLAY_FONT_SIZE, QFont.Weight.Bold)
        self.status_font = QFont("Segoe UI", 14, QFont.Weight.Bold)

    def _setup_window(self):
        """Configure the overlay window properties."""
        # Set window flags for transparent overlay
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )

        # Set transparency attributes
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Set window geometry to cover entire screen
        self.setGeometry(0, 0, self.overlay_width, self.overlay_height)

        # Make it non-interactive
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.activateWindow()

    def move_to(self, x: int, y: int, width: int, height: int):
        """Move overlay to new position."""
        self.overlay_x = x
        self.overlay_y = y
        self.overlay_width = width
        self.overlay_height = height
        self.setGeometry(0, 0, width, height)
        self.update()

    def paintEvent(self, event):
        """Draw the overlay content: circles, labels, and status."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw all marks
        for idx, mark in enumerate(self.marks):
            self._draw_mark(painter, mark, idx + 1)

        # Draw status in top-left corner
        self._draw_status(painter)

    def _draw_mark(self, painter: QPainter, mark: dict, index: int):
        """Draw a single mark (circle + label)."""
        # Convert normalized coordinates to screen pixels
        # bbox coordinates are 0-1000 relative to scene crop
        bbox = mark.get("bbox", {"x1": 0, "y1": 0, "x2": 500, "y2": 500})
        
        # Calculate center from bbox
        x1 = bbox.get("x1", 0)
        y1 = bbox.get("y1", 0)
        x2 = bbox.get("x2", 500)
        y2 = bbox.get("y2", 500)
        
        # Center of bbox
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        # Scale to overlay size
        x = int((cx / 1000) * self.overlay_width)
        y = int((cy / 1000) * self.overlay_height)

        radius = OVERLAY_CIRCLE_RADIUS

        # Draw outer glow
        glow_color = QColor(self.circle_color)
        glow_color.setAlpha(50)
        glow_pen = QPen(glow_color, OVERLAY_LINE_WIDTH + 4)
        painter.setPen(glow_pen)
        painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)

        # Draw main circle
        pen = QPen(self.circle_color, OVERLAY_LINE_WIDTH)
        painter.setPen(pen)
        painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)

        # Draw fill
        fill_color = QColor(self.circle_color)
        fill_color.setAlpha(40)
        painter.setBrush(fill_color)
        painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)

        # Draw index number
        painter.setFont(self.font)
        painter.setPen(self.text_color)
        painter.drawText(x - radius, y - radius - 5, radius * 2, radius, 
                         Qt.AlignmentFlag.AlignCenter, str(index))

        # Draw label below circle
        label = mark.get("label", "")
        if len(label) > 15:
            label = label[:12] + "..."

        metrics = QFontMetrics(self.font)
        label_width = metrics.horizontalAdvance(label)
        label_x = x - label_width // 2
        label_y = y + radius + 18

        # Draw label background
        bg_color = QColor(0, 0, 0, 180)
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(label_x - 4, label_y - 14, label_width + 8, 18)

        # Draw label text
        painter.setPen(self.text_color)
        painter.drawText(label_x, label_y, label)

        # Draw confidence if available
        confidence = mark.get("confidence", 0)
        if confidence > 0:
            conf_text = f"{confidence}%"
            conf_metrics = QFontMetrics(self.font)
            conf_x = x - conf_metrics.horizontalAdvance(conf_text) // 2
            conf_y = y - radius - 18
            painter.drawText(conf_x, conf_y, conf_text)

    def _draw_status(self, painter: QPainter):
        """Draw status indicator in top-left corner."""
        status_text = self.status
        if not self.visible:
            status_text = "HIDDEN"

        # Status background
        painter.setFont(self.status_font)
        metrics = QFontMetrics(self.status_font)
        text_width = metrics.horizontalAdvance(status_text)
        text_height = metrics.height()

        bg_x = 10
        bg_y = 10
        bg_w = text_width + 20
        bg_h = text_height + 12

        # Color based on status
        if self.status == STATUS_LIVE:
            bg_color = QColor(0, 180, 0, 200)
        elif self.status == STATUS_ANALYZING:
            bg_color = QColor(200, 180, 0, 200)
        elif self.status in [STATUS_API_ERROR, STATUS_PARSE_ERROR]:
            bg_color = QColor(200, 50, 50, 200)
        elif self.status == STATUS_STALE:
            bg_color = QColor(150, 100, 0, 200)
        elif self.status == STATUS_WAITING:
            bg_color = QColor(100, 100, 100, 200)
        else:
            bg_color = QColor(80, 80, 80, 200)

        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(bg_x, bg_y, bg_w, bg_h, 5, 5)

        # Draw status text
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(bg_x + 10, bg_y + text_height - 2, status_text)

    def update_marks(self, marks: List[dict]):
        """Update displayed marks and redraw."""
        self.marks = marks
        if self.visible:
            self.update()

    def update_status(self, status: str):
        """Update status indicator."""
        self.status = status
        if self.visible:
            self.update()

    def toggle_visibility(self):
        """Toggle overlay visibility."""
        self.visible = not self.visible
        if self.visible:
            self.show()
            self.activateWindow()
        else:
            self.hide()
        return self.visible

    def show_overlay(self):
        """Show the overlay."""
        self.visible = True
        self.show()
        self.activateWindow()
        self.update()

    def hide_overlay(self):
        """Hide the overlay."""
        self.visible = False
        self.hide()

    def _clear_temp_status(self):
        """Clear temporary status (like ANALYZING) back to LIVE."""
        if self.status == STATUS_ANALYZING:
            self.status = STATUS_LIVE
            self.update()

    def is_visible(self) -> bool:
        """Check if overlay is visible."""
        return self.visible


class OverlayManager:
    """Manages the overlay lifecycle."""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.overlay: Optional[TransparentOverlay] = None
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def create_overlay(self) -> TransparentOverlay:
        """Create the overlay window."""
        self.overlay = TransparentOverlay(self.x, self.y, self.width, self.height)
        return self.overlay

    def get_overlay(self) -> Optional[TransparentOverlay]:
        """Get the overlay instance."""
        return self.overlay

    def move_overlay(self, x: int, y: int, width: int, height: int):
        """Move overlay to new position."""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        if self.overlay:
            self.overlay.move_to(x, y, width, height)

    def update_marks(self, marks: List[dict]):
        """Update marks on the overlay."""
        if self.overlay:
            self.overlay.update_marks(marks)

    def update_status(self, status: str):
        """Update status on the overlay."""
        if self.overlay:
            self.overlay.update_status(status)

    def toggle_overlay(self) -> bool:
        """Toggle overlay visibility. Returns new state."""
        if self.overlay:
            return self.overlay.toggle_visibility()
        return False

    def show(self):
        """Show the overlay."""
        if self.overlay:
            self.overlay.show_overlay()

    def hide(self):
        """Hide the overlay."""
        if self.overlay:
            self.overlay.hide_overlay()

    def close(self):
        """Close the overlay."""
        if self.overlay:
            self.overlay.close()
            self.overlay = None
