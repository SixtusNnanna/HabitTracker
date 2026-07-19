from datetime import date
from fastapi import APIRouter

from app.api.dependencies import CurrentHabitDeps, LogDeps


router = APIRouter()


@router.get("/{habit_id}/stat-range", response_model=dict)
async def get_habit_start_in_range(
    start_date: date,
    end_date: date,
    service: LogDeps,
    habit: CurrentHabitDeps
     ) -> dict:
    return await service.get_stats_for_range(habit, start_date, end_date)


@router.get("/{habit_id}/stats/week", response_model=dict)
async def weekly_starts(habit: CurrentHabitDeps, service: LogDeps):
    return await service.get_weekly_trend(habit)


@router.get("/{habit_id}/stats/month", response_model=dict)
async def monthly_starts(habit: CurrentHabitDeps, service: LogDeps):
    return await service.get_monthly_trend(habit)
