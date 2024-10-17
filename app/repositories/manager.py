from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.repositories.base import BaseAsyncRepository
from app.models import Manager

from typing import Optional

class ManagerRepository(BaseAsyncRepository[Manager]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Manager)

    async def find_by_email(self, email: str) -> Optional[Manager]:
        result = await self.session.execute(
            select(self.model).where(self.model.email == email)
        )
        return result.scalars().first()

    async def find_by_company_id(self, company_id: int) -> list[Manager]:
        result = await self.session.execute(
            select(self.model).where(self.model.company_id == company_id)
        )
        return result.scalars().all()

    async def find_by_token(self, token: str) -> Optional[Manager]:
        result = await self.session.execute(
            select(self.model).where(self.model.token == token)
        )
        return result.scalars().first()
