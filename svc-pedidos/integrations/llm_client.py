import os
import httpx
import asyncio

GEMINI_API_KEY = os.getenv("LLM_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"

async def classify_risk(total_amount: float, items: list) -> str:
    if not GEMINI_API_KEY:
        return "SEM_ANALISE"

    prompt_lines = "\n".join(
        f"- {item['quantity']}x {item['product_name']} a R$ {item['unit_price']:.2f}"
        for item in items
    )
    prompt = f"Responda apenas UMA PALAVRA (BAIXO, MEDIO ou ALTO). Risco do pedido R$ {total_amount:.2f}: {prompt_lines}"

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 100,
            "temperature": 0.1
        }
    }

    max_retries = 2
    base_delay = 45.0

    for attempt in range(max_retries):
        try:
            print(f"[LLM] Chamando {GEMINI_MODEL} (Tentativa {attempt+1}/2)...")
            #No SSl para demonstracao da LLM (apenas nessa chamada)
            async with httpx.AsyncClient(verify=False) as client:
                resp = await client.post(url, json=payload, timeout=60.0)
                resp.raise_for_status()
                data = resp.json()
                
                # Parsing resiliente
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        answer = parts[0].get("text", "").strip().upper()
                        for valid in ["BAIXO", "MEDIO", "ALTO"]:
                            if valid in answer:
                                print(f"[LLM] Resultado: {valid}")
                                return valid
                
                print(f"[LLM] Resposta inesperada: {data}")
        except (httpx.TimeoutException, httpx.RequestError) as e:
            print(f"[LLM] Erro de rede/API: {e}")
            if attempt < max_retries - 1:
                print(f"[LLM] Aguardando {base_delay}s para redefinir...")
                await asyncio.sleep(base_delay)
            else:
                return "TIMEOUT"
        except Exception as e:
            print(f"[LLM] Erro critico Google AI: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(base_delay)
            else:
                return "DESCONHECIDO"
            
    return "TIMEOUT"
