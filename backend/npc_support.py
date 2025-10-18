# consultant.py

import os
import json
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request
import requests

# FastAPI app setup for General Consultant NPC
app = FastAPI(
    title="Bank Consultant Backend",
    description="Backend for NPC Consultant to answer general questions about the bank and Islamic financing.",
    version="1.0.0"
)

# Bank API configuration
BANK_API_KEY = "sk-roG3OusRr0TLCHAADks6lw"
BANK_BASE_URL = "https://openai-hub.neuraldeep.tech"
LLM_MODEL = "gpt-4o-mini"

# Helper function to call Bank's LLM API for general questions
def call_llm_api_for_questions(question: str) -> str:
    prompt = (
        f"Answer the following question about Zaman Bank or Islamic financing in a clear, informative, and friendly manner as of October 18, 2025.\n"
        "Focus on Islamic principles: no interest (Riba), ethical investments, Sharia compliance, Zakat, etc.\n"
        "If the question is about the bank, describe services like Sharia-compliant accounts, financing, investments, and consultations.\n"
        "Keep responses concise, structured, and encouraging.\n\n"
        f"Question: {question}"
    )
    
    headers = {
        "Authorization": f"Bearer {BANK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful consultant for Zaman Bank, expert in Islamic finance, providing accurate and supportive answers."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 600,
        "temperature": 0.7
    }
    
    response = requests.post(f"{BANK_BASE_URL}/v1/chat/completions", headers=headers, json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Error calling LLM API: {response.text}")
    
    return response.json()["choices"][0]["message"]["content"]

# API Endpoint for general questions
@app.post("/answer-question")
async def answer_question(request: Request):
    try:
        data = await request.json()
        question = data.get("question", "")
        
        if not question:
            raise HTTPException(status_code=400, detail="No question provided.")
        
        # Get LLM response
        answer_text = call_llm_api_for_questions(question)
        
        # Response structure for WebGL game
        response = {
            "answer": answer_text
        }
        
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Run the app (for development, use uvicorn consultant:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)  # Different port to avoid conflict