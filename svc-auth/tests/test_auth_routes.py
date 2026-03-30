"""
Testes Unitários — svc-auth
Estratégia: SQLite em memória (sem Postgres) + TestClient do FastAPI
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import Base, get_db

# ── Banco de testes em memória ─────────────────────────────────
DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Cria e destroi as tabelas antes/depois de cada teste."""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


client = TestClient(app)


# ── TESTES DE REGISTRO ─────────────────────────────────────────

def test_register_primeiro_usuario_vira_admin():
    """O primeiro usuário a se registrar deve receber role ADMIN."""
    resp = client.post("/register", json={
        "nome_completo": "Admin Teste",
        "email": "admin@test.com",
        "password": "senha123"
    })
    assert resp.status_code == 201
    assert resp.json()["role"] == "ADMIN"


def test_register_segundo_usuario_vira_user():
    """O segundo usuário deve receber role USER."""
    client.post("/register", json={
        "nome_completo": "Admin",
        "email": "admin@test.com",
        "password": "senha123"
    })
    resp = client.post("/register", json={
        "nome_completo": "Cidadão Teste",
        "email": "user@test.com",
        "password": "senha456"
    })
    assert resp.status_code == 201
    assert resp.json()["role"] == "USER"


def test_register_email_duplicado_retorna_400():
    """Cadastro com e-mail já existente deve retornar 400."""
    client.post("/register", json={
        "nome_completo": "Admin",
        "email": "dup@test.com",
        "password": "senha123"
    })
    resp = client.post("/register", json={
        "nome_completo": "Outro",
        "email": "dup@test.com",
        "password": "outrasenha"
    })
    assert resp.status_code == 400
    assert "uso" in resp.json()["detail"].lower()


def test_register_retorna_token():
    """Registro deve retornar access_token e token_type."""
    resp = client.post("/register", json={
        "nome_completo": "Token Test",
        "email": "token@test.com",
        "password": "senha123"
    })
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


# ── TESTES DE LOGIN ────────────────────────────────────────────

def test_login_credenciais_validas():
    """Login com credenciais corretas deve retornar 200 e um token."""
    client.post("/register", json={
        "nome_completo": "Login User",
        "email": "login@test.com",
        "password": "minha_senha"
    })
    resp = client.post("/login", json={
        "email": "login@test.com",
        "password": "minha_senha"
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_senha_errada_retorna_401():
    """Login com senha errada deve retornar 401."""
    client.post("/register", json={
        "nome_completo": "Senha Errada",
        "email": "wrong@test.com",
        "password": "certa"
    })
    resp = client.post("/login", json={
        "email": "wrong@test.com",
        "password": "errada"
    })
    assert resp.status_code == 401


def test_login_email_inexistente_retorna_401():
    """Login com e-mail não cadastrado deve retornar 401."""
    resp = client.post("/login", json={
        "email": "naoexiste@test.com",
        "password": "qualquer"
    })
    assert resp.status_code == 401
