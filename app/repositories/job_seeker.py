from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseAsyncRepository
from app.models.job_seeker import JobSeeker

from sqlalchemy.future import select

from typing import Optional


class JobSeekerRepository(BaseAsyncRepository[JobSeeker]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, JobSeeker)

    async def find_by_telegram_id(self, telegram_id: int) -> Optional[JobSeeker]:
        query = await self.session.execute(
            select(JobSeeker).where(JobSeeker.telegram_id == telegram_id)
        )
        return query.scalars().first()
