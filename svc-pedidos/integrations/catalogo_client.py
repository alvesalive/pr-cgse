import os
import httpx
from cache_utils import get_cache, set_cache

CATALOGO_API_URL = os.getenv("CATALOGO_API_URL", "http://svc-catalogo:8000")

async def fetch_catalog(token: str, force_refresh=False) -> list:
    """Consulta svc-catalogo puxando a base inteira, com Cache local no Redis embutido"""
    cache_key = "catalog_global_cache"
    
    if not force_refresh:
        cached = get_cache(cache_key)
        if cached:
            return cached

    # Header Forwarding
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CATALOGO_API_URL}/produtos", headers=headers, timeout=5.0)
        
        if response.status_code == 200:
            data = response.json()
            set_cache(cache_key, data, ex=300) # Expira em 5 mins
            return data
        else:
            raise Exception(f"Erro HTTP do Catálogo: {response.status_code} {response.text}")

async def validate_and_enrich_items(items_requested: list, token: str):
    catalogo = await fetch_catalog(token)
    catalogo_map = {str(p["id"]): p for p in catalogo}
    
    missing_ids = [str(item.product_id) for item in items_requested if str(item.product_id) not in catalogo_map]
    
    if missing_ids:
        # Se algum item faltar, força refresh pulando cache (novo produto recém cadastrado)
        catalogo = await fetch_catalog(token, force_refresh=True)
        catalogo_map = {str(p["id"]): p for p in catalogo}
        
    enriched_items = []
    total_amount = 0.0
    
    for item in items_requested:
        if str(item.product_id) not in catalogo_map:
            raise Exception(f"Produto {item.product_id} inexistente/inválido.")
            
        p_data = catalogo_map[str(item.product_id)]
        preco = float(p_data["preco_atual"])
        nome = p_data["nome"]
        qtde = item.quantity
        
        enriched_items.append({
            "product_id": str(item.product_id),
            "product_name": nome,
            "unit_price": preco,
            "quantity": qtde
        })
        
        total_amount += (preco * qtde)
        
    return total_amount, enriched_items
