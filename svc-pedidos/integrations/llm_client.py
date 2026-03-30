import os
import httpx

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = "google/gemini-2.5-flash"

async def classify_risk(total_amount: float, items: list) -> str:
    if not LLM_API_KEY:
        return "SEM_ANALISE"
        
    prompt = f"Analise o pedido e classifique Nivel de Risco como BAIXO, MEDIO ou ALTO com base nas seguintes informacoes do Carrinho. Ticket Total: R$ {total_amount:.2f}. Itens:\n"
    for item in items:
        prompt += f"- {item['quantity']}x {item['product_name']} a R$ {item['unit_price']}\n"
    
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "Seu nome e PR-CGSE RiskEngine. Responda num fôlego, SOMENTE UMA PALAVRA das tres a seguir: BAIXO, MEDIO, ALTO."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=6.0)
            data = resp.json()
            if "choices" in data and len(data["choices"]) > 0:
                answer = data["choices"][0]["message"]["content"].strip().upper()
                for valid in ["BAIXO", "MEDIO", "ALTO"]:
                    if valid in answer:
                        return valid
            return "DESCONHECIDO"
    except Exception as e:
        print(f"Erro no AI Model Call (OpenRouter): {e}")
        return "TIMEOUT"
