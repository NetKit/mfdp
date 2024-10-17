from aiogram import BaseMiddleware
from aiogram.types import Message

from typing import Callable, Dict, Any, Awaitable

from app.repositories import repository_scope
from app.models import JobSeeker


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        async with repository_scope() as repos:
            user = await repos.job_seeker().find_by_telegram_id(
                data["event_from_user"].id
            )
            if not user:
                user = JobSeeker(
                    telegram_id=data["event_from_user"].id,
                    name=data["event_from_user"].full_name,
                )
            await repos.job_seeker().add(user)

        data["user"] = user

        return await handler(event, data)
