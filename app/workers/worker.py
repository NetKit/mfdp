from __future__ import annotations

from pgqueuer.db import AsyncpgDriver
from pgqueuer.models import Job
from pgqueuer.qm import QueueManager

from app.core.database import build_asyncpg_conn

from .extractor import extractor_worker
from .embeddings import embeddings_worker
from .vacancy_embeddings import vacancy_embeddings_worker
from .resume_salary_estimator import resume_salary_estimator_worker
from .vacancy_salary_estimator import vacancy_salary_estimator_worker

import logging
import json

logging.basicConfig(level=logging.INFO)

async def run_worker() -> QueueManager:
    conn = await build_asyncpg_conn()

    driver = AsyncpgDriver(conn)
    qm = QueueManager(driver)

    @qm.entrypoint(
        "extract_resume",
        concurrency_limit=1,
        requests_per_second=0.1,
    )
    async def extract_resume(job: Job) -> None:
        params = json.loads(job.payload)

        await extractor_worker(*params)

    @qm.entrypoint(
        "calculate_resume_embeddings",
        concurrency_limit=1,
    )
    async def calculate_resume_embeddings(job: Job) -> None:
        params = json.loads(job.payload)

        await embeddings_worker(params[0])
    
    @qm.entrypoint(
        "estimate_resume_salary",
    )
    async def estimate_resume_salary(job: Job) -> None:
        params = json.loads(job.payload)

        await resume_salary_estimator_worker(params[0])

    @qm.entrypoint(
        "calculate_vacancy_embeddings",
        concurrency_limit=1,
    )
    async def calculate_vacancy_embeddings(job: Job) -> None:
        params = json.loads(job.payload)

        await vacancy_embeddings_worker(params[0])

    @qm.entrypoint(
        "estimate_vacancy_salary",
    )
    async def estimate_vacancy_salary(job: Job) -> None:
        params = json.loads(job.payload)

        await vacancy_salary_estimator_worker(params[0])

    return qm
