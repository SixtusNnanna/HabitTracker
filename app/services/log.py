from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseService
from app.database.models import Habit, HabitLog, User
from app.api.schemas.log import LogCreate, LogUpdate, LogResponse


class LogService(BaseService[HabitLog]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, HabitLog)

    async def _get_owned_habit_(
        self, habit_id: str, user: User
    ) -> Optional[Habit]:
        stmt = (
            select(Habit)
            .where(Habit.id == habit_id, Habit.user_id == user.id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_log(
        self,
        habit_id: str,
        log_data: LogCreate,
        user: User,
    ) -> Optional[HabitLog]:
        owned_habit = await self._get_owned_habit_(habit_id, user)
        if not owned_habit:
            return None
        new_log = HabitLog(
            **log_data.model_dump(),
            habit_id=habit_id

        )
        self.session.add(new_log)
        await self.session.commit()
        await self.session.refresh(new_log)
        return new_log

    async def get_log(self, id: str, habit_id: str, user: User) -> Optional[HabitLog]:
        _owned_habit = await self._get_owned_habit_(habit_id, user)
        if not _owned_habit:
            return None
        return await self.get_item(id=id, habit_id=habit_id)

    async def update_log(
        self,
        id: str,
        habit_id: str,
        update_data: LogUpdate,
        user: User,
    ) -> Optional[HabitLog]:
        habit = await self._get_owned_habit_(habit_id, user)
        if not habit:
            return None

        filters = {"id": id, "habit_id": habit.id}
        return await self.update(
            filters=filters,
            updates=update_data.model_dump(exclude_unset=True)
        )

    async def list_logs(
        self,
        habit_id: str,
        user: User,
    ) -> list[HabitLog]:
        habit = await self._get_owned_habit_(habit_id, user)
        if not habit:
            return []
        return await self.list(habit_id=habit.id)

    async def delete_log(
            self,
            habit_id: str,
            user: User
    ) -> bool:
        habit = await self._get_owned_habit_(habit_id, user)
        if habit is None:
            return False
        return await self.delete(id=id, habit_id=habit.id)









