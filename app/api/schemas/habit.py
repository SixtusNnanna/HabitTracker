from datetime import datetime
from pydantic import BaseModel
from app.database.utils import FrequencyType, MetricType


class HabitBase(BaseModel):
    name: str
    description: str
    frequency_type: FrequencyType
    metric_type: MetricType
    target_value: int | None = None
    target_unit: str | None = None
    day_of_week: list[str] | None  = None
    interval_days: int | None = None


class CreateHabit(HabitBase):
    pass


class HabitResponse(HabitBase):
    id: str
    user_id: str
    created_at: datetime


class HabitUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    frequency_type: FrequencyType | None = None
    metric_type: MetricType | None = None
    target_value: int | None = None
    target_unit: str | None = None
    day_of_week: list[str] | None = None
    interval_days: int | None = None
