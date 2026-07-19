from datetime import date, timedelta
from typing import Optional
import calendar
from abc import ABC, abstractmethod
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseService
from app.utils import Period
from app.database.models import Habit, HabitLog, User
from app.api.schemas.log import LogCreate, LogUpdate
from dataclasses import dataclass
from app.database.utils import FrequencyType


class LogService(BaseService[HabitLog]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, HabitLog)

    async def create_log(
        self,
        habit_id: str,
        log_data: LogCreate,
    ) -> HabitLog:
        existing = await self.session.execute(
            select(HabitLog).where(
                HabitLog.habit_id == habit_id,
                HabitLog.date_ == log_data.date_,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Habit already logged for this date")

        new_log = HabitLog(
            **log_data.model_dump(),
            habit_id=habit_id

        )
        self.session.add(new_log)
        await self.session.commit()
        await self.session.refresh(new_log)
        return new_log

    async def get_log(self, id: str, habit_id: str) -> Optional[HabitLog]:
        return await self.get_item(id=id, habit_id=habit_id)

    async def update_log(
        self,
        id: str,
        habit_id: str,
        update_data: LogUpdate,
    ) -> Optional[HabitLog]:

        filters = {"id": id, "habit_id": habit_id}
        return await self.update(
            filters=filters,
            updates=update_data.model_dump(exclude_unset=True)
        )

    async def list_logs(
        self,
        habit_id: str
    ) -> list[HabitLog]:
        return await self.list(habit_id=habit_id)

    async def delete_log(
            self,
            id: str,
            habit_id: str,
    ) -> bool:
        return await self.delete(id=id, habit_id=habit_id)

    async def is_due(self, habit: Habit, check_date: date):
        if check_date < habit.created_at.date():
            return False
        if habit.frequency_type == FrequencyType.DAILY:
            return True
        if habit.frequency_type == FrequencyType.WEEKLY:
            weekday_name = check_date.strftime("%A")
            return weekday_name in (habit.day_of_week or [])

        if habit.frequency_type == FrequencyType.INTERVAL:
            if habit.interval_days is None:
                return None
            days_since_creation = (check_date - habit.created_at.date()).days
            return days_since_creation % habit.interval_days == 0
        return False

    async def get_stats_for_range(self, habit: Habit, start_date: date, end_date: date) -> dict:
        total_days = (end_date - start_date).days + 1

        due_days = [
            start_date + timedelta(days=i)
            for i in range(total_days)
            if await self.is_due(habit, start_date + timedelta(days=i))
        ]

        completed_days = len([
            log for log in habit.logs
            if start_date <= log.date_ <= end_date
        ])

        return {
            "start_date": start_date,
            "end_date": end_date,
            "due_days": len(due_days),
            "completed_days": completed_days,
        }

    async def get_weekly_trend(self, habit: Habit) -> dict:
        today = date.today()

        current = await self.get_stats_for_range(
            habit,
            today - timedelta(days=6),
            today,
        )
        previous = await self.get_stats_for_range(
            habit,
            today - timedelta(days=13),
            today - timedelta(days=7),
        )

        def rate(stats: dict) -> float:
            return (
                stats["completed_days"] / stats["due_days"] * 100
                if stats["due_days"]
                else 0.0
            )

        current_rate = rate(current)
        previous_rate = rate(previous)

        return {
            "current_rate": round(current_rate, 1),
            "previous_rate": round(previous_rate, 1),
            "change_percent": round(current_rate - previous_rate, 1),
        }

    async def get_monthly_trend(self, habit: Habit) -> dict:
        today = date.today()

        current = await self.get_stats_for_range(
            habit,
            today - timedelta(days=29),
            today,
        )
        previous = await self.get_stats_for_range(
            habit,
            today - timedelta(days=59),
            today - timedelta(days=30),
        )

        def rate(stats: dict) -> float:
            return (
                stats["completed_days"] / stats["due_days"] * 100
                if stats["due_days"]
                else 0.0
            )

        current_rate = rate(current)
        previous_rate = rate(previous)

        return {
            "current_rate": round(current_rate, 1),
            "previous_rate": round(previous_rate, 1),
            "change_percent": round(current_rate - previous_rate, 1)
        }














