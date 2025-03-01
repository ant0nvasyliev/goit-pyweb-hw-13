import asyncio
from logging.config import fileConfig

from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool

from alembic import context

from src.conf.config import config as app
from src.entity.models import Base

# Ініціалізація конфігурації Alembic
config = context.config

# Налаштування логування
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Додаємо мета-дані моделей для автоматичної генерації міграцій
target_metadata = Base.metadata

# Встановлюємо URL підключення до бази даних
config.set_main_option("sqlalchemy.url", app.DB_URL)  # ✅ Виправлено

def run_migrations_offline() -> None:
    """Запуск міграцій у офлайн-режимі."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations(connection: Connection):
    """Функція для синхронного запуску міграцій."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def runs_async_migrations():
    """Функція для асинхронного запуску міграцій."""
    db_settings = config.get_section(config.config_ini_section) or {}  # Запобігання None
    connectable = async_engine_from_config(
        db_settings,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Функція для онлайн-режиму міграцій."""
    asyncio.run(runs_async_migrations())


# Вибір режиму запуску міграцій (онлайн або офлайн)
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
