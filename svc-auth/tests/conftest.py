"""
conftest.py — Executado antes de qualquer import de teste.
Força DATABASE_URL para SQLite para que database.py não tente usar psycopg2.
"""
import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_auth.db")
os.environ.setdefault("JWT_SECRET", "chave_secreta_jwt_super_segura")
