from datetime import date
from pydantic import BaseModel
from app.database.utils import LogStatus


class LogBase(BaseModel):
    date_: date = date.today()
    status: LogStatus = LogStatus.COMPLETED
    value: float | None = None
    note: str | None = None


class LogCreate(LogBase):
    pass


class LogUpdate(BaseModel):
    date_: date | None = None
    status: LogStatus | None = None
    value: float | None = None
    note: str | None = None


class LogResponse(BaseModel):
    id: str
    habit_id: str
    date_: date
    status: LogStatus
    value: float | None
    note: str | None

    model_config = {"from_attributes": True}
