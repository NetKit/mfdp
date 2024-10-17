from app.core.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from typing import List


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(256), nullable=True)

    vacancies: Mapped[List["Vacancy"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )
    managers: Mapped[List["Manager"]] = relationship(
        "Manager", back_populates="company", cascade="all, delete-orphan"
    )
