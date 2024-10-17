from app.core.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from typing import Optional

from enum import Enum

class UserStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"


class PreferredWorkType(Enum):
    IN_OFFICE = "in office"
    HYBRID = "hybrid"
    REMOTE = "remote"


class JobSeeker(Base):
    __tablename__ = "job_seekers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[UserStatus] = mapped_column(
        index=True, nullable=False, default=UserStatus.PENDING
    )
    telegram_id: Mapped[int] = mapped_column(index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(
        String(256), index=True, unique=True, nullable=True
    )
    location: Mapped[str] = mapped_column(index=True, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(15), nullable=True, unique=True)
    preferred_work_type: Mapped[PreferredWorkType] = mapped_column(
        index=True, nullable=False, default=PreferredWorkType.IN_OFFICE
    )

    resume: Mapped["Resume"] = relationship(
        back_populates="job_seeker", cascade="all, delete-orphan"
    )
