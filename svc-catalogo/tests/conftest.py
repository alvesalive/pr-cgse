"""
conftest.py — Executado antes de qualquer import de teste.
1. Forca DATABASE_URL para SQLite (sem psycopg2)
2. Patcha o tipo UUID do PostgreSQL para ser compativel com SQLite
"""
import os
import uuid as _uuid

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_catalogo.db")
os.environ.setdefault("JWT_SECRET", "chave_secreta_jwt_super_segura")
os.environ.setdefault("MINIO_ENDPOINT", "localhost:9000")
os.environ.setdefault("MINIO_ACCESS_KEY", "test")
os.environ.setdefault("MINIO_SECRET_KEY", "test")

# Patch UUID para compatibilidade com SQLite (deve ocorrer antes do import de models.py)
from sqlalchemy import types as _sa_types
import sqlalchemy.dialects.postgresql as _pg_dialect


class _GUID(_sa_types.TypeDecorator):
    """Tipo UUID portatil: funciona com PostgreSQL e SQLite."""
    impl = _sa_types.String(36)
    cache_ok = True

    def __init__(self, as_uuid=True, **kw):
        self.as_uuid = as_uuid
        super().__init__(**kw)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if self.as_uuid:
            return _uuid.UUID(str(value))
        return str(value)


_pg_dialect.UUID = _GUID
