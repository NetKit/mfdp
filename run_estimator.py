from app.workers.salary_estimator import resume_salary_estimator_worker

import asyncio

asyncio.run(resume_salary_estimator_worker(1))
