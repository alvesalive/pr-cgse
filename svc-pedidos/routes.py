from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import json, asyncio, logging

import schemas, models, auth, messaging
from cache_utils import get_cache, set_cache
from database import get_db, SessionLocal
from integrations import catalogo_client, llm_client

router = APIRouter(tags=["pedidos"])
logger = logging.getLogger(__name__)


async def _atualizar_risco_background(order_id: str, total: float, items_enriquecidos: list):
    """Tarefa assíncrona: classifica risco via LLM e persiste resultado."""
    try:
        risco = await llm_client.classify_risk(total, items_enriquecidos)
        logger.info(f"[BG] Risco classificado para {order_id}: {risco}")
    except Exception as e:
        logger.error(f"[BG] Erro LLM para {order_id}: {e}")
        risco = "TIMEOUT"

    db = SessionLocal()
    try:
        order = db.query(models.Order).filter(models.Order.id == order_id).first()
        if order:
            order.risk_level = risco
            db.commit()
            db.refresh(order)
            pedido_resp = schemas.OrderResponse.model_validate(order)
            set_cache(f"order_{order_id}", json.loads(pedido_resp.model_dump_json()), ex=600)
            logger.info(f"[BG] Order {order_id} atualizado com risco={risco}")
    finally:
        db.close()


@router.post("/", response_model=schemas.OrderResponse)
async def criar_pedido(
    payload: schemas.OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_uuid: str = Depends(auth.get_current_user_uuid),
    raw_token: str = Depends(auth.get_current_user_token)
):
    try:
        total, items_enriquecidos = await catalogo_client.validate_and_enrich_items(payload.items, raw_token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Salva o pedido imediatamente com risco pendente — retorna rápido ao frontend
    novo_pedido = models.Order(
        user_uuid=user_uuid,
        status="PROCESSADO",
        risk_level="ANALISANDO",
        total_amount=total
    )
    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)

    for item in items_enriquecidos:
        db.add(models.OrderItem(
            order_id=novo_pedido.id,
            product_id=item["product_id"],
            product_name=item["product_name"],
            unit_price=item["unit_price"],
            quantity=item["quantity"]
        ))

    db.commit()
    db.refresh(novo_pedido)

    messaging.publish_order_notification(user_uuid, str(novo_pedido.id), novo_pedido.status, total)

    # Background: chama LLM e atualiza o pedido quando concluir
    background_tasks.add_task(_atualizar_risco_background, str(novo_pedido.id), total, items_enriquecidos)

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
        raise HTTPException(status_code=403, detail="Não pertence a você")

    pedido = db.query(models.Order).filter(models.Order.id == id, models.Order.user_uuid == user_uuid).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido ausente")

    set_cache(f"order_{pedido.id}", json.loads(schemas.OrderResponse.model_validate(pedido).model_dump_json()), ex=600)
    return pedido


@router.get("/", response_model=List[schemas.OrderResponse])
def listar_pedidos_do_user(
    db: Session = Depends(get_db),
    user_uuid: str = Depends(auth.get_current_user_uuid)
):
    return db.query(models.Order).filter(models.Order.user_uuid == user_uuid).order_by(models.Order.created_at.desc()).all()

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_pedido(
    id: str,
    db: Session = Depends(get_db),
    user_uuid: str = Depends(auth.get_current_user_uuid)
):
    pedido = db.query(models.Order).filter(models.Order.id == id, models.Order.user_uuid == user_uuid).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido ausente ou sem permissão")

    # Guardar dados antes de deletar
    total = pedido.total_amount
    
    db.delete(pedido)
    db.commit()
    
    # Invalida cache e notifica rabbitmq
    cache_key = f"order_{id}"
    get_cache(cache_key) # placeholder import safe logic
    # Em redis real poderiamos usar delete. Aqui o get_cache nao deleta, omitindo redis flush por demo, setando null
    set_cache(cache_key, None, ex=1) 
    
    messaging.publish_order_notification(user_uuid, id, "CANCELADO_EXCLUIDO", total, event_type="ORDER_DELETED")
    return None

@router.put("/{id}", response_model=schemas.OrderResponse)
async def atualizar_pedido(
    id: str,
    payload: schemas.OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_uuid: str = Depends(auth.get_current_user_uuid),
    raw_token: str = Depends(auth.get_current_user_token)
):
    pedido = db.query(models.Order).filter(models.Order.id == id, models.Order.user_uuid == user_uuid).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido ausente ou sem permissão")

    try:
        total, items_enriquecidos = await catalogo_client.validate_and_enrich_items(payload.items, raw_token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Limpa itens antigos
    db.query(models.OrderItem).filter(models.OrderItem.order_id == id).delete()
    
    pedido.total_amount = total
    pedido.risk_level = "ANALISANDO"
    
    # Adiciona novos itens
    for item in items_enriquecidos:
        db.add(models.OrderItem(
            order_id=pedido.id,
            product_id=item["product_id"],
            product_name=item["product_name"],
            unit_price=item["unit_price"],
            quantity=item["quantity"]
        ))
        
    db.commit()
    db.refresh(pedido)
    
    # Invalida/Atualiza cache
    cache_key = f"order_{id}"
    set_cache(cache_key, json.loads(schemas.OrderResponse.model_validate(pedido).model_dump_json()), ex=600)
    
    # RabbitMQ Event
    messaging.publish_order_notification(user_uuid, id, "ALTERADO", total, event_type="ORDER_UPDATED")
    
    # Re-avalia risco em background
    background_tasks.add_task(_atualizar_risco_background, str(pedido.id), total, items_enriquecidos)

    return pedido

@router.get("/check-produto/{produto_id}")
def check_produto(produto_id: str, db: Session = Depends(get_db)):
    """Verifica se um produto existe em algum pedido (usado internamente pelo svc-catalogo)"""
    existe = db.query(models.OrderItem).filter(models.OrderItem.product_id == produto_id).first() is not None
    return {"exists": existe}
