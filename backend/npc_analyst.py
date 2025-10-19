import os
import json
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request
import requests

router = APIRouter(prefix="/analyst")

# FastAPI app setup for Financial Analyst NPC
# app = FastAPI(
#     title="Financial Analyst Backend",
#     description="Backend for NPC Financial Analyst to fully analyze user banking data from a file, provide insights, subscription info, monthly comparisons, and optional alternatives to non-essential expenses, adapting to user queries.",
#     version="1.0.0"
# )

# Bank API configuration (using the same as Banker for consistency)
BANK_API_KEY = "sk-roG3OusRr0TLCHAADks6lw"
BANK_BASE_URL = "https://openai-hub.neuraldeep.tech"
LLM_MODEL = "gpt-4o-mini"

# Path to user data JSON file
USER_DATA_PATH = "backend/user_full_banking_data.json"

# Helper function to load user data from JSON file
def load_user_data() -> Dict[str, Any]:
    try:
        if not os.path.exists(USER_DATA_PATH):
            raise HTTPException(status_code=500, detail=f"User data file not found at {USER_DATA_PATH}")
        with open(USER_DATA_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in user data file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading user data file: {str(e)}")

# Helper function to call Bank's LLM API for financial analysis with user data and optional query
def call_llm_api_for_analysis(user_data: Dict[str, Any], query: str = "") -> str:
    # Extract relevant fields from user_data
    goal_target = user_data.get("goal", {}).get("target_amount", 1000000)
    goal_current = user_data.get("goal", {}).get("current_amount", 0)
    user_age = user_data.get("age", 30)  # Default to 30 if not provided
    monthly_income = user_data.get("monthly_income", 0)
    transactions1 = user_data.get("transactions1", [])
    transactions2 = user_data.get("transactions2", [])
    transactions3_current = user_data.get("transactions3Current", [])
    subscriptions = user_data.get("subscriptions", [])
    
    # Base prompt parts
    base_analysis = (
        "Анализируйте транзакции за три периода (transactions1 - старый месяц, transactions2 - средний, transactions3Current - текущий), подписки, доходы, расходы и цель.\n"
        "Предоставьте insights: паттерны расходов, категории, избытки/дефициты.\n"
        "Информация о подписках: список, общая стоимость, рекомендации по отмене ненужных.\n"
        "Сравнение месяцев: общие расходы по периодам, избытки (доход - расходы), тенденции.\n"
        "Если запрос касается альтернатив ненужным тратам, предложите шариат-соответствующие альтернативы (этичные, без риба).\n"
        f"Финансовая цель: {goal_target} тенге. Текущие сбережения: {goal_current} тенге. Возраст: {user_age} лет. Ежемесячный доход: {monthly_income} тенге.\n"
        f"Транзакции1: {json.dumps(transactions1, indent=2, ensure_ascii=False)}\n"
        f"Транзакции2: {json.dumps(transactions2, indent=2, ensure_ascii=False)}\n"
        f"Транзакции3Current: {json.dumps(transactions3_current, indent=2, ensure_ascii=False)}\n"
        f"Подписки: {json.dumps(subscriptions, indent=2, ensure_ascii=False)}\n\n"
    )
    
    if query:
        # Custom query prompt: adapt output to the specific query
        prompt = (
            "Как полезный финансовый аналитик, специализирующийся на исламских финансах, проанализируйте финансовые данные пользователя на 19 октября 2025 года, 01:24 +05, адаптируя анализ под следующий запрос: '{query}'.\n"
            "Адаптируйте вывод: если запрос касается конкретных аспектов (например, анализ расходов в первом и втором месяцах, insights по ним; или только анализ подписок; или альтернативы тратам), фокусируйтесь на этих частях и опускайте нерелевантные разделы. Если запрос общий, предоставьте полный анализ.\n"
            + base_analysis +
            "Вывод в четком, структурированном тексте на русском языке, адаптированном под запрос:\n"
            "- Ключевые insights (если релевантно).\n"
"- Анализ подписок (если релевантно).\n"
            "- Сравнение месяцев (если релевантно).\n"
            "- Альтернативы тратам (если запрошено).\n"
            "- Прогресс к цели (в процентах) и мотивационное сообщение с упоминанием закята (если релевантно)."
        ).format(query=query)
    else:
        # Default prompt: full analysis
        prompt = (
            "Как полезный финансовый аналитик, специализирующийся на исламских финансах, полностью проанализируйте финансовые данные пользователя на 19 октября 2025 года, 01:24 +05.\n"
            + base_analysis +
            "Вывод в четком, структурированном тексте на русском языке:\n"
            "- Ключевые insights по расходам и паттернам.\n"
            "- Анализ подписок с рекомендациями.\n"
            "- Сравнение месяцев (расходы, избытки, тенденции).\n"
            "- Прогресс к цели (в процентах) и мотивационное сообщение с упоминанием закята и этичных финансов."
        )

    headers = {
        "Authorization": f"Bearer {BANK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a knowledgeable financial analyst focused on Islamic finance, providing detailed, personalized insights and advice in a friendly manner."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1500,  # Increased for more detailed analysis
        "temperature": 0.7
    }

    response = requests.post(f"{BANK_BASE_URL}/v1/chat/completions", headers=headers, json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Error calling LLM API: {response.text}")

    return response.json()["choices"][0]["message"]["content"]

# API Endpoint for Financial Analysis, accepting optional query
@router.post("/analyze-finances")
async def analyze_finances(request: Request):
    try:
        data = await request.json()
        query = data.get("query", "")  # Optional user text query

        # Load user data from file
        user_data = load_user_data()

        # Get LLM analysis
        analysis_text = call_llm_api_for_analysis(user_data, query)

        # Response structure with only text field
        response = {
            "reply": analysis_text
        }

        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# # Run the app (for development, use uvicorn analyst:app --reload)
# if __name__ == "main":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)  # Different port to avoid conflict with Banker