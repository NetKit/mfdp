from app.repositories import repository_scope
from app.services import prepare_data_for_prediction, predict_salary

import logging

logger = logging.getLogger(__name__)


async def vacancy_salary_estimator_worker(vacancy_id):
    async with repository_scope() as repos:
        vacancy = await repos.vacancy().find_by_id(vacancy_id)

    if not vacancy:
        return logger.error(f"Vacancy with ID {vacancy_id} not found.")

    encoded_df = prepare_data_for_prediction(
        vacancy.required_years_of_experience,
        vacancy.seniority,
        vacancy.job_type,
        vacancy.location,
        vacancy.role,
        vacancy.description,
        vacancy.requirements_embedding,
    )
    predicted_salary = predict_salary(
        encoded_df, vacancy.role, vacancy.location, vacancy.seniority
    )

    logger.info(f"Predicted salary for vacancy ID {vacancy_id}: {predicted_salary}")

    async with repository_scope() as repos:
        await repos.vacancy().partial_update(
            vacancy.id, {"estimated_salary": predicted_salary}
        )
