from ulid import ULID
from datetime import datetime, date
from app.database.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String, Integer, Text, ForeignKey, Enum, JSON, DateTime, Date, func,
    Numeric, Boolean
)
from app.database.utils import MetricType, FrequencyType, LogStatus


def generate_ulid():
    return str(ULID())


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(
        String(26), primary_key=True, index=True,
        default=generate_ulid
    )
    full_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(Text)
    is_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
        )
    habits: Mapped[list["Habit"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Habit(Base):
    __tablename__ = "habits"
    id: Mapped[str] = mapped_column(
        String(26), primary_key=True, index=True,
        default=generate_ulid
    )
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)

    frequency_type: Mapped[FrequencyType] = mapped_column(
        Enum(FrequencyType), nullable=False
        )
    metric_type: Mapped[MetricType] = mapped_column(
        Enum(MetricType), default=MetricType.BOOLEAN
    )
    target_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_unit: Mapped[str | None] = mapped_column(String(30), nullable=True)
    day_of_week: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    interval_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    user: Mapped["User"] = relationship(back_populates="habits")
    logs: Mapped[list["HabitLog"]] = relationship(
        back_populates="habit",
        cascade="all, delete-orphan"
    )


class HabitLog(Base):
    __tablename__ = "logs"

    id: Mapped[str] = mapped_column(
        String(26),
        index=True,
        primary_key=True,
        default=generate_ulid,
    )
    habit_id: Mapped[str] = mapped_column(
        String, ForeignKey("habits.id", ondelete="CASCADE"),
        nullable=False
    )

    date_: Mapped[date] = mapped_column(
        Date, index=True, default=date.today, nullable=False
    )
    status: Mapped[LogStatus] = mapped_column(
        Enum(LogStatus, name="log_status"),
        default=LogStatus.COMPLETED,
        nullable=False
    )
    value: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    note: Mapped[str] = mapped_column(Text, nullable=True)

    completed_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    habit: Mapped[Habit] = relationship(
        back_populates="logs"
    )

