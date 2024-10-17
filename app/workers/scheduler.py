from app.core.database import build_asyncpg_conn

from pgqueuer.db import AsyncpgDriver
from pgqueuer.queries import Queries

import json


class Scheduler:
    def __init__(self):
        self.conn = None
        self.driver = None
        self.queries = None

    async def init_connection(self):
        self.conn = await build_asyncpg_conn()
        self.driver = AsyncpgDriver(self.conn)
        self.queries = Queries(self.driver)

    async def enqueue(self, queue: str, params: list):
        if self.queries is None:
            await self.init_connection()

        return await self.queries.enqueue(
            [queue],
            [json.dumps(params).encode("utf-8")],
            [0],
        )


scheduler = Scheduler()
