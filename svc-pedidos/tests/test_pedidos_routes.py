"""
Testes Unitários — svc-pedidos
Estratégia: SQLite em memória + mocks de RabbitMQ e LLM
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, AsyncMock
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import Base, get_db
import auth as auth_module

DATABASE_URL = "sqlite:///./test_pedidos.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

USER_UUID = "user-test-uuid-001"


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_user():
    return USER_UUID


def override_get_token():
    return "fake-token"


@pytest.fixture(autouse=True)
def setup_and_teardown():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[auth_module.get_current_user_uuid] = override_get_user
    app.dependency_overrides[auth_module.get_current_user_token] = override_get_token
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


client = TestClient(app)


# ── TESTES DE PEDIDOS ──────────────────────────────────────────

@patch("integrations.catalogo_client.validate_and_enrich_items", new_callable=AsyncMock)
@patch("messaging.publish_order_notification")
@patch("integrations.llm_client.classify_risk", new_callable=AsyncMock)
def test_criar_pedido_retorna_200_com_risco_analisando(mock_llm, mock_rabbit, mock_catalogo):
    """Criação de pedido deve ser imediata e retornar status ANALISANDO."""
    mock_catalogo.return_value = (500.00, [
        {"product_id": "abc-123", "product_name": "Monitor", "unit_price": 500.00, "quantity": 1}
    ])
    mock_llm.return_value = "BAIXO"
    mock_rabbit.return_value = None

    resp = client.post("/", json={"items": [{"product_id": "abc-123", "quantity": 1}]})
    assert resp.status_code == 200
    body = resp.json()
    assert body["risk_level"] == "ANALISANDO"
    assert body["status"] == "PROCESSADO"
    assert body["total_amount"] == 500.00


@patch("integrations.catalogo_client.validate_and_enrich_items", new_callable=AsyncMock)
@patch("messaging.publish_order_notification")
@patch("integrations.llm_client.classify_risk", new_callable=AsyncMock)
def test_listar_pedidos_retorna_lista(mock_llm, mock_rabbit, mock_catalogo):
    """GET / deve retornar os pedidos do usuário logado."""
    mock_catalogo.return_value = (100.0, [
        {"product_id": "prod-1", "product_name": "Caneta", "unit_price": 100.0, "quantity": 1}
    ])
    mock_llm.return_value = "BAIXO"
    mock_rabbit.return_value = None

    client.post("/", json={"items": [{"product_id": "prod-1", "quantity": 1}]})
    resp = client.get("/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1


@patch("integrations.catalogo_client.validate_and_enrich_items", new_callable=AsyncMock)
@patch("messaging.publish_order_notification")
@patch("integrations.llm_client.classify_risk", new_callable=AsyncMock)
def test_deletar_pedido_existente_retorna_204(mock_llm, mock_rabbit, mock_catalogo):
    """DELETE de pedido existente deve retornar 204 e publicar evento."""
    mock_catalogo.return_value = (200.0, [
        {"product_id": "prod-2", "product_name": "Mesa", "unit_price": 200.0, "quantity": 1}
    ])
    mock_llm.return_value = "MEDIO"
    mock_rabbit.return_value = None

    create_resp = client.post("/", json={"items": [{"product_id": "prod-2", "quantity": 1}]})
    pedido_id = create_resp.json()["id"]

    del_resp = client.delete(f"/{pedido_id}")
    assert del_resp.status_code == 204
    mock_rabbit.assert_called()


def test_deletar_pedido_inexistente_retorna_404():
    """DELETE de ID inválido deve retornar 404."""
    resp = client.delete("/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_check_produto_sem_pedido_retorna_false():
    """check-produto de produto sem pedido deve retornar exists=false."""
    resp = client.get("/check-produto/produto-nao-existe")
    assert resp.status_code == 200
    assert resp.json()["exists"] == False


@patch("integrations.catalogo_client.validate_and_enrich_items", new_callable=AsyncMock)
@patch("messaging.publish_order_notification")
@patch("integrations.llm_client.classify_risk", new_callable=AsyncMock)
def test_check_produto_com_pedido_retorna_true(mock_llm, mock_rabbit, mock_catalogo):
    """check-produto de produto que está em algum pedido deve retornar exists=true."""
    pid = "produto-em-pedido"
    mock_catalogo.return_value = (300.0, [
        {"product_id": pid, "product_name": "Produto X", "unit_price": 300.0, "quantity": 1}
    ])
    mock_llm.return_value = "ALTO"
    mock_rabbit.return_value = None

    client.post("/", json={"items": [{"product_id": pid, "quantity": 1}]})
    resp = client.get(f"/check-produto/{pid}")
    assert resp.status_code == 200
    assert resp.json()["exists"] == True
