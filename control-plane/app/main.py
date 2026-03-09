from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.admin.resources import router as admin_router
from app.api.health import router as health_router
from app.core.errors import http_exception_handler, integrity_error_handler, unhandled_exception_handler
from app.core.redis_client import redis_client
from app.db.models import Tenant
from app.db.session import SessionLocal, engine

logger = logging.getLogger(__name__)


async def _seed_default_tenant() -> None:
    """Ensure a default tenant exists after Alembic migrations have run."""
    async with SessionLocal() as session:
        result = await session.execute(select(Tenant).where(Tenant.name == "default"))
        if result.scalar_one_or_none() is None:
            try:
                session.add(Tenant(id="00000000-0000-0000-0000-000000000001", name="default", status="active"))
                await session.commit()
            except IntegrityError:
                await session.rollback()
                logger.info("default tenant already exists (concurrent insert)")


@asynccontextmanager
async def lifespan(_: FastAPI):
    await _seed_default_tenant()
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
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
