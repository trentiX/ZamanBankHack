import os
import json
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request
import requests


router = APIRouter(prefix="/support")

# Bank API configuration
BANK_API_KEY = "API-KEY"
BANK_BASE_URL = "https://openai-hub.neuraldeep.tech"
LLM_MODEL = "gpt-4o-mini"

# Predefined bank products database
BANK_PRODUCTS = [
    {
        "name": "BNPL (рассрочка)",
        "type": "финансирование",
        "markup_tenge": "от 300",
        "max_amount_tenge": 300_000,
        "min_amount_tenge": 10_000,
        "min_term_months": 1,
        "max_term_months": 12,
        "min_age": 18,
        "max_age": 63,
        "description": "Sharia-compliant Buy Now, Pay Later для небольших покупок с коротким сроком финансирования."
    },
    {
        "name": "Исламское финансирование",
        "type": "финансирование",
        "markup_tenge": "от 6,000",
        "max_amount_tenge": 5_000_000,
        "min_amount_tenge": 100_000,
        "min_term_months": 3,
        "max_term_months": 60,
        "min_age": 18,
        "max_age": 60,
        "description": "Гибкое финансирование по принципам шариата для средних и крупных расходов."
    },
    {
        "name": "Исламская ипотека",
        "type": "финансирование",
        "markup_tenge": "от 200,000",
        "max_amount_tenge": 75_000_000,
        "min_amount_tenge": 3_000_000,
        "min_term_months": 12,
        "max_term_months": 240,
        "min_age": 25,
        "max_age": 60,
        "description": "Долгосрочное финансирование жилья по принципам шариата."
    },
    {
        "name": "Копилка",
        "type": "инвестиционный",
        "expected_return": "до 18%",
        "max_amount_tenge": 20_000_000,
        "min_amount_tenge": 1_000,
        "min_term_months": 1,
        "max_term_months": 12,
        "description": "Краткосрочный инвестиционный продукт по шариату с привлекательной доходностью."
    },
    {
        "name": "Вакала",
        "type": "инвестиционный",
        "expected_return": "до 20%",
        "max_amount_tenge": "не ограничена",
        "min_amount_tenge": 50_000,
        "min_term_months": 3,
        "max_term_months": 36,
        "description": "Инвестиционный продукт по шариату для высоких доходов, подходит для крупных вложений."
    }
]

@router.post("/ask-banker")
async def handle_support_query(request: Request) -> Dict[str, Any]:
    """
    Endpoint to handle general questions about Islamic banking, terms, products, and services.
    Uses LLM to generate Sharia-compliant responses based on predefined bank products.
    """
    try:
        # Parse incoming request
        data = await request.json()
        user_query = data.get("text", "").strip()
        if not user_query:
            raise HTTPException(status_code=400, detail="No query provided in 'text' field.")

        # Prepare the prompt for the LLM
        system_prompt = """
You are a helpful support agent NPC for an Islamic bank. Answer user questions about Islamic banking principles, terms, products, services, and related topics in a Sharia-compliant, friendly, and informative manner.
Provide accurate information based on Islamic finance rules (e.g., no riba/interest, focus on profit-sharing, asset-backed transactions).
If the question relates to bank products, use the following predefined products database for reference.
Always respond concisely, clearly, and politely.

Bank Products Database (JSON):
{products_json}
""".format(products_json=json.dumps(BANK_PRODUCTS, indent=2, ensure_ascii=False))

        user_prompt = f"User Question: {user_query}"

        # Prepare headers and payload for the LLM API
        headers = {
            "Authorization": f"Bearer {BANK_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        # Send request to the LLM API
        llm_response = requests.post(
            f"{BANK_BASE_URL}/v1/chat/completions",
            headers=headers,
            json=payload
        )

        if llm_response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"LLM API error: {llm_response.status_code} - {llm_response.text}"
            )

        # Parse LLM response
        result = llm_response.json()
        reply = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        if not reply:
            raise HTTPException(status_code=500, detail="Empty response from LLM.")

        # Return the reply in the expected format
        return {"reply": reply}

    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

