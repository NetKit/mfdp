from app.repositories import repository_scope

from .models import model
from .scheduler import scheduler

import numpy as np

import logging

logger = logging.getLogger(__name__)

async def vacancy_embeddings_worker(vacancy_id: int):
    async with repository_scope() as repos:
        vacancy = await repos.vacancy().find_by_id(vacancy_id)

    if not vacancy:
        return logger.warning(f"Vacancy with ID {vacancy_id} not found.")
    
    requirement_embeddings = model.encode(
        vacancy.requirements, show_progress_bar=False, normalize_embeddings=True
    )
    # use max over all requirement embeddings to capture most important features
    vacancy.requirements_embedding = np.max(np.stack(requirement_embeddings), axis=0)

    async with repository_scope() as repos:
        await repos.vacancy().update(vacancy)

    await scheduler.enqueue("estimate_vacancy_salary", [vacancy.id])
