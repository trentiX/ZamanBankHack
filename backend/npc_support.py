import os
import json
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request
import requests


router = APIRouter(prefix="/support")
# FastAPI app setup for General Islamic Banking Q&A Agent
# app = FastAPI(
#     title="Islamic Banking Q&A Agent",
#     description="Backend for an NPC Banker to answer general questions about Islamic banking and bank services in a Sharia-compliant manner.",
#     version="1.0.0"
# )

# Bank API configuration
BANK_API_KEY = "sk-roG3OusRr0TLCHAADks6lw"
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

# Helper function to call Bank's LLM API for general Islamic banking questions
def call_llm_api_for_qa(query: str) -> str:
    prompt = (
        "Ты эксперт по исламскому банкингу, работающий в банке, который предлагает продукты, соответствующие принципам шариата. "
        "Дата и время: 19 октября 2025, 04:44 +05. Отвечай на русском языке на вопрос пользователя: '{query}'.\n\n"
        "Учитывай следующее:\n"
        "- Объясняй принципы исламского банкинга (запрет риба, этичные инвестиции, поддержка закята) при необходимости.\n"
        "- Если вопрос касается продуктов банка, ссылайся на следующий список:\n"
        f"{json.dumps(BANK_PRODUCTS, indent=2, ensure_ascii=False)}\n"
        "- Отвечай кратко, структурированно, не более 150 слов.\n"
        "- Если вопрос неясен, дай общий ответ о преимуществах исламского банкинга.\n"
        "- Завершай ответ мотивацией к этичному финансовому поведению.\n\n"
        "Формат ответа:\n"
        "- Основной ответ на вопрос.\n"
        "- Краткое упоминание, как это связано с шариатом (если применимо).\n"
        "- Мотивация к ответственному финансовому поведению."
    ).format(query=query)

    headers = {
        "Authorization": f"Bearer {BANK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "Ты эксперт по исламскому банкингу, предоставляющий точные и лаконичные ответы на русском языке."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 150,
        "temperature": 0.7
    }

    try:
        response = requests.post(f"{BANK_BASE_URL}/v1/chat/completions", headers=headers, json=payload)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Ошибка вызова LLM API: {response.text}")
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки запроса: {str(e)}")

# API Endpoint for general Islamic banking questions
@router.post("/ask-banker")
async def ask_banker(request: Request):
    try:
        data = await request.json()
        query = data.get("query", "")  # User question about Islamic banking or bank services
        
        if not query:
            raise HTTPException(status_code=400, detail="Не предоставлен запрос (query).")

        # Get LLM response
        answer = call_llm_api_for_qa(query)

        # Response structure
        response = {
            "reply": answer
        }

        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Неверный формат запроса: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

# # Run the app (for development, use uvicorn banker:app --reload)
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)