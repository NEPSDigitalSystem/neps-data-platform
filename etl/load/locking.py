"""Transaction-scoped identity locks for concurrent PostgreSQL writers."""
import hashlib

from sqlalchemy import func, select


def lock_identity(connection, namespace, key):
    if connection.dialect.name == "postgresql":
        value = hashlib.sha256((namespace + ":" + key).encode()).digest()[:8]
        connection.execute(select(func.pg_catalog.pg_advisory_xact_lock(int.from_bytes(value, "big", signed=True))))
