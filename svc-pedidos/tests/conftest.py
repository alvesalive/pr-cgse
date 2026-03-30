"""
conftest.py — Executado antes de qualquer import de teste.
Força DATABASE_URL para SQLite para que database.py não tente usar psycopg2.
"""
import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_pedidos.db")
os.environ.setdefault("JWT_SECRET", "chave_secreta_jwt_super_segura")
os.environ.setdefault("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("CATALOGO_API_URL", "http://localhost:8001")
os.environ.setdefault("LLM_API_KEY", "fake-key-for-tests")
