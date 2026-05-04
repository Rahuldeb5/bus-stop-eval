from dataclasses import dataclass
from enum import Enum

@dataclass
class Location:
    lat: float
    lng: float

class Importance(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class CriterionResult:
    criterion: str
    passed: bool | None = None
    importance: Importance | None = None
    notes: str | None = None
