import os
import json
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request
import requests

router = APIRouter(prefix="/banker")

# Bank API configuration
BANK_API_KEY = "sk-roG3OusRr0TLCHAADks6lw"
BANK_BASE_URL = "https://openai-hub.neuraldeep.tech"
LLM_MODEL = "gpt-4o-mini"

# Path to user data JSON file
USER_DATA_PATH = "as.json"

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
        "description": "Sharia-compliant Buy Now, Pay Later for small purchases, ideal for short-term financing needs."
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
        "description": "Flexible Sharia-compliant financing for medium to large expenses, such as business or personal needs."
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
        "description": "Long-term Sharia-compliant home financing for purchasing property."
    },
    {
        "name": "Копилка",
        "type": "инвестиционный",
        "expected_return": "до 18%",
        "max_amount_tenge": 20_000_000,
        "min_amount_tenge": 1_000,
        "min_term_months": 1,
        "max_term_months": 12,
        "description": "Short-term Sharia-compliant investment product for small to medium savings with attractive returns."
    },
    {
        "name": "Вакала",
        "type": "инвестиционный",
        "expected_return": "до 20%",
        "max_amount_tenge": "не ограничена",
        "min_amount_tenge": 50_000,
        "min_term_months": 3,
        "max_term_months": 36,
        "description": "Sharia-compliant investment product for higher returns, suitable for larger investments."
    }
]

def load_user_data() -> Dict[str, Any]:
    """Load user data from JSON file."""
    if not os.path.exists(USER_DATA_PATH):
        raise FileNotFoundError(f"User data file not found at {USER_DATA_PATH}")
    with open(USER_DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_llm_prompt(user_query: str, user_data: Dict[str, Any], products: list) -> str:
    """Generate a prompt for the LLM based on user query, data, and available products."""
    products_str = json.dumps(products, ensure_ascii=False, indent=2)
    user_data_str = json.dumps(user_data, ensure_ascii=False, indent=2)
    
    prompt = f"""
    You are a helpful Sharia-compliant banker assistant. Your role is to answer customer questions about banking services, suggest suitable products based on the user's data, and provide accurate information.

    User Data:
    {user_data_str}

    Available Products:
    {products_str}

    User Query: {user_query}

    Respond in a friendly, professional manner. If the query is about products, suggest only those that match the user's age, needs, and financial situation from the available products. Explain why the product fits. If the query is general, provide informative answers. Always ensure responses are Sharia-compliant and ethical.

    Response should be in Russian if the query is in Russian, otherwise in English.
    """
    return prompt

def call_llm_api(prompt: str) -> str:
    """Call the LLM API to get a response."""
    headers = {
        "Authorization": f"Bearer {BANK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.7
    }
    response = requests.post(f"{BANK_BASE_URL}/v1/chat/completions", headers=headers, json=payload)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="LLM API error")
    
    data = response.json()
    return data['choices'][0]['message']['content'].strip()

@router.post("/")
async def handle_query(request: Request) -> Dict[str, str]:
    """Endpoint to handle customer queries and respond using LLM."""
    try:
        body = await request.json()
        user_query = body.get("text")
        
        if not user_query:
            raise HTTPException(status_code=400, detail="Missing 'text' in request body")
        
        user_data = load_user_data()
        prompt = generate_llm_prompt(user_query, user_data, BANK_PRODUCTS)
        reply = call_llm_api(prompt)
        
        return {"reply": reply}
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

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

# Helper function to call Bank's LLM API for service suggestions with user data and optional query
def call_llm_api_for_services(user_data: Dict[str, Any], query: str = "") -> str:
    # Extract relevant fields from user_data
    goal = user_data.get("goal", {}).get("target_amount", 1000000)
    current_savings = user_data.get("goal", {}).get("current_amount", 0)
    user_age = user_data.get("age", 30)  # Default to 30 if not provided
    monthly_income = user_data.get("monthly_income", 0)
    transactions = []
    for key in ["transactions1", "transactions2", "transactions3Current"]:
        transactions.extend(user_data.get(key, []))
    subscriptions = user_data.get("subscriptions", [])
# Filter products based on user age
    eligible_products = [
        product for product in BANK_PRODUCTS
        if ('min_age' not in product or user_age >= product['min_age']) and
           ('max_age' not in product or user_age <= product['max_age'])
    ]
    
    if query:
        # Custom query prompt (suggest one product)
        prompt = (
            "As a helpful banker specializing in Islamic finance, analyze the user's financial data as of October 19, 2025, 01:24 +05, focusing on the following query: '{query}'.\n"
            "Select exactly one Sharia-compliant banking service from the following list that best matches the user's needs based on their spending patterns, financial goal, savings, age, and income:\n"
            f"{json.dumps(eligible_products, indent=2, ensure_ascii=False)}\n\n"
            "Consider the following:\n"
            "- Match the product to the query and user's needs (e.g., financing for large expenses like housing, investments for savings growth).\n"
            "- Ensure the product aligns with Islamic principles (no Riba, ethical investments, Zakat encouragement).\n"
            "- For 'what-if' scenarios (e.g., taking a mortgage), evaluate affordability based on monthly income, expenses, and savings.\n"
            f"User's financial goal: {goal} tenge. Current savings: {current_savings} tenge. User age: {user_age} years. Monthly income: {monthly_income} tenge.\n"
            f"Transactions: {json.dumps(transactions, indent=2, ensure_ascii=False)}\n"
            f"Subscriptions: {json.dumps(subscriptions, indent=2)}\n\n"
            "Output in clear, structured text:\n"
            "- Name the recommended product.\n"
            "- Explain why this product is the best fit for the query and user's situation, referencing their data.\n"
            "- Calculate progress toward the goal (as a percentage) and any relevant affordability metrics.\n"
            "- End with a brief motivational message encouraging ethical financial behavior and Zakat."
            "Отвечай только на русском языке!"
        ).format(query=query)
    else:
        # Default prompt (suggest 3-5 products)
        prompt = (
            "As a helpful banker specializing in Islamic finance, analyze the user's transactions, financial goal, and savings as of October 19, 2025, 01:24 +05.\n"
            "Suggest 3-5 Sharia-compliant banking services from the following list, tailoring recommendations to the user's spending patterns, goal, and savings:\n"
            f"{json.dumps(eligible_products, indent=2, ensure_ascii=False)}\n\n"
            "Consider the following:\n"
            "- Match services to the user's needs (e.g., financing for large expenses, investments for savings growth).\n"
            "- Ensure suggestions align with Islamic principles (no Riba, ethical investments, Zakat encouragement).\n"
            "- Calculate progress toward the goal and include motivational advice.\n"
            f"User's financial goal: {goal} tenge. Current savings: {current_savings} tenge. User age: {user_age} years. Monthly income: {monthly_income} tenge.\n"
            f"Transactions: {json.dumps(transactions, indent=2, ensure_ascii=False)}\n\n"
            "Output in clear, structured text: list 3-5 specific service suggestions with brief explanations, ending with encouragement."
            "Отвечай только на русском языке!"
        )
    
    headers = {
        "Authorization": f"Bearer {BANK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a knowledgeable banker focused on Islamic finance, providing personalized, Sharia-compliant service recommendations in a friendly manner."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    response = requests.post(f"{BANK_BASE_URL}/v1/chat/completions", headers=headers, json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Error calling LLM API: {response.text}")
    
    return response.json()["choices"][0]["message"]["content"]

# API Endpoint for Banker suggestions, accepting only query
@router.post("/suggest-services")
async def suggest_services(request: Request):
    try:
        data = await request.json()
        query = data.get("query", "")  # Optional user text query
        
        # Load user data from file
        user_data = load_user_data()
        
        # Get LLM suggestions
        suggestions_text = call_llm_api_for_services(user_data, query)
        
        # Response structure with only text field
        response = {
            "reply": suggestions_text
        }
        
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Run the app (for development, use uvicorn banker:app --reload)
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
