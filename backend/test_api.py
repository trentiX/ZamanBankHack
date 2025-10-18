import requests
import json
import os
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Bank API configuration
BANK_API_KEY = "sk-roG3OusRr0TLCHAADks6lw"
BANK_BASE_URL = "https://openai-hub.neuraldeep.tech"
LLM_MODEL = "gpt-4o-mini"

# Helper function to load transaction data from a JSON file in the same directory as the script
def load_transactions(filename: str) -> dict:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")
    file_path = os.path.join(script_dir, filename)
    print(f"Looking for file: {file_path}")
    
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise Exception(f"File {file_path} not found. Please place it in the same directory as this script.")
    except json.JSONDecodeError:
        raise Exception(f"Error decoding {file_path}. Ensure it contains valid JSON.")

# Function to call Bank's LLM API with goal, current balance, and transactions
def call_llm_api(transactions: dict, goal: float, current_balance: float) -> str:
    prompt = (
        "Analyze the following user transactions in a kind and supportive manner as of October 18, 2025, 16:58 +05. Provide insights on:\n"
        "- Where the money is being spent (categorize expenses).\n"
        "- Identify non-essential expenses on your own and suggest affordable or free alternatives.\n"
        "Consider Islamic finance principles: avoid interest-based transactions, promote ethical spending, and encourage savings for Zakat or charity.\n"
        f"The user's financial goal is {goal} rubles, and their current balance is {current_balance} rubles.\n"
        "Calculate how much is left to reach the goal and include positive motivation in your analysis.\n\n"
        f"Transactions: {json.dumps(transactions, indent=2)}\n\n"
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
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    response = requests.post(f"{BANK_BASE_URL}/v1/chat/completions", headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Error calling LLM API: {response.text}")
    
    return response.json()["choices"][0]["message"]["content"]

# Function to generate main Donut Chart using Matplotlib (distribution by categories only)
def generate_main_donut_chart(transactions: list) -> str:
    category_totals = {}
    for tx in transactions:
        category = tx.get("category", "Uncategorized")
        amount = float(tx.get("amount", 0))
        category_totals[category] = category_totals.get(category, 0) + amount
    
    if not category_totals:
        raise ValueError("No transactions to generate chart.")
    
    labels = list(category_totals.keys())
    sizes = list(category_totals.values())
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.3), textprops={'fontsize': 10})
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    ax.set_title('Main Expense Distribution by Categories (Oct 2025)')
    
    # Save to base64
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)
    plt.close()
    main_donut_base64 = base64.b64encode(buf.read()).decode("utf-8")
    
    # Optionally save as file for testing
    with open("main_donut_chart.png", "wb") as f:
        f.write(base64.b64decode(main_donut_base64))
    print("\nMain Donut chart saved as 'main_donut_chart.png' and base64 generated.")
    
    return main_donut_base64

# Function to generate separate Donut Charts for each category using Matplotlib
def generate_category_donut_charts(transactions: list) -> dict:
    # Group by category
    category_groups = {}
    for tx in transactions:
        category = tx.get("category", "Uncategorized")
        if category not in category_groups:
            category_groups[category] = []
        category_groups[category].append(tx)
    
    charts = {}
    for category, txs in category_groups.items():
        # Group by description for sub-details
        desc_totals = {}
        for tx in txs:
            desc = tx.get("description", "Uncategorized")
            amount = float(tx.get("amount", 0))
            desc_totals[desc] = desc_totals.get(desc, 0) + amount
        
        if not desc_totals:
            continue
        
        labels = list(desc_totals.keys())
        sizes = list(desc_totals.values())
        
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie(sizes, labels=labels, autopct=lambda pct: f'{pct:.1f}%\n({int(pct * sum(sizes) / 100):d} RUB)', startangle=90, wedgeprops=dict(width=0.3), textprops={'fontsize': 8})
        ax.axis('equal')
        ax.set_title(f'{category} Expense Details (Oct 2025)')
        
        # Save to base64
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches='tight')
        buf.seek(0)
        plt.close()
        charts[category] = base64.b64encode(buf.read()).decode("utf-8")
        
        # Optionally save as file for testing
        with open(f"{category}_donut_chart.png", "wb") as f:
            f.write(base64.b64decode(charts[category]))
        print(f"\n{category} Donut chart saved as '{category}_donut_chart.png' and base64 generated.")
    
    return charts

# Main test function
def test_simple_api(filename: str):
    try:
        print(f"Loading transactions from {filename}...")
        data = load_transactions(filename)
        
        # Extract transactions and current_balance (default to 0 if not provided)
        transactions = data.get("transactions", [])
        current_balance = data.get("current_savings", 0)  # Use "current_savings" from JSON or 0
        goal = 1000000  # Fixed goal of 1,000,000 rubles
        
        print("Loaded data:")
        print(json.dumps(data, indent=2))
        
        print("\nSending to LLM for analysis...")
        analysis_text = call_llm_api(data, goal, current_balance)
        
        print("\nLLM Analysis:")
        print(analysis_text)
        
        # Generate main Donut Chart (by categories only)
        print("\nGenerating Main Donut Chart...")
        main_donut_base64 = generate_main_donut_chart(transactions)
        print("\nMain Donut Chart Base64 (for WebGL/OpenGL):")
        print(main_donut_base64[:100] + "...")
        
        # Generate separate Donut Charts for each category
        print("\nGenerating Category Donut Charts...")
        category_donut_base64 = generate_category_donut_charts(transactions)
        for category, base64_str in category_donut_base64.items():
            print(f"\n{category} Donut Chart Base64 (for WebGL/OpenGL):")
            print(base64_str[:100] + "...")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_simple_api("user_full_banking_data.json")