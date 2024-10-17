from sqlalchemy.ext.asyncio import AsyncSession

from contextlib import asynccontextmanager

from .company import CompanyRepository
from .job_seeker import JobSeekerRepository
from .resume import ResumeRepository
from .vacancy import VacancyRepository
from .manager import ManagerRepository

from app.core.database import AsyncSessionLocal

class RepositoryManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    def company(self) -> CompanyRepository:
        return CompanyRepository(self.session)

    def job_seeker(self) -> JobSeekerRepository:
        return JobSeekerRepository(self.session)

    def resume(self) -> ResumeRepository:
        return ResumeRepository(self.session)

    def vacancy(self) -> VacancyRepository:
        return VacancyRepository(self.session)

    def manager(self) -> ManagerRepository:
        return ManagerRepository(self.session)

@asynccontextmanager
async def repository_scope():
    session = AsyncSessionLocal()
    repos = RepositoryManager(session)

    try:
        yield repos
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()
