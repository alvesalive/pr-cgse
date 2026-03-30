from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

import schemas, models, storage, auth
from database import get_db

router = APIRouter(tags=["catalogo"])

@router.get("/produtos", response_model=List[schemas.ProductResponse])
def listar_produtos(
    db: Session = Depends(get_db),
    user_uuid: str = Depends(auth.get_current_user_uuid)
):
    """Pede UUID assinado (JWT) Privacy by Design para exibir catálogo"""
    produtos = db.query(models.Product).all()
    return produtos

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
