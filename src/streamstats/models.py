from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# Определение набора именованных констант,
# описывающих уровень события
class Level(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

# Определение модели события
@dataclass
class Event:
    timestamp: datetime
    level: Level
    source: str
    message: str
