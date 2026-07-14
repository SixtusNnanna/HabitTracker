from typing import List

from fastapi import APIRouter, HTTPException, status
from app.api.dependencies import  CurrentUserDps, HabitsDeps
from app.api.schemas.habit import HabitResponse, CreateHabit, HabitUpdate


router = APIRouter()


@router.get("/habit-list", response_model=List[HabitResponse])
async def get_habit_list(service: HabitsDeps, user: CurrentUserDps):
    return await service.get_all_habit(user)


@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(id: str, service: HabitsDeps, user: CurrentUserDps):
    habit = await service.get_habit_by_id(id, user)
    if habit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    return habit


@router.post("/create-habit", response_model=HabitResponse)
async def create_habit(service: HabitsDeps, habit_data: CreateHabit, user: CurrentUserDps):
    return await service.create_habit(habit_data, user)


@router.put("/{habit_id}/update", response_model=HabitResponse)
async def update_habit(id: str, service: HabitsDeps, habit_data: HabitUpdate, user: CurrentUserDps):
    return await service.update_habit(id, habit_data, user)


@router.delete("/{habit_id}/delete", response_model=None)
async def delete_habit(id: str, service: HabitsDeps, user: CurrentUserDps):
    await service.delete_habit(id, user)
    return {
        "message": "Habit Has been Deleted Successfully"
    }


