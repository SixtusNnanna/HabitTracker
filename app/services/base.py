from typing import Any, Generic, TypeVar

from sqlalchemy import delete as sa_delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseService(Generic[ModelType]):

    def __init__(self, session: AsyncSession, model: type[ModelType]):
        self.session = session
        self.model = model

    async def add(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get(self, id: str) -> ModelType | None:
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_item(self, **filters) -> ModelType | None:
        stmt = select(self.model).filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, **filters: Any) -> list[ModelType]:
        stmt = select(self.model)
        for field, val in filters.items():
            stmt = stmt.where(getattr(self.model, field) == val)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self, filters: dict[str, Any], updates: dict[str, Any]
    ) -> ModelType | None:
        obj = await self.get_item(**filters)
        if obj is None:
            return None
        for field, val in updates.items():
            setattr(obj, field, val)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def delete(self, **filters):
        result = await self.session.execute(sa_delete(self.model).filter_by(**filters))
        await self.session.commit()
        return result.rowcount > 0
