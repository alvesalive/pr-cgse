"""
conftest.py — Executado antes de qualquer import de teste.
1. Forca DATABASE_URL para SQLite (sem psycopg2)
2. Patcha o tipo UUID do PostgreSQL para ser compativel com SQLite
   (SQLite armazena UUID como string; o dialeto PostgreSQL espera uuid.UUID)
"""
import os
import uuid as _uuid

# Variaveis de ambiente — DEVEM ser definidas antes de qualquer import dos servicos
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_pedidos.db")
os.environ.setdefault("JWT_SECRET", "chave_secreta_jwt_super_segura")
os.environ.setdefault("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("CATALOGO_API_URL", "http://localhost:8001")
os.environ.setdefault("LLM_API_KEY", "fake-key-for-tests")

# ── Patch de UUID para SQLite ──────────────────────────────────────────────────
# O tipo UUID(as_uuid=True) do dialeto PostgreSQL chama .hex() nos valores,
# mas o SQLite devolve strings. Este patch substitui o tipo por uma versao
# compativel com ambos os bancos ANTES que models.py seja importado.
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
        if isinstance(value, _uuid.UUID):
            return str(value)
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if self.as_uuid:
            return _uuid.UUID(str(value))
        return str(value)


# Substitui o UUID do modulo postgresql pelo nosso tipo portatil.
# Como conftest.py carrega antes da coleta dos testes (e antes do import de models.py),
# qualquer `from sqlalchemy.dialects.postgresql import UUID` vai pegar o _GUID.
_pg_dialect.UUID = _GUID
