from fastapi import APIRouter
from .user import router as user_router
from .habits import router as habit_router


router = APIRouter()

router.include_router(user_router, prefix="/auth", tags=["User"])
router.include_router(habit_router, prefix="/habit", tags=["Habit"])
