import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.models import Base
from app.db.session import get_db_session
from app.main import app


@pytest.fixture
def client() -> TestClient:
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_local = async_sessionmaker(bind=test_engine, expire_on_commit=False)

    async def override_db():
        async with session_local() as session:
            yield session

    async def prepare():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    import asyncio

    asyncio.run(prepare())
    app.dependency_overrides[get_db_session] = override_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    asyncio.run(test_engine.dispose())


def test_tenant_crud(client: TestClient) -> None:
    created = client.post("/api/admin/tenants", json={"name": "tenant-a", "status": "active"})
    assert created.status_code == 200
    tenant_id = created.json()["data"]["id"]

    listed = client.get("/api/admin/tenants")
    assert listed.status_code == 200
    assert len(listed.json()["data"]) == 1

    got = client.get(f"/api/admin/tenants/{tenant_id}")
    assert got.status_code == 200

    updated = client.put(f"/api/admin/tenants/{tenant_id}", json={"name": "tenant-b", "status": "active"})
    assert updated.status_code == 200
    assert updated.json()["data"]["name"] == "tenant-b"

    deleted = client.delete(f"/api/admin/tenants/{tenant_id}")
    assert deleted.status_code == 200


def test_provider_crud(client: TestClient) -> None:
    created = client.post("/api/admin/providers", json={"name": "openai", "base_url": None, "enabled": True})
    assert created.status_code == 200
    provider_id = created.json()["data"]["id"]

    listed = client.get("/api/admin/providers")
    assert listed.status_code == 200
    assert listed.json()["data"][0]["name"] == "openai"

    updated = client.put(
        f"/api/admin/providers/{provider_id}",
        json={"name": "openai-updated", "base_url": "https://api.openai.com", "enabled": True},
    )
    assert updated.status_code == 200

    deleted = client.delete(f"/api/admin/providers/{provider_id}")
    assert deleted.status_code == 200


def test_model_catalog_crud(client: TestClient) -> None:
    provider = client.post("/api/admin/providers", json={"name": "deepseek", "base_url": None, "enabled": True}).json()["data"]

    created = client.post(
        "/api/admin/model-catalog",
        json={
            "model_key": "router/default-fast",
            "display_name": "Default Fast",
            "provider_id": provider["id"],
            "upstream_model": "deepseek/deepseek-chat",
            "enabled": True,
        },
    )
    assert created.status_code == 200
    model_id = created.json()["data"]["id"]

    listed = client.get("/api/admin/model-catalog")
    assert listed.status_code == 200
    assert len(listed.json()["data"]) == 1

    updated = client.put(
        f"/api/admin/model-catalog/{model_id}",
        json={
            "model_key": "router/default-balanced",
            "display_name": "Default Balanced",
            "provider_id": provider["id"],
            "upstream_model": "deepseek/deepseek-reasoner",
            "enabled": True,
        },
    )
    assert updated.status_code == 200

    deleted = client.delete(f"/api/admin/model-catalog/{model_id}")
    assert deleted.status_code == 200


def test_route_policy_crud(client: TestClient) -> None:
    created = client.post(
        "/api/admin/route-policies",
        json={
            "policy_name": "default-fast-policy",
            "target_models": ["router/default-fast"],
            "fallback_models": ["router/default-balanced"],
            "strategy": "fallback",
            "weights": {},
        },
    )
    assert created.status_code == 200
    assert created.json()["data"]["strategy"] == "fallback"
    policy_id = created.json()["data"]["id"]

    listed = client.get("/api/admin/route-policies")
    assert listed.status_code == 200
    assert len(listed.json()["data"]) == 1

    updated = client.put(
        f"/api/admin/route-policies/{policy_id}",
        json={
            "policy_name": "default-fast-policy-v2",
            "target_models": ["router/default-fast", "router/default-balanced"],
            "fallback_models": ["router/default-balanced"],
            "strategy": "weighted",
            "weights": {"router/default-fast": 0.7, "router/default-balanced": 0.3},
        },
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["strategy"] == "weighted"

    deleted = client.delete(f"/api/admin/route-policies/{policy_id}")
    assert deleted.status_code == 200
