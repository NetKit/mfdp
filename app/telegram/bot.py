from aiogram import Dispatcher, F
from aiogram.types import BotCommand
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from app.models import JobSeeker
from app.core import bot
from app.core import salary_percentiles
from app.services import detect_location
from app.telegram.middlewares import AuthMiddleware
from app.workers.scheduler import scheduler
from app.repositories import repository_scope

import logging

logging.basicConfig(level=logging.INFO)

dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message, user: JobSeeker):
    await message.answer(f"Hello there, {user.name}!")


class UploadResumeForm(StatesGroup):
    location = State()
    work_type = State()
    upload = State()


@dp.message(Command("upload_resume"))
async def upload_resume(message: Message, user: JobSeeker, state: FSMContext):
    await state.set_state(UploadResumeForm.location)

    await message.answer("What location are you considering?")


@dp.message(UploadResumeForm.location)
async def add_file(message: Message, user: JobSeeker, state: FSMContext):
    location = await detect_location(user.id, message.text)

    await message.answer(f"{location} it is!")
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="in office")],
            [KeyboardButton(text="hybrid")],
            [KeyboardButton(text="remote")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await state.set_state(UploadResumeForm.work_type)
    await message.answer(
        "What type of work are you looking for?", reply_markup=keyboard
    )


@dp.message(UploadResumeForm.work_type)
async def set_work_type(message: Message, user: JobSeeker, state: FSMContext):
    work_type = message.text.lower()
    if work_type not in ["in office", "hybrid", "remote"]:
        return await message.answer(
            "Please choose a valid work type: in office, hybrid, or remote."
        )

    await state.update_data(work_type=work_type)
    await state.set_state(UploadResumeForm.upload)
    await message.answer("Great! Now, please upload your resume as a PDF file.")


@dp.message(UploadResumeForm.upload)
async def add_file(message: Message, user: JobSeeker, state: FSMContext):
    if not message.document.file_id:
        return await message.answer("Please add pdf file")

    await scheduler.enqueue("extract_resume", [user.id, message.document.file_id])
    await message.answer("Processing resume now!")
    await state.clear()

@dp.message(Command("summary"))
async def get_resume_summary(message: Message, user: JobSeeker):
    async with repository_scope() as repos:
        resume = await repos.resume().find_by_seeker_id(user.id)
        
    if not resume:
        await message.answer("You haven't uploaded a resume yet. Use /upload_resume to add your resume.")
        return

    summary = f"Here's a summary of your resume:\n\n"
    summary += f"Role: {resume.role}\n"
    summary += f"Seniority: {resume.seniority}\n"
    summary += f"Preferred work type: {user.preferred_work_type.name}\n\n"
    summary += f"Preferred location: {user.location}\n"
    
    if resume.key_skills:
        summary += f"Skills: {', '.join(resume.key_skills)}\n\n"

    if resume.estimated_salary:
        summary += f"Estimated salary {resume.estimated_salary}\n"

    if resume.role and user.location and resume.seniority:
        median_salary = salary_percentiles.get(resume.role, {}).get(user.location, {}).get(resume.seniority, {}).get('percentile_50')
        if median_salary is not None:
            summary += f"Median salary for your role and location is: ${median_salary:.2f}\n"

    if resume.summary:
        summary += f"\n{resume.summary}\n"

    await message.answer(summary)

async def run_bot() -> None:
    dp.update.outer_middleware(AuthMiddleware())

    await bot.set_my_commands([
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="upload_resume", description="Upload your resume"),
        BotCommand(command="summary", description="Get a summary of your resume"),
        BotCommand(command="search", description="Search for job vacancies"),
    ])
    
    await dp.start_polling(bot)
