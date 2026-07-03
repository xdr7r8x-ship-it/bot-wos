# Data models for Dream Memory
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class DetectedObject:
    """Detected game object."""
    name: str
    x: int  # relative 0-1000
    y: int  # relative 0-1000
    confidence: int  # 0-100


@dataclass
class AnalysisResult:
    """Result from AI analysis."""
    success: bool
    objects: List[DetectedObject]
    error: Optional[str] = None
    wave_id: Optional[int] = None
    timestamp: float = 0
