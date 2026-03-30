from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json

import schemas, models, auth, messaging
from cache_utils import get_cache, set_cache
from database import get_db
from integrations import catalogo_client, llm_client

router = APIRouter(tags=["pedidos"])

@router.post("/", response_model=schemas.OrderResponse)
async def criar_pedido(
    payload: schemas.OrderCreate,
    db: Session = Depends(get_db),
    user_uuid: str = Depends(auth.get_current_user_uuid),
    raw_token: str = Depends(auth.get_current_user_token)
):
    try:
        total, items_enriquecidos = await catalogo_client.validate_and_enrich_items(payload.items, raw_token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    risco = await llm_client.classify_risk(total, items_enriquecidos)
    
    novo_pedido = models.Order(
        user_uuid=user_uuid,
        status="PROCESSADO",
        risk_level=risco,
        total_amount=total
    )
    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)
    
    for item in items_enriquecidos:
        order_item = models.OrderItem(
            order_id=novo_pedido.id,
            product_id=item["product_id"],
            product_name=item["product_name"],
            unit_price=item["unit_price"],
            quantity=item["quantity"]
        )
        db.add(order_item)
    
    db.commit()
    db.refresh(novo_pedido)
    
    messaging.publish_order_notification(user_uuid, str(novo_pedido.id), novo_pedido.status, total)
    
    # Store fully populated schema dump cache logic
    pedido_resp = schemas.OrderResponse.model_validate(novo_pedido)
    set_cache(f"order_{novo_pedido.id}", json.loads(pedido_resp.model_dump_json()), ex=600)
    
    return novo_pedido


@router.get("/{id}", response_model=schemas.OrderResponse)
def obter_pedido(
    id: str,
    db: Session = Depends(get_db),
    user_uuid: str = Depends(auth.get_current_user_uuid)
):
    cached = get_cache(f"order_{id}")
    if cached:
        if cached.get("user_uuid") == user_uuid:
            return cached
        raise HTTPException(status_code=403, detail="Não pertence a voce")
             
    pedido = db.query(models.Order).filter(models.Order.id == id, models.Order.user_uuid == user_uuid).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido ausente")
        
    schema_dump = schemas.OrderResponse.model_validate(pedido).model_dump_json()
    set_cache(f"order_{pedido.id}", json.loads(schema_dump), ex=600)
    
    return pedido

@router.get("/", response_model=List[schemas.OrderResponse])
def listar_pedidos_do_user(
    db: Session = Depends(get_db),
    user_uuid: str = Depends(auth.get_current_user_uuid)
):
    return db.query(models.Order).filter(models.Order.user_uuid == user_uuid).all()
