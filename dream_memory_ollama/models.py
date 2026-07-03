"""
Dream Memory Zero-Data Overlay - Data Models
Simple data structures for the application.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Mark:
    """Represents a detected object mark."""
    label: str
    x: int  # Center X (0-1000 normalized)
    y: int  # Center Y (0-1000 normalized)
    bbox: dict  # {"x1": 0, "y1": 0, "x2": 1000, "y2": 1000}
    confidence: int  # 0-100


@dataclass
class AnalysisResult:
    """Result from vision analysis."""
    wave_id: str
    requests: List[str]
    marks: List[Mark]
    error: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "AnalysisResult":
        """Create from dictionary."""
        marks = []
        for m in data.get("marks", []):
            marks.append(Mark(
                label=m.get("label", ""),
                x=m.get("x", 500),
                y=m.get("y", 500),
                bbox=m.get("bbox", {"x1": 0, "y1": 0, "x2": 500, "y2": 500}),
                confidence=m.get("confidence", 0)
            ))

        return cls(
            wave_id=data.get("wave_id", ""),
            requests=data.get("requests", []),
            marks=marks,
            error=data.get("error")
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "wave_id": self.wave_id,
            "requests": self.requests,
            "marks": [
                {
                    "label": m.label,
                    "x": m.x,
                    "y": m.y,
                    "bbox": m.bbox,
                    "confidence": m.confidence
                }
                for m in self.marks
            ],
            "error": self.error
        }


@dataclass
class GameGeometry:
    """Game window geometry."""
    x: int
    y: int
    width: int
    height: int

    def to_tuple(self) -> tuple:
        """Convert to tuple (x, y, width, height)."""
        return (self.x, self.y, self.width, self.height)
