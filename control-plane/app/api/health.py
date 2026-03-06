from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.core.redis_client import redis_client
from app.db.session import SessionLocal

router = APIRouter()


@router.get("/healthz")
async def healthz() -> dict[str, str]:
    try:
        async with SessionLocal() as session:
            await session.execute(text("SELECT 1"))
        await redis_client.ping()
    except Exception as exc:  # pragma: no cover - defensive branch
        raise HTTPException(status_code=503, detail="dependency check failed") from exc

    return {"status": "ok"}
