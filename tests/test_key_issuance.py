import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.models import ApiKey, Base
from app.db.session import get_db_session
from app.main import app


@pytest.fixture
def client_with_db() -> TestClient:
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
    app.state.test_session_local = session_local

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    asyncio.run(test_engine.dispose())


class DummyResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self) -> dict:
        return self._payload


def test_create_key_success(client_with_db: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from app.core import litellm_client

    async def fake_post(self, url, json, headers):
        return DummyResponse(200, {"key": "sk-virtual-123", "id": "key-id-1"})

    monkeypatch.setattr(litellm_client.settings, "litellm_admin_key", "master-key")
    monkeypatch.setattr("httpx.AsyncClient.post", fake_post)

    tenant = client_with_db.post("/api/admin/tenants", json={"name": "tenant-k", "status": "active"}).json()["data"]

    resp = client_with_db.post(
        "/api/admin/keys",
        json={
            "tenant_id": tenant["id"],
            "display_name": "backend-service",
            "litellm_key_alias": "tenant-k-main",
            "allowed_models": ["router/default-fast"],
            "metadata_json": {"env": "test"},
        },
    )

    assert resp.status_code == 200
    body = resp.json()["data"]
    assert body["litellm_generated_key"] == "sk-virtual-123"
    assert body["allowed_models"] == ["router/default-fast"]


def test_create_key_rollback_on_litellm_failure(client_with_db: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from app.core import litellm_client

    async def fake_post(self, url, json, headers):
        return DummyResponse(500, {"error": "boom"})

    monkeypatch.setattr(litellm_client.settings, "litellm_admin_key", "master-key")
    monkeypatch.setattr("httpx.AsyncClient.post", fake_post)

    tenant = client_with_db.post("/api/admin/tenants", json={"name": "tenant-rb", "status": "active"}).json()["data"]

    resp = client_with_db.post(
        "/api/admin/keys",
        json={
            "tenant_id": tenant["id"],
            "display_name": "backend-service",
            "litellm_key_alias": "tenant-rb-main",
            "allowed_models": ["router/default-fast"],
            "metadata_json": {"env": "test"},
        },
    )

    assert resp.status_code == 502

    async def run_check() -> int:
        async with app.state.test_session_local() as session:
            rows = (await session.execute(select(ApiKey))).scalars().all()
            return len(rows)

    assert asyncio.run(run_check()) == 0
