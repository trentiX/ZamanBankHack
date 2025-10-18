import os
import json
import base64
from typing import Dict, List, Any
from fastapi import FastAPI, HTTPException, Request
import requests
import matplotlib.pyplot as plt
from io import BytesIO

app = FastAPI(
    title="Transaction Analysis Backend",
    description="Backend for analyzing user transactions and generating challenges, loading user data from a JSON file.",
    version="1.0.0"
)

BANK_API_KEY = "sk-roG3OusRr0TLCHAADks6lw"
BANK_BASE_URL = "https://openai-hub.neuraldeep.tech"
LLM_MODEL = "gpt-4o-mini"
USER_DATA_FILE = "user_full_banking_data_with_subscription_usage.json"

# Load user data from JSON file
def load_user_data(file_path: str = USER_DATA_FILE) -> Dict[str, Any]:
    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail=f"User data file {file_path} not found.")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading user data: {str(e)}")

# Helper function to call Bank's LLM API
def call_llm_api(user_data: Dict[str, Any], query: str = "") -> Dict[str, Any]:
    goal = user_data.get("goal", {}).get("target_amount", 1000000)
    current_savings = user_data.get("goal", {}).get("current_amount", 0)
    transactions = []
    for key in ["transactions1", "transactions2", "transactions3Current"]:
        transactions.extend(user_data.get(key, []))
    subscriptions = user_data.get("subscriptions", [])

    if query:
        prompt = (
            f"Analyze the user's financial data in a kind and supportive manner as of October 18, 2025, 23:07 +05, focusing on the following query: '{query}'.\n"
            "Provide insights based on the data provided.\n"
            "- For monthly comparisons: Group expenses by month, compare last month (October 2025) to previous month (September 2025), highlight changes in categories, prices, or patterns, and provide a small challenge to improve spending in one category (e.g., 'Let's try to spend 20% less on taxis this month'). Include the target amount for the challenge (e.g., reduce taxi spending to X RUB).\n"
            "Consider Islamic finance principles: avoid interest-based transactions, promote ethical spending, and encourage savings for Zakat or charity.\n"
            f"The user's financial goal is {goal} rubles, and their current savings is {current_savings} rubles.\n"
            "Output in clear, structured JSON format with fields:\n"
            "- analysis: Text of the analysis.\n"
            "- challenge: { text: string, target_amount: number, category: string } (if applicable, otherwise null).\n"
            "- goal_progress: Percentage progress toward the goal.\n"
            f"Full user data: {json.dumps(user_data, indent=2)}\n\n"
            "End the analysis text with encouragement."
        )
    else:
        prompt = (
            "Analyze the following user transactions in a kind and supportive manner as of October 18, 2025, 23:07 +05. Provide insights on:\n"
            "- Where the money is being spent (categorize expenses).\n"
            "- Identify non-essential expenses and suggest affordable or free alternatives.\n"
            "Consider Islamic finance principles: avoid interest-based transactions, promote ethical spending, and encourage savings for Zakat or charity.\n"
            f"The user's financial goal is {goal} rubles, and their current savings is {current_savings} rubles.\n"
            "Output in clear, structured JSON format with fields:\n"
            "- analysis: Text of the analysis.\n"
            "- challenge: null\n"
            "- goal_progress: Percentage progress toward the goal.\n"
            f"Transactions: {json.dumps(transactions, indent=2)}\n\n"
            "End the analysis text with encouragement."
        )
    
    headers = {
        "Authorization": f"Bearer {BANK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a kind-hearted but professional financial analyst specializing in personal finance and Islamic principles."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1500,
        "temperature": 0.7
    }

    try:
        response = requests.post(f"{BANK_BASE_URL}/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return json.loads(response.json()["choices"][0]["message"]["content"])
    except requests.exceptions.RequestException as e:
        return {"analysis": f"Error calling LLM API: {str(e)}", "challenge": None, "goal_progress": 0}

# Generate main donut chart
def generate_main_donut_chart(transactions: List[Dict[str, Any]]) -> str:
    category_totals = {}
    for tx in transactions:
        category = tx.get("category", "Uncategorized")
        amount = abs(float(tx.get("amount", 0)))
        category_totals[category] = category_totals.get(category, 0) + amount
    
    if not category_totals:
        return None
    
    labels = list(category_totals.keys())
    sizes = list(category_totals.values())
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.3), textprops={'fontsize': 10})
    ax.axis('equal')
    ax.set_title('Main Expense Distribution by Categories (Recent Months)')
    
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return base64.b64encode(buf.read()).decode("utf-8")

# Generate category-specific donut charts
def generate_category_donut_charts(transactions: List[Dict[str, Any]]) -> Dict[str, str]:
    category_groups = {}
    for tx in transactions:
        category = tx.get("category", "Uncategorized")
        if category not in category_groups:
            category_groups[category] = []
        category_groups[category].append(tx)
    
    charts = {}
    for category, txs in category_groups.items():
        desc_totals = {}
        for tx in txs:
            desc = tx.get("description", "Uncategorized")
            amount = abs(float(tx.get("amount", 0)))
            desc_totals[desc] = desc_totals.get(desc, 0) + amount
        
        if not desc_totals:
            continue
        
        labels = list(desc_totals.keys())
        sizes = list(desc_totals.values())
        
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie(sizes, labels=labels, autopct=lambda pct: f'{pct:.1f}%\n({int(pct * sum(sizes) / 100):d} RUB)', startangle=90, wedgeprops=dict(width=0.3), textprops={'fontsize': 8})
        ax.axis('equal')
        ax.set_title(f'{category} Expense Details (Recent Months)')
        
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches='tight')
        buf.seek(0)
        plt.close()
        charts[category] = base64.b64encode(buf.read()).decode("utf-8")
    
    return charts

# Calculate challenge progress
def calculate_challenge_progress(user_data: Dict[str, Any], challenge: Dict[str, Any]) -> float:
    if not challenge or not challenge.get("category") or not challenge.get("target_amount"):
        return 0.0
    
    category = challenge["category"]
    target_amount = challenge["target_amount"]
    
    current_month_expenses = 0
    for tx in user_data.get("transactions3Current", []):
        if tx.get("category") == category:
            current_month_expenses += abs(float(tx.get("amount", 0)))
    
    if current_month_expenses <= target_amount:
        progress = (1 - current_month_expenses / target_amount) * 100 if target_amount > 0 else 100
    else:
        progress = 0
    return min(max(progress, 0), 100)

# API endpoint
@app.post("/analyze")
async def analyze(request: Request):
    try:
        data = await request.json()
        query = data.get("query", "")
        
        # Load user data from file
        user_data = load_user_data()
        
        # Get LLM analysis
        result = call_llm_api(user_data, query)
        
        # Combine transactions for charts
        transactions = []
        for key in ["transactions1", "transactions2", "transactions3Current"]:
            transactions.extend(user_data.get(key, []))
        
        # Generate charts
        main_donut_base64 = generate_main_donut_chart(transactions) if transactions else None
        category_donut_base64 = generate_category_donut_charts(transactions) if transactions else {}
        
        # Calculate challenge progress
        challenge_progress = calculate_challenge_progress(user_data, result.get("challenge", None))
        
        # Response
        response = {
            "analysis": result["analysis"],
            "challenge": result["challenge"],
            "goal_progress": result["goal_progress"],
            "challenge_progress": challenge_progress,
            "main_chart": main_donut_base64,
            "category_charts": category_donut_base64
        }
        
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)