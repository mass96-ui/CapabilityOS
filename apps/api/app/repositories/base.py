from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository providing reusable CRUD operations.

    All repositories in CapabilityOS should inherit from this class.
    """

    def __init__(self, session: AsyncSession, model: type[ModelType]) -> None:
        self.session = session
        self.model = model

    # ==========================================================
    # CREATE
    # ==========================================================

    async def create(self, **kwargs: Any) -> ModelType:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    # ==========================================================
    # READ
    # ==========================================================

    async def get_by_id(self, entity_id: str) -> ModelType | None:
        statement = select(self.model).where(self.model.id == entity_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        filters: dict[str, Any] | None = None,
    ) -> list[ModelType]:
        statement = select(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    statement = statement.where(
                        getattr(self.model, field) == value
                    )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    # ==========================================================
    # UPDATE
    # ==========================================================

    async def update(
        self,
        instance: ModelType,
        **kwargs: Any,
    ) -> ModelType:
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    # ==========================================================
    # DELETE
    # ==========================================================

    async def delete(self, instance: ModelType) -> None:
        await self.session.delete(instance)
        await self.session.commit()

    async def delete_by_id(self, entity_id: str) -> bool:
        statement = delete(self.model).where(self.model.id == entity_id)
        result = await self.session.execute(statement)
        await self.session.commit()
        return result.rowcount > 0

    # ==========================================================
    # EXISTS
    # ==========================================================

    async def exists(self, entity_id: str) -> bool:
        statement = select(self.model.id).where(self.model.id == entity_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none() is not None

    # ==========================================================
    # COUNT
    # ==========================================================

    async def count(self) -> int:
        statement = select(self.model)
        result = await self.session.execute(statement)
        return len(result.scalars().all())