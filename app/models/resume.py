from app.core.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, ARRAY, Integer
from pgvector.sqlalchemy import Vector

from typing import Optional, List


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    summary: Mapped[str] = mapped_column(Text(), nullable=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    role: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    seniority: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    yoe: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    key_skills: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(128)), nullable=True
    )
    languages: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(64)), nullable=True
    )
    education: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    skills_embeddings: Mapped[Optional[List[float]]] = mapped_column(
        Vector(1024), nullable=True
    )
    content_embedding: Mapped[Optional[List[float]]] = mapped_column(
        Vector(1024), nullable=True
    )
    estimated_salary: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    job_seeker_id: Mapped[int] = mapped_column(
        ForeignKey("job_seekers.id"), nullable=False
    )
    job_seeker: Mapped["JobSeeker"] = relationship(back_populates="resume")
