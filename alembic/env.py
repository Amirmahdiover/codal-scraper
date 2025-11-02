from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import configparser




# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

import os
from dotenv import load_dotenv
import urllib
load_dotenv()
USE_WINDOWS_AUTH = os.getenv("USE_WINDOWS_AUTH", "no").lower() == "yes"

if USE_WINDOWS_AUTH:
    connection_string = (
        "mssql+pyodbc://@{host}/{db}?"
        "driver={driver}&trusted_connection=yes&TrustServerCertificate={trust_cert}"
    ).format(
        host=os.getenv("DB_HOST"),
        db=os.getenv("DB_NAME"),
        driver=urllib.parse.quote_plus(os.getenv("DB_DRIVER")),
        trust_cert=os.getenv("TRUST_SERVER_CERTIFICATE", "no")
    )
else:
    connection_string = (
        "mssql+pyodbc://{user}:{password}@{host}/{db}?"
        "driver={driver}&TrustServerCertificate={trust_cert}"
    ).format(
        user=os.getenv("DB_USER"),
        password=urllib.parse.quote_plus(os.getenv("DB_PASSWORD")),
        host=os.getenv("DB_HOST"),
        db=os.getenv("DB_NAME"),
        driver=urllib.parse.quote_plus(os.getenv("DB_DRIVER")),
        trust_cert=os.getenv("TRUST_SERVER_CERTIFICATE", "no")
    )

# Override the config with the env-based URL
config = context.config
config._file_config = configparser.RawConfigParser()


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from db.models import Base  
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


from sqlalchemy import create_engine

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we create an Engine directly using the connection string
    built from environment variables, and associate a connection with the context.
    """

    connectable = create_engine(connection_string, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # optional: detects column type changes
            compare_server_default=True  # optional: detects default changes
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


