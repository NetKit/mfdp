from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.repositories.base import BaseAsyncRepository
from app.models.resume import Resume

from typing import Optional


class ResumeRepository(BaseAsyncRepository[Resume]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Resume)

    async def find_by_seeker_id(self, seeker_id: int) -> Optional[Resume]:
        result = await self.session.execute(
            select(self.model).where(self.model.job_seeker_id == seeker_id)
        )
        return result.scalars().first()
