from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text
from typing import Optional

class Manager(Base):
    __tablename__ = "managers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    token: Mapped[Optional[str]] = mapped_column(Text(), nullable=True, index=True)

    company: Mapped["Company"] = relationship("Company", back_populates="managers")
