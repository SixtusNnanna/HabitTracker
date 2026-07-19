from typing import List

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import CurrentHabitDeps, LogDeps
from app.api.schemas.log import LogCreate, LogResponse, LogUpdate
from app.database.models import HabitLog

router = APIRouter()


@router.get("/{log_id}", response_model=LogResponse)
async def get_log_id(log_id: str, service: LogDeps, habit: CurrentHabitDeps):
    log = await service.get_log(id=log_id, habit_id=habit.id)
    if log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Log not found"
        )
    return log


@router.get("/", response_model=List[LogResponse])
async def log_list(service: LogDeps, habit: CurrentHabitDeps):
    return await service.list_logs(habit.id)


@router.post("/", response_model=LogResponse)
async def create_log(
    service: LogDeps,
    habit: CurrentHabitDeps,
    log_data: LogCreate,
) -> HabitLog:
    try:
        log = await service.create_log(habit_id=habit.id, log_data=log_data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)
        )
    return log


@router.put("/{log_id}/update", response_model=LogResponse)
async def update_log_(
    log_id: str,
    service: LogDeps,
    habit: CurrentHabitDeps,
    log_update_data: LogUpdate,
):
    log = await service.update_log(
        id=log_id,
        habit_id=habit.id,
        update_data=log_update_data
    )
    if log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Log not found"
        )
    return log


@router.delete("/{log_id}", response_model=None)
async def delete_log(log_id: str, service: LogDeps, habit: CurrentHabitDeps):
    await service.delete_log(id=log_id, habit_id=habit.id)
    return {
        "message": "Log Deleted Succesfully"
    }


