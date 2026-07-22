from typing import List

from fastapi import APIRouter, HTTPException, status
from app.api.dependencies import  CurrentUserDps, HabitsDeps
from app.api.schemas.habit import HabitResponse, CreateHabit, HabitUpdate


router = APIRouter()


@router.get("/list", response_model=List[HabitResponse])
async def get_habit_list(service: HabitsDeps, user: CurrentUserDps):
    return await service.get_all_habit(user)


@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(habit_id: str, service: HabitsDeps, user: CurrentUserDps):
    habit = await service.get_habit_by_id(habit_id, user)
    if habit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    return habit


@router.post("/", response_model=HabitResponse, status_code=201)
async def create_habit(service: HabitsDeps, habit_data: CreateHabit, user: CurrentUserDps):
    return await service.create_habit(habit_data, user)


@router.put("/{habit_id}/update", response_model=HabitResponse)
async def update_habit(habit_id: str, service: HabitsDeps, habit_data: HabitUpdate, user: CurrentUserDps):
    result = await service.update_habit(habit_id, habit_data, user)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You're not allowed to perform this action"
        )
    return result


@router.delete("/{habit_id}/delete", response_model=None)
async def delete_habit(habit_id: str, service: HabitsDeps, user: CurrentUserDps):
    result = await service.delete_habit(habit_id, user)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You're not allowed to perform this action"
        )
    return {
        "message": "Habit Has been Deleted Successfully"
    }


