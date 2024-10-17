from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from typing import Type, TypeVar, Generic, Optional, List

from app.core.database import Base

T = TypeVar("T", bound=Base)


class BaseAsyncRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def find_by_id(self, id: int) -> Optional[T]:
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalars().first()

    async def find_by_ids(self, ids: List[int]) -> List[T]:
        result = await self.session.execute(
            select(self.model).where(self.model.id.in_(ids))
        )
        return result.scalars().all()

    async def find_all(self) -> List[T]:
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def add(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: T) -> Optional[T]:
        existing_entity = await self.find_by_id(entity.id)
        if existing_entity:
            for key, value in vars(entity).items():
                if key != "_sa_instance_state":
                    setattr(existing_entity, key, value)
            await self.session.flush()
            await self.session.refresh(existing_entity)
        return existing_entity

    async def partial_update(self, id: int, update_data: dict) -> Optional[T]:
        await self.session.execute(
            update(self.model).where(self.model.id == id).values(**update_data)
        )
        await self.session.flush()
        return await self.find_by_id(id)

    async def delete(self, id: int) -> bool:
        entity = await self.find_by_id(id)
        if entity:
            await self.session.delete(entity)
            await self.session.flush()
            return True
        return False
