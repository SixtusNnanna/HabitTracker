from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Habit, User
from app.services.base import BaseService
from app.api.schemas.habit import CreateHabit, HabitBase, HabitUpdate


class HabitService(BaseService[Habit]):

    def __init__(self, session: AsyncSession):
        super().__init__(session, Habit)

    async def create_habit(
        self, habit_create_data: CreateHabit, user: User
    ) -> Habit:
        new_habit = Habit(
            **habit_create_data.model_dump(),
            user_id=user.id
        )
        await self.add(new_habit)
        return new_habit

    async def get_habit_by_id(
            self, id: str, user: User
    ) -> Habit | None:
        return await self.get_item(id=id, user_id=user.id)

    async def update_habit(
            self,
            id: str,
            habit_update_data: HabitUpdate,
            user: User
            ):
        filters = {"id": id, "user_id": user.id}
        return await self.update(
            filters=filters,
            updates=habit_update_data.model_dump(exclude_unset=True)
        )

    async def get_all_habit(self, user: User):
        return await self.list(user_id=user.id)

    async def delete_habit(self, id: str, user: User):
        return await self.delete(id, user.id)

