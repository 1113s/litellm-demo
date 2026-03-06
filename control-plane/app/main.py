from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.keys import router as keys_router
from app.api.models import router as models_router

app = FastAPI(
    title="LiteLLM Demo Control Plane",
    version="0.1.0",
    description="Control-plane REST API skeleton for OpenRouter-like demo.",
)

app.include_router(health_router, tags=["health"])
app.include_router(keys_router, prefix="/keys", tags=["keys"])
app.include_router(models_router, prefix="/models", tags=["models"])
