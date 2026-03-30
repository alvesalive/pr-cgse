import uuid
from sqlalchemy import Column, String, Float
from sqlalchemy.dialects.postgresql import UUID
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(String, nullable=True)
    preco_atual = Column(Float, nullable=False)
    anexo_url = Column(String(500), nullable=True)
