import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from app.core import settings


class Gemini:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def file_request(
        self, prompt: str, file_path: str, json_schema: str = None, temperature: int = 0
    ):
        file = genai.upload_file(path=file_path)

        conf = GenerationConfig(temperature=temperature)
        if json_schema:
            conf.response_mime_type = "application/json"
            conf.response_schema = json_schema

        result = await self.model.generate_content_async(
            [prompt, file], generation_config=conf
        )

        return result.text

    async def request(self, prompt: str, json_schema: str = None, temperature: int = 0):
        conf = GenerationConfig(temperature=temperature)
        if json_schema:
            conf.response_mime_type = "application/json"
            conf.response_schema = json_schema

        result = await self.model.generate_content_async(prompt, generation_config=conf)

        return result.text


genai.configure(api_key=settings.gemini_token)

gemini = Gemini()
