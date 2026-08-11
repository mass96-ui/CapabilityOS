from __future__ import annotations

from typing import Generic, Sequence, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseService(Generic[ModelType]):
    """
    Generic CRUD service.

    Every domain service in CapabilityOS should inherit from this class.
    """

    def __init__(
        self,
        session: AsyncSession,
        model: type[ModelType],
    ) -> None:
        self.session = session
        self.model = model

    async def create(self, obj: ModelType) -> ModelType:
        """
        Persist a new model instance.
        """
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get_by_id(self, obj_id: int) -> ModelType | None:
        """
        Retrieve a record by primary key.
        """
        statement = select(self.model).where(self.model.id == obj_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_all(self) -> Sequence[ModelType]:
        """
        Retrieve all records.
        """
        statement = select(self.model)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def update(self, obj: ModelType) -> ModelType:
        """
        Update an existing record.
        """
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj_id: int) -> bool:
        """
        Delete a record by primary key.
        """
        statement = delete(self.model).where(self.model.id == obj_id)
        result = await self.session.execute(statement)
        await self.session.commit()

        return result.rowcount > 0