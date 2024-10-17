from app.repositories import repository_scope

from .models import model
from .scheduler import scheduler

import numpy as np

import logging

logger = logging.getLogger(__name__)

async def embeddings_worker(resume_id: int):
    async with repository_scope() as repos:
        resume = await repos.resume().find_by_id(resume_id)

    if not resume:
        return logger.warning(f"Resume with ID {resume_id} not found.")

    resume.content_embedding = model.encode(
        resume.content, show_progress_bar=False, normalize_embeddings=True
    )
    skill_embeddings = model.encode(
        resume.key_skills, show_progress_bar=False, normalize_embeddings=True
    )
    # use max over all skill embedding to capture most important features
    resume.skills_embeddings = np.max(np.stack(skill_embeddings), axis=0)

    async with repository_scope() as repos:
        await repos.resume().update(resume)

    await scheduler.enqueue("estimate_resume_salary", [resume.id])
