from fastapi import FastAPI
from npc_analyst import router as analyst_router
from npc_banker import router as banker_router
from npc_support import router as support_router

app = FastAPI(
    title="Unified NPC Services",
    description="Объединенный сервер для NPC Analyst, Banker и Support",
    version="1.0.0"
)

# Добавляем роутеры
app.include_router(analyst_router)
app.include_router(banker_router)
app.include_router(support_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)