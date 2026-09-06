from logging.config import fileConfig
import importlib.util
import os
import pathlib

from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import src
from src.core.database import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Set up ALEMBIC_DB_URL from .env file (Not automatic, you need to do this config manually if you want to use .env file and the DB_URL)
load_dotenv()
ALEMBIC_DB_URL = os.getenv("ALEMBIC_DB_URL")
config.set_main_option("sqlalchemy.url", ALEMBIC_DB_URL)


def _discover_and_import_models() -> None:
    """
    Import every <package>/models.py under src so Alembic autogenerate sees all
    tables without you having to add an explicit import for each new model.
    Each module registers its tables on Base.metadata when it is executed.
    """
    src_dir = pathlib.Path(src.__file__).parent
    for path in sorted(src_dir.rglob("models.py")):
        module_name = ".".join(path.relative_to(src_dir.parent).with_suffix("").parts)
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]


# Import all application models so autogenerate knows every table.
_discover_and_import_models()
# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata



# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
