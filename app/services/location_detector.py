from app.services import gemini
from app.repositories import repository_scope
from app.core import available_cities

DEFAULT_LOCATION = "москва"


async def detect_location(user_id: int, location: str) -> str:
    prompt = f"""
From input string select location that is closest to input. If nothing suits return blank string
Input: {location}
List of locations: {available_cities}
return only location string without any explanation and formatting
"""
    location = await gemini.request(prompt=prompt)
    if location == "":
        location = DEFAULT_LOCATION

    async with repository_scope() as repos:
        await repos.job_seeker().partial_update(
            user_id,
            {"location": location},
        )

    return location
