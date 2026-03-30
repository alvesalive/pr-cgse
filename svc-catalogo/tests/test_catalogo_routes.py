"""
Testes Unitarios — svc-catalogo
Estrategia: SQLite em memoria + mocks de MinIO e svc-pedidos
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import Base, get_db
from models import Product  # nome real da classe no models.py

DATABASE_URL = "sqlite:///./test_catalogo.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_user():
    return "user-test-uuid"


@pytest.fixture(autouse=True)
def setup_and_teardown():
    Base.metadata.create_all(bind=engine)
    from auth import get_current_user_uuid
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_uuid] = override_get_user
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


client = TestClient(app)


# ── TESTES DE SAÚDE ────────────────────────────────────────────

def test_health_check_retorna_ok():
    """GET / deve retornar status ok."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# ── TESTES DE LISTAGEM ─────────────────────────────────────────

def test_listar_produtos_retorna_lista_vazia():
    """GET /produtos deve retornar lista vazia quando nao ha produtos."""
    resp = client.get("/produtos")
    assert resp.status_code == 200
    assert resp.json() == []


def test_listar_produtos_com_dados():
    """GET /produtos deve retornar os produtos cadastrados."""
    db = TestingSessionLocal()
    db.add(Product(
        nome="Cadeira Ergonomica",
        descricao="Cadeira de escritorio",
        preco_atual=1500.00,
    ))
    db.commit()
    db.close()

    resp = client.get("/produtos")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["nome"] == "Cadeira Ergonomica"


# ── TESTES DE CRIAÇÃO ──────────────────────────────────────────

def test_criar_produto_com_autenticacao():
    """POST /produtos com autenticacao deve criar o produto."""
    resp = client.post("/produtos", json={
        "nome": "Monitor 4K",
        "descricao": "Monitor ultra-wide",
        "preco_atual": 3500.00
    })
    assert resp.status_code == 201
    assert resp.json()["nome"] == "Monitor 4K"


def test_criar_produto_sem_autenticacao_retorna_401():
    """POST /produtos sem token deve retornar 401."""
    # Remove o override de autenticacao para esse teste
    app.dependency_overrides.clear()
    resp = client.post("/produtos", json={
        "nome": "Produto Sem Auth",
        "descricao": "Desc",
        "preco_atual": 100.00
    })
    assert resp.status_code in [401, 403]


# ── TESTES DE DELECAO ──────────────────────────────────────────

@patch("httpx.get")
def test_deletar_produto_sem_pedido_retorna_204(mock_httpx):
    """DELETE produto que nao esta em pedido deve retornar 204."""
    mock_httpx.return_value = MagicMock(status_code=200, json=lambda: {"exists": False})

    db = TestingSessionLocal()
    p = Product(nome="Para Deletar", descricao="Teste", preco_atual=10.00)
    db.add(p)
    db.commit()
    produto_id = str(p.id)
    db.close()

    resp = client.delete(f"/produtos/{produto_id}")
    assert resp.status_code == 204


@patch("httpx.get")
def test_deletar_produto_em_pedido_retorna_400(mock_httpx):
    """DELETE produto que esta em pedido deve retornar 400."""
    mock_httpx.return_value = MagicMock(status_code=200, json=lambda: {"exists": True})

    db = TestingSessionLocal()
    p = Product(nome="Em Pedido", descricao="Nao pode deletar", preco_atual=50.00)
    db.add(p)
    db.commit()
    produto_id = str(p.id)
    db.close()

    resp = client.delete(f"/produtos/{produto_id}")
    assert resp.status_code == 400


def test_deletar_produto_inexistente_retorna_404():
    """DELETE com ID invalido deve retornar 404."""
    resp = client.delete("/produtos/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
