from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

import os

import app.models # noqa
from app.core.database import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

engine = create_async_engine(os.getenv('DATABASE_URL'), future=True)

def run_migrations_offline() -> None:
    pass


def run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine

    async with connectable.connect() as connection:
        await connection.run_sync(run_migrations)
    
    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
