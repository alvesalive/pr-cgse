from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class ProductBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    preco_atual: float

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: UUID
    anexo_url: Optional[str] = None

    class Config:
        from_attributes = True
