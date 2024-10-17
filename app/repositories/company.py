from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseAsyncRepository
from app.models.company import Company


class CompanyRepository(BaseAsyncRepository[Company]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Company)
