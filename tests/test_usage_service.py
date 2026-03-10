import asyncio
import logging

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.models import Base
from app.db.session import get_db_session
from app.main import app


@pytest.fixture
def client_with_usage_db() -> TestClient:
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_local = async_sessionmaker(bind=test_engine, expire_on_commit=False)

    async def override_db():
        async with session_local() as session:
            yield session

    async def prepare():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.execute(
                text(
                    """
                    CREATE TABLE "LiteLLM_SpendLogs" (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      api_key TEXT,
                      model TEXT,
                      custom_llm_provider TEXT,
                      status TEXT,
                      prompt_tokens INTEGER,
                      completion_tokens INTEGER,
                      spend REAL,
                      "startTime" TEXT
                    )
                    """
                )
            )
            await conn.execute(
                text(
                    """
                    INSERT INTO "LiteLLM_SpendLogs"
                    (api_key, model, custom_llm_provider, status, prompt_tokens, completion_tokens, spend, "startTime")
                    VALUES
                    ('tenant-a', 'router/default-fast', 'openai', 'success', 10, 20, 0.12, '2026-03-06T00:00:00'),
                    ('tenant-a', 'router/default-fast', 'openai', 'failure', 5, 0, 0.03, '2026-03-06T01:00:00'),
                    ('tenant-b', 'router/default-balanced', 'anthropic', 'success', 8, 16, 0.22, '2026-03-06T02:00:00')
                    """
                )
            )

    asyncio.run(prepare())
    app.dependency_overrides[get_db_session] = override_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    asyncio.run(test_engine.dispose())


@pytest.fixture
def client_without_usage_table() -> TestClient:
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_local = async_sessionmaker(bind=test_engine, expire_on_commit=False)

    async def override_db():
        async with session_local() as session:
            yield session

    async def prepare():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(prepare())
    app.dependency_overrides[get_db_session] = override_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    asyncio.run(test_engine.dispose())


def test_usage_summary_aggregate(client_with_usage_db: TestClient) -> None:
    resp = client_with_usage_db.get("/api/admin/usage/summary?tenant=tenant-a&model=router/default-fast&provider=openai")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["request_count"] == 2
    assert data["success_count"] == 1
    assert data["error_count"] == 1
    assert data["total_input_tokens"] == 15
    assert data["total_output_tokens"] == 20
    assert data["total_spend"] == pytest.approx(0.15)


def test_usage_summary_missing_table_returns_readable_error(
    client_without_usage_table: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.WARNING)
    resp = client_without_usage_table.get("/api/admin/usage/summary")
    assert resp.status_code == 404
    assert "does not exist" in resp.json()["error"]["message"]
    assert "usage summary skipped: table LiteLLM_SpendLogs does not exist" in caplog.text

