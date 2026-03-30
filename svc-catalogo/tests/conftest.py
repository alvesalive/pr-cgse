"""
conftest.py — Executado antes de qualquer import de teste.
Força DATABASE_URL para SQLite para que database.py não tente usar psycopg2.
"""
import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_catalogo.db")
os.environ.setdefault("JWT_SECRET", "chave_secreta_jwt_super_segura")
os.environ.setdefault("MINIO_ENDPOINT", "localhost:9000")
os.environ.setdefault("MINIO_ACCESS_KEY", "test")
os.environ.setdefault("MINIO_SECRET_KEY", "test")
