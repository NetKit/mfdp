from app.core.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, ARRAY
from pgvector.sqlalchemy import Vector

from typing import Optional, List

class Vacancy(Base):
    __tablename__ = 'vacancies'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text())
    requirements: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String(128)), nullable=True)
    languages: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String(64)), nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(64))
    country: Mapped[Optional[str]] = mapped_column(String(128))
    job_type: Mapped[Optional[str]] = mapped_column(String(64))
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(1024), nullable=True)

    company_id: Mapped[int] = mapped_column(ForeignKey('companies.id'), nullable=False)
    company: Mapped["Company"] = relationship(back_populates="vacancies")
