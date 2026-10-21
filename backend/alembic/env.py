from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

import app.models  # noqa: F401 - registers every model on Base.metadata
from app.core.config import settings
from app.core.database import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata

# Created with raw SQL in migration 0002 (partitioning and the trigram index have no ORM equivalent).
SQL_ONLY = {"ix_items_name_trgm", "ix_price_history_item"}


def include_object(obj, name, type_, reflected, compare_to):
    return not (name in SQL_ONLY or (name or "").startswith("price_history"))


def run_migrations_offline() -> None:
    context.configure(url=settings.DATABASE_URL, target_metadata=target_metadata, literal_binds=True, include_object=include_object)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, include_object=include_object)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
