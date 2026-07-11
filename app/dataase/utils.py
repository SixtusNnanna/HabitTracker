from enum import Enum

class FrequencyType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    INTERVAL = "interval"


class MetricType(str, Enum):
    BOOLEAN = "boolean"
    DURATION = "duration"
    COUNT = "count"


class LogStatus(str, Enum):
    COMPLETED = "completed"
    SKIPPED = "skipped"
