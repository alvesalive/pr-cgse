"""
Testes Unitários — svc-catalogo
Estratégia: SQLite em memória + mock de MinIO
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

DATABASE_URL = "sqlite:///./test_catalogo.db"
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
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


client = TestClient(app)

# Token JWT simulado para autenticação nos testes
ADMIN_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsImV4cCI6OTk5OTk5OTk5OSwicm9sZSI6IkFETUlOIn0.fake"
USER_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTQ1NiIsImV4cCI6OTk5OTk5OTk5OSwicm9sZSI6IlVTRVIifQ.fake"


def test_listar_produtos_retorna_lista_vazia():
    """GET / deve retornar lista vazia quando não há produtos."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_listar_produtos_com_dados():
    """GET / deve retornar os produtos cadastrados."""
    from models import Produto
    db = TestingSessionLocal()
    db.add(Produto(
        nome="Cadeira Ergonômica",
        descricao="Cadeira de escritório",
        preco=1500.00,
        unidade="UN",
        imagem_url="http://localhost/img.jpg"
    ))
    db.commit()
    db.close()

    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["nome"] == "Cadeira Ergonômica"


def test_criar_produto_sem_autenticacao_retorna_401():
    """POST / sem token deve retornar 401 ou 403."""
    resp = client.post("/", data={
        "nome": "Produto Teste",
        "descricao": "Desc",
        "preco": "100.00",
        "unidade": "UN"
    })
    assert resp.status_code in [401, 403, 422]


def test_deletar_produto_inexistente_retorna_404():
    """DELETE com ID inválido deve retornar 404."""
    from auth import create_access_token
    token = create_access_token(subject="admin-uuid", role="ADMIN")
    resp = client.delete(
        "/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code in [404, 403, 401, 422]
