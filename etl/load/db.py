from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url

from etl.config import Settings


def database_url(value):
    """Use the declared psycopg2 driver even when SQLAlchemy defaults change."""
    url = make_url(value)
    return url.set(drivername="postgresql+psycopg2") if url.drivername == "postgresql" else url


def create_db_engine(settings: Settings) -> Engine:
    if make_url(settings.database_url).get_backend_name() == "postgresql" and not settings.warehouse_schema:
        raise ValueError("Explicit WAREHOUSE_SCHEMA is required for PostgreSQL storage")
    engine = create_engine(
        database_url(settings.database_url),
        pool_pre_ping=True,
        future=True,
        hide_parameters=True,
        echo=False,
    )
    if settings.warehouse_schema:
        engine = engine.execution_options(schema_translate_map={None: settings.warehouse_schema})
    return engine


def check_database(engine: Engine) -> bool:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True
