import os
import httpx
import asyncio

GEMINI_API_KEY = os.getenv("LLM_API_KEY", "")
GEMINI_MODEL = "gemini-3.0-flash"

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

    max_retries = 3
    base_delay = 1.0

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, timeout=20.0)
                resp.raise_for_status()
                data = resp.json()
                
                if "candidates" in data and data["candidates"]:
                    answer = data["candidates"][0]["content"]["parts"][0]["text"].strip().upper()
                    for valid in ["BAIXO", "MEDIO", "ALTO"]:
                        if valid in answer:
                            return valid
                
                print(f"[LLM] Resposta inesperada: {data}")
                return "DESCONHECIDO"
        except (httpx.TimeoutException, httpx.RequestError) as e:
            print(f"[LLM] Erro de rede (Tentativa {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(base_delay * (2 ** attempt)) # Exponential backoff
            else:
                print("[LLM] Máximo de tentativas alcançado. Processamento falhou.")
                return "TIMEOUT"
        except Exception as e:
            print(f"[LLM] Erro Google AI Studio (Outro erro): {e}")
            return "DESCONHECIDO"
            
    return "TIMEOUT"
