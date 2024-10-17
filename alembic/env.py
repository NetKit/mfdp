from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

import os

import app.models  # noqa
from app.core.database import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

engine = create_async_engine(os.getenv("DATABASE_URL"), future=True)


def include_object(object, name, type_, reflected, compare_to):
    # Exclude specific tables
    if type_ == "table" and name in ["pgqueuer", "pgqueuer_statistics"]:
        return False  # Ignore these tables

    # Exclude specific indexes related to pgqueuer and pgqueuer_statistics
    if type_ == "index" and name in [
        "pgqueuer_priority_id_id1_idx",
        "pgqueuer_updated_id_id1_idx",
        "pgqueuer_statistics_unique_count",
    ]:
        return False  # Ignore these indexes

    # Exclude specific triggers related to pgqueuer
    if type_ == "trigger" and name == "tg_pgqueuer_changed":
        return False  # Ignore this trigger

    return True  # Include everything else


def run_migrations_offline() -> None:
    pass


def run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
    )

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
