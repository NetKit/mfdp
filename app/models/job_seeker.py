from app.core.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from typing import List, Optional

class JobSeeker(Base):
    __tablename__ = 'job_seekers'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(256), index=True, unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(15), nullable=True, unique=True)
    
    resume: Mapped["Resume"] = relationship(back_populates="job_seeker", cascade="all, delete-orphan")
