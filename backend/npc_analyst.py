import os
import traceback
import json
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request
import requests

router = APIRouter(prefix="/analyst")

# Bank API configuration (using the same as Banker for consistency)
BANK_API_KEY = "sk-roG3OusRr0TLCHAADks6lw"
BANK_BASE_URL = "https://openai-hub.neuraldeep.tech"
LLM_MODEL = "gpt-4o-mini"

# Path to user data JSON file
USER_DATA_PATH = "user_full_banking_data_enriched.json"


@router.post("/analyze-finances")
async def analyze_finances(request: Request) -> Dict[str, Any]:
    """
    Endpoint to handle user queries for financial analysis.
    Analyzes the JSON file for non-essential expenses, suggests alternatives,
    compares expenses across months, and analyzes subscription usage.
    """
    try:
        # Parse incoming request
        data = await request.json()
        user_query = data.get("text", "").strip()
        if not user_query:
            raise HTTPException(status_code=400, detail="No query provided in 'text' field.")

        # Load user financial data from JSON file
        if not os.path.exists(USER_DATA_PATH):
            raise HTTPException(status_code=404, detail="User data file not found.")
        
        with open(USER_DATA_PATH, "r", encoding="utf-8") as f:
            user_data = json.load(f)

        # Prepare the prompt for the LLM
        system_prompt = """
You are a helpful financial analyst NPC. Analyze the provided user financial data.
Focus on:
- Identifying non-essential expenses (e.g., entertainment, dining out) and suggest cost-effective alternatives.
- Comparing expenses across different months (e.g., total spending, category breakdowns).
- Analyzing subscription usage: list active subscriptions, their costs, usage frequency, and suggest cancellations or optimizations if underused.
Adapt your response to the user's specific query if provided, but always include key insights from the data.
Respond concisely and clearly, in a friendly tone.
"""

        user_prompt = f"""
Financial Data (JSON):
{json.dumps(user_data, indent=2)}

User Query: {user_query}
"""

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
            "max_tokens": 1500
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
        analysis = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        if not analysis:
            raise HTTPException(status_code=500, detail="Empty response from LLM.")

        # Return the analysis in the expected format
        return {"analysis": analysis, "reply": analysis}  # Provide both for flexibility

    except HTTPException as he:
        raise he
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
# # Run the app (for development, use uvicorn analyst:app --reload)
# if __name__ == "main":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)  # Different port to avoid conflict with Banker
