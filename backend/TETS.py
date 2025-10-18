import json
import base64
from typing import Dict, List, Any
import requests
import matplotlib.pyplot as plt
from io import BytesIO

# Bank API configuration
BANK_API_KEY = "sk-roG3OusRr0TLCHAADks6lw"
BANK_BASE_URL = "https://openai-hub.neuraldeep.tech"
LLM_MODEL = "gpt-4o-mini"

# Load user data from JSON file
def load_user_data(file_path: str) -> Dict[str, Any]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise ValueError(f"Error loading user data: {str(e)}")

# Helper function to call Bank's LLM API with user data and optional query
def call_llm_api(user_data: Dict[str, Any], query: str = "") -> str:
    # Extract relevant fields from user_data
    goal = user_data.get("goal", {}).get("target_amount", 1000000)
    current_savings = user_data.get("goal", {}).get("current_amount", 0)
    transactions = []
    for key in ["transactions1", "transactions2", "transactions3Current"]:
        transactions.extend(user_data.get(key, []))
    subscriptions = user_data.get("subscriptions", [])

    if query:
        # Custom query prompt
        prompt = (
            f"Analyze the user's financial data in a kind and supportive manner as of October 18, 2025, 19:56 +05, focusing on the following query: '{query}'.\n"
            "Provide insights based on the data provided.\n"
            "- For subscription analysis: Identify which subscriptions are used (based on usage_timestamps, usage_count, last_used, not_used_in_last_90_days) and suggest cancellations for unused ones.\n"
            "- For monthly comparisons: Group expenses by month, compare last month (October 2025) to previous month (September 2025), highlight changes in categories, prices, or patterns, and provide a small challenge to improve spending in one non-essential category.\n"
            "Consider Islamic finance principles: avoid interest-based transactions, promote ethical spending, and encourage savings for Zakat or charity.\n"
            f"The user's financial goal is {goal} rubles, and their current savings is {current_savings} rubles.\n"
            "Calculate how much is left to reach the goal and include positive motivation.\n\n"
            f"Full user data: {json.dumps(user_data, indent=2)}\n\n"
            "Output in clear, structured text, ending with encouragement."
        )
    else:
        # Default prompt
        prompt = (
            "Analyze the following user transactions in a kind and supportive manner as of October 18, 2025, 19:56 +05. Provide insights on:\n"
            "- Where the money is being spent (categorize expenses).\n"
            "- Identify non-essential expenses on your own and suggest affordable or free alternatives.\n"
            "Consider Islamic finance principles: avoid interest-based transactions, promote ethical spending, and encourage savings for Zakat or charity.\n"
            f"The user's financial goal is {goal} rubles, and their current savings is {current_savings} rubles.\n"
            "Calculate how much is left to reach the goal and include positive motivation in your analysis.\n\n"
            f"Transactions: {json.dumps(transactions, indent=2)}\n"
            f"Subscriptions: {json.dumps(subscriptions, indent=2)}\n\n"
            "Output in clear, structured text, ending with encouragement."
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
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Error calling LLM API: {str(e)}"

# Function to generate main Donut Chart using Matplotlib
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

# Function to generate separate Donut Charts for each category
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

# Main function to analyze user data
def analyze_user_data(file_path: str, query: str = ""):
    try:
        # Load user data
        user_data = load_user_data(file_path)

        # Get LLM analysis
        analysis_text = call_llm_api(user_data, query)

        # Combine transactions for charts
        transactions = []
        for key in ["transactions1", "transactions2", "transactions3Current"]:
            transactions.extend(user_data.get(key, []))

        # Generate charts
        main_donut_base64 = generate_main_donut_chart(transactions) if transactions else None
        category_donut_base64 = generate_category_donut_charts(transactions) if transactions else {}

        # Save results
        result = {
            "analysis": analysis_text,
            "main_chart": main_donut_base64,
            "category_charts": category_donut_base64
        }

        # Print analysis
        print("=== Financial Analysis ===")
        print(result["analysis"])
        print("\n=== Charts Generated ===")
        print(f"Main Donut Chart: {'Generated' if main_donut_base64 else 'None'}")
        print(f"Category Donut Charts: {list(category_donut_base64.keys())}")

        # Save charts to files for inspection
        if main_donut_base64:
            with open("main_donut_chart.png", "wb") as f:
                f.write(base64.b64decode(main_donut_base64))
        for category, chart in category_donut_base64.items():
            with open(f"{category}_donut_chart.png", "wb") as f:
                f.write(base64.b64decode(chart))

        return result

    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        return None

# Test the script with a monthly comparison query to check for challenge
if __name__ == "__main__":
    # Path to the user data JSON file
    FILE_PATH = "Project/user_full_banking_data.json"

    # Test: Monthly expense comparison with challenge
    print("\n=== Test: Monthly Expense Comparison with Challenge ===")
    analyze_user_data(FILE_PATH, "Compare my expenses in October 2025 with September 2025."
                      )