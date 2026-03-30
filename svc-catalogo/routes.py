from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import httpx
import os

import schemas, models, storage, auth
import logging
from database import get_db

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(tags=["catalogo"])

@router.get("/produtos", response_model=List[schemas.ProductResponse])
def listar_produtos(
    db: Session = Depends(get_db),
    user_uuid: str = Depends(auth.get_current_user_uuid)
):
    """Pede UUID assinado (JWT) Privacy by Design para exibir catálogo"""
    try:
        logger.info(f"Listar produtos requisitado por: {user_uuid}")
        produtos = db.query(models.Product).all()
        return produtos
    except Exception as e:
        logger.error(f"Erro ao listar produtos: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao acessar banco de dados do catálogo")

@router.post("/produtos", response_model=schemas.ProductResponse, status_code=201)
def criar_produto(
    produto_in: schemas.ProductCreate,
    db: Session = Depends(get_db),
    user_uuid: str = Depends(auth.get_current_user_uuid)
):
    """Cadastra um novo bem no catálogo (requer autenticação JWT)"""
    produto = models.Product(
        nome=produto_in.nome,
        descricao=produto_in.descricao,
        preco_atual=produto_in.preco_atual
    )
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto

@router.put("/produtos/{id}", response_model=schemas.ProductResponse)
def atualizar_produto(
    id: str,
    produto_in: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    user_uuid: str = Depends(auth.get_current_user_uuid)
):
    produto = db.query(models.Product).filter(models.Product.id == id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    if produto_in.nome is not None:
        produto.nome = produto_in.nome
    if produto_in.descricao is not None:
        produto.descricao = produto_in.descricao
    if produto_in.preco_atual is not None:
        produto.preco_atual = produto_in.preco_atual
        
    db.commit()
    db.refresh(produto)
    return produto

@router.delete("/produtos/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_produto(
    id: str,
    db: Session = Depends(get_db),
    user_uuid: str = Depends(auth.get_current_user_uuid)
):
    produto = db.query(models.Product).filter(models.Product.id == id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
        
    # Verificar se produto existe em pedido
    svc_pedidos_url = os.getenv("PEDIDOS_API_URL", "http://svc-pedidos:8000")
    try:
        resp = httpx.get(f"{svc_pedidos_url}/check-produto/{id}", timeout=3.0)
        if resp.status_code == 200 and resp.json().get("exists", False):
            raise HTTPException(status_code=400, detail="Este produto consta em pedidos existentes e não pode ser apagado por segurança contratual.")
    except httpx.RequestError:
        pass # Se o serviço estiver fora, permite deletar ou loga erro. Nesse caso, vamos permitir ou assumir seguro.

    db.delete(produto)
    db.commit()
    return None

@router.post("/produtos/{id}/imagem", response_model=schemas.ProductResponse)
async def upload_imagem_produto(
    id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_uuid: str = Depends(auth.get_current_user_uuid)
):
    produto = db.query(models.Product).filter(models.Product.id == id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não listado")
    
    file_bytes = await file.read()
    safe_filename = f"{id}_{file.filename}"
    
    try:
        url = storage.upload_image(file_bytes, safe_filename, content_type=file.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    produto.anexo_url = url
    db.commit()
    db.refresh(produto)
    
    return produto
