from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from npc_analyst import router as analyst_router
from npc_banker import router as banker_router
from npc_support import router as support_router

app = FastAPI(
    title="Unified NPC Services",
    description="Объединенный сервер для NPC Analyst, Banker и Support",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Можешь потом заменить на конкретный домен
    allow_credentials=True,
    allow_methods=["*"],  # <-- Важно для OPTIONS и POST
    allow_headers=["*"],  # <-- ВАЖНО!!!
)

# Добавляем роутеры
app.include_router(analyst_router)
app.include_router(banker_router)
app.include_router(support_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
