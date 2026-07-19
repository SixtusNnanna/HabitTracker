from fastapi import APIRouter
from .user import router as user_router
from .habits import router as habit_router
from .log import router as log_router
from .stats import router as stat_router


router = APIRouter()

router.include_router(user_router, prefix="/auth", tags=["User"])
router.include_router(habit_router, prefix="/habit", tags=["Habit"])
router.include_router(log_router, prefix="/log", tags=["log"])
router.include_router(stat_router, prefix="/habit", tags=["HabitStat"])
