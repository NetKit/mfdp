from app.core import bot
from app.services import resume_extractor
from app.repositories import repository_scope
from app.models import Resume

from .scheduler import scheduler

import logging

logger = logging.getLogger(__name__)


async def extractor_worker(user_id: int, telegram_file_id: str):
    logger.info(
        f"Starting extraction process for user ID {user_id} with file ID {telegram_file_id}."
    )

    async with repository_scope() as repos:
        user = await repos.job_seeker().find_by_id(user_id)

    if not user:
        logger.error(f"User with ID {user_id} not found.")
        return

    logger.info(f"User with ID {user_id} found. Proceeding to fetch file.")
    file_info = await bot.get_file(telegram_file_id)

    target_path = f"/tmp/{telegram_file_id}.pdf"

    await bot.download_file(file_path=file_info.file_path, destination=target_path)

    try:
        logger.info(f"Extracting data from file path {target_path}.")
        data = await resume_extractor.extract(target_path)
    except Exception as e:
        logger.exception(
            f"An error occurred while extracting resume for user ID {user_id}: {e}"
        )
        return await bot.send_message(
            user.telegram_id,
            "Unfortunately, we weren't able to parse your resume. You can do it manually later",
        )

    logger.info(
        f"Data extraction successful for user ID {user_id}. Compiling information."
    )
    combined_info = []

    if data.summary:
        combined_info.append(data.summary)

    if data.about:
        combined_info.append(data.about)

    if data.workExperience:
        for experience in data.workExperience:
            combined_info.append(
                f"{experience.jobTitle} at {experience.company} from {experience.startDate} to {experience.endDate}"
            )
            if experience.achievments:
                combined_info.append(
                    "Achievements: " + ", ".join(experience.achievments)
                )

    combined_string = "\n".join(combined_info)
    logger.info(
        f"Information compiled for user ID {user_id}. Updating or creating resume record."
    )

    async with repository_scope() as repos:
        resume = await repos.resume().find_by_seeker_id(user.id)
        if not resume:
            logger.info(
                f"No existing resume found for user ID {user_id}. Creating new resume."
            )
            resume = Resume(
                seniority=data.seniority,
                role=data.role,
                title=data.title,
                yoe=data.experience_years,
                education=data.education,
                key_skills=data.skills,
                languages=data.languages,
                content=combined_string,
                job_seeker_id=user.id,
            )

            await repos.resume().add(resume)
        else:
            logger.info(
                f"Existing resume found for user ID {user_id}. Updating resume."
            )
            resume.seniority = data.seniority
            resume.role = data.role
            resume.title = data.title
            resume.yoe = data.experience_years
            resume.education = data.education
            resume.key_skills = data.skills
            resume.languages = data.languages
            resume.content = combined_string

            await repos.resume().update(resume)

    logger.info(
        f"Resume processing complete for user ID {user_id}. Sending confirmation message."
    )
    await bot.send_message(user.telegram_id, "All done! :)")
    await scheduler.enqueue("calculate_resume_embeddings", [resume.id])
