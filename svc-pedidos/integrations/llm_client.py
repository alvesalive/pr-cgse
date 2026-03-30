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
    prompt = (
        f"Você é o RiskEngine do sistema governamental PR-CGSE. "
        f"Analise este pedido público e responda SOMENTE UMA PALAVRA entre: BAIXO, MEDIO ou ALTO.\n\n"
        f"Valor Total: R$ {total_amount:.2f}\n"
        f"Itens:\n{prompt_lines}\n\n"
        f"Resposta (apenas uma palavra):"
    )

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 10,
            "temperature": 0.1
        }
    }

    max_retries = 5
    base_delay = 5.0

    for attempt in range(max_retries):
        try:
            print(f"[LLM] Chamando {GEMINI_MODEL} (Tentativa {attempt+1}/5)...")
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, timeout=60.0)
                resp.raise_for_status()
                data = resp.json()
                
                if "candidates" in data and data["candidates"]:
                    answer = data["candidates"][0]["content"]["parts"][0]["text"].strip().upper()
                    for valid in ["BAIXO", "MEDIO", "ALTO"]:
                        if valid in answer:
                            print(f"[LLM] Resultado: {valid}")
                            return valid
                
                print(f"[LLM] Resposta inesperada: {data}")
        except (httpx.TimeoutException, httpx.RequestError) as e:
            print(f"[LLM] Erro de rede/API: {e}")
            if attempt < max_retries - 1:
                sleep_time = base_delay * (2 ** attempt)
                print(f"[LLM] Aguardando {sleep_time}s para redefinir...")
                await asyncio.sleep(sleep_time)
            else:
                return "TIMEOUT"
        except Exception as e:
            print(f"[LLM] Erro critico Google AI: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(base_delay)
            else:
                return "DESCONHECIDO"
            
    return "TIMEOUT"
