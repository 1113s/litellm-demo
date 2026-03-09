from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.api.admin.resources import router as admin_router
from app.api.health import router as health_router
from app.api.models import router as models_router
from app.core.errors import http_exception_handler, unhandled_exception_handler
from app.core.redis_client import redis_client
from app.db.session import engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await redis_client.aclose()
    await engine.dispose()


app = FastAPI(
    title="LiteLLM Demo Control Plane",
    version="0.1.0",
    description="Control-plane REST API skeleton for OpenRouter-like demo.",
    lifespan=lifespan,
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])

app.include_router(models_router, prefix="/api/models", tags=["models"])
