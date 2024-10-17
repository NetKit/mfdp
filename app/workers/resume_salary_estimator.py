from app.core import bot
from app.repositories import repository_scope
from app.services import prepare_data_for_prediction, predict_salary

import logging

logger = logging.getLogger(__name__)


async def resume_salary_estimator_worker(resume_id):
    async with repository_scope() as repos:
        resume = await repos.resume().find_by_id(resume_id)
        user = await repos.job_seeker().find_by_id(resume.job_seeker_id)

    if not resume:
        return logger.error(f"Resume with ID {resume_id} not found.")

    encoded_df = prepare_data_for_prediction(
        resume.yoe,
        resume.seniority,
        user.preferred_work_type.value,
        user.location,
        resume.role,
        resume.content,
        resume.skills_embeddings,
    )
    predicted_salary = predict_salary(
        encoded_df, resume.role, user.location, resume.seniority
    )

    logger.info(f"Predicted salary for resume ID {resume_id}: {predicted_salary}")

    async with repository_scope() as repos:
        await repos.resume().partial_update(
            resume.id, {"estimated_salary": predicted_salary}
        )

    await bot.send_message(
        user.telegram_id,
        f"Your current estimated salary based on your resume, work type and location is about {predicted_salary}$",
    )
