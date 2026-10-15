from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, text
from sqlalchemy.dialects import postgresql

from etl.config import get_settings, validate_warehouse_schema
from etl.load.db import database_url

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()
url = database_url(config.attributes.get('database_url', settings.database_url))
schema = config.attributes.get('warehouse_schema', settings.warehouse_schema)
if not schema:
    raise ValueError('Explicit WAREHOUSE_SCHEMA is required for migration review/execution')
# Reuse the settings validator even for programmatic Alembic callers.
validate_warehouse_schema(schema)
quoted_schema = postgresql.dialect().identifier_preparer.quote_schema(schema)


def run_migrations_offline() -> None:
    context.configure(url=url, literal_binds=True, dialect_opts={'paramstyle': 'named'},
                      version_table_schema=schema)
    with context.begin_transaction():
        context.execute(f'SET LOCAL search_path TO {quoted_schema}, pg_catalog')
        context.run_migrations()


def migrate(connection):
    if connection.dialect.name != 'postgresql':
        raise ValueError('The migration chain requires PostgreSQL')
    # Both frozen 002 and Alembic history must resolve in this exact schema.
    # A schema is provisioned by its owner, never silently created here.
    connection.execute(text(f'SET LOCAL search_path TO {quoted_schema}, pg_catalog'))
    if connection.execute(text('SELECT current_schema()')).scalar_one() != schema:
        raise ValueError('Approved warehouse schema is absent or inaccessible')
    others = connection.execute(text("SELECT n.nspname FROM pg_class c JOIN pg_namespace n "
        "ON n.oid=c.relnamespace WHERE c.relname='alembic_version' AND c.relkind='r' "
        "AND n.nspname<>:schema"), {'schema': schema}).scalars().all()
    if others:
        raise ValueError('Alembic history exists outside selected schema; review before moving it')
    context.configure(connection=connection, version_table_schema=schema)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    supplied = config.attributes.get('connection')
    if supplied is not None:
        migrate(supplied)
    else:
        engine = create_engine(url, hide_parameters=True, echo=False)
        try:
            with engine.begin() as connection:
                migrate(connection)
        finally:
            engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
