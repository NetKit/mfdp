from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.repositories.base import BaseAsyncRepository
from app.models.vacancy import Vacancy

from typing import List

class VacancyRepository(BaseAsyncRepository[Vacancy]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Vacancy)
    
    async def find_by_company_id(self, company_id: int) -> List[Vacancy]:
        result = await self.session.execute(
            select(self.model).where(self.model.company_id == company_id)
        )
        return result.scalars().all()
