from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ModelCatalog, Provider, RoutePolicy, Tenant
from app.db.session import get_db_session
from app.schemas.admin import (
    ModelCatalogCreate,
    ModelCatalogRead,
    ProviderCreate,
    ProviderRead,
    RoutePolicyCreate,
    RoutePolicyRead,
    TenantCreate,
    TenantRead,
)

router = APIRouter()


@router.post("/tenants")
async def create_tenant(payload: TenantCreate, db: AsyncSession = Depends(get_db_session)) -> dict:
    item = Tenant(name=payload.name, status=payload.status)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return {"data": TenantRead.model_validate(item, from_attributes=True).model_dump()}


@router.get("/tenants")
async def list_tenants(db: AsyncSession = Depends(get_db_session)) -> dict:
    rows = (await db.execute(select(Tenant).order_by(Tenant.created_at.desc()))).scalars().all()
    return {"data": [TenantRead.model_validate(x, from_attributes=True).model_dump() for x in rows]}


@router.get("/tenants/{tenant_id}")
async def get_tenant(tenant_id: str, db: AsyncSession = Depends(get_db_session)) -> dict:
    item = await db.get(Tenant, tenant_id)
    if not item:
        raise HTTPException(status_code=404, detail="tenant not found")
    return {"data": TenantRead.model_validate(item, from_attributes=True).model_dump()}


@router.put("/tenants/{tenant_id}")
async def update_tenant(tenant_id: str, payload: TenantCreate, db: AsyncSession = Depends(get_db_session)) -> dict:
    item = await db.get(Tenant, tenant_id)
    if not item:
        raise HTTPException(status_code=404, detail="tenant not found")
    item.name = payload.name
    item.status = payload.status
    await db.commit()
    await db.refresh(item)
    return {"data": TenantRead.model_validate(item, from_attributes=True).model_dump()}


@router.delete("/tenants/{tenant_id}")
async def delete_tenant(tenant_id: str, db: AsyncSession = Depends(get_db_session)) -> dict:
    item = await db.get(Tenant, tenant_id)
    if not item:
        raise HTTPException(status_code=404, detail="tenant not found")
    await db.delete(item)
    await db.commit()
    return {"data": {"id": tenant_id, "deleted": True}}


@router.post("/providers")
async def create_provider(payload: ProviderCreate, db: AsyncSession = Depends(get_db_session)) -> dict:
    item = Provider(**payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return {"data": ProviderRead.model_validate(item, from_attributes=True).model_dump()}


@router.get("/providers")
async def list_providers(db: AsyncSession = Depends(get_db_session)) -> dict:
    rows = (await db.execute(select(Provider).order_by(Provider.created_at.desc()))).scalars().all()
    return {"data": [ProviderRead.model_validate(x, from_attributes=True).model_dump() for x in rows]}


@router.put("/providers/{provider_id}")
async def update_provider(provider_id: str, payload: ProviderCreate, db: AsyncSession = Depends(get_db_session)) -> dict:
    item = await db.get(Provider, provider_id)
    if not item:
        raise HTTPException(status_code=404, detail="provider not found")
    for k, v in payload.model_dump().items():
        setattr(item, k, v)
    await db.commit()
    await db.refresh(item)
    return {"data": ProviderRead.model_validate(item, from_attributes=True).model_dump()}


@router.delete("/providers/{provider_id}")
async def delete_provider(provider_id: str, db: AsyncSession = Depends(get_db_session)) -> dict:
    item = await db.get(Provider, provider_id)
    if not item:
        raise HTTPException(status_code=404, detail="provider not found")
    await db.delete(item)
    await db.commit()
    return {"data": {"id": provider_id, "deleted": True}}


@router.post("/model-catalog")
async def create_model_catalog(payload: ModelCatalogCreate, db: AsyncSession = Depends(get_db_session)) -> dict:
    if not await db.get(Provider, payload.provider_id):
        raise HTTPException(status_code=404, detail="provider not found")
    item = ModelCatalog(**payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return {"data": ModelCatalogRead.model_validate(item, from_attributes=True).model_dump()}


@router.get("/model-catalog")
async def list_model_catalog(db: AsyncSession = Depends(get_db_session)) -> dict:
    rows = (await db.execute(select(ModelCatalog).order_by(ModelCatalog.created_at.desc()))).scalars().all()
    return {"data": [ModelCatalogRead.model_validate(x, from_attributes=True).model_dump() for x in rows]}


@router.put("/model-catalog/{model_id}")
async def update_model_catalog(model_id: str, payload: ModelCatalogCreate, db: AsyncSession = Depends(get_db_session)) -> dict:
    item = await db.get(ModelCatalog, model_id)
    if not item:
        raise HTTPException(status_code=404, detail="model not found")
    if not await db.get(Provider, payload.provider_id):
        raise HTTPException(status_code=404, detail="provider not found")
    for k, v in payload.model_dump().items():
        setattr(item, k, v)
    await db.commit()
    await db.refresh(item)
    return {"data": ModelCatalogRead.model_validate(item, from_attributes=True).model_dump()}


@router.delete("/model-catalog/{model_id}")
async def delete_model_catalog(model_id: str, db: AsyncSession = Depends(get_db_session)) -> dict:
    item = await db.get(ModelCatalog, model_id)
    if not item:
        raise HTTPException(status_code=404, detail="model not found")
    await db.delete(item)
    await db.commit()
    return {"data": {"id": model_id, "deleted": True}}


@router.post("/route-policies")
async def create_route_policy(payload: RoutePolicyCreate, db: AsyncSession = Depends(get_db_session)) -> dict:
    item = RoutePolicy(**payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return {"data": RoutePolicyRead.model_validate(item, from_attributes=True).model_dump()}


@router.get("/route-policies")
async def list_route_policies(db: AsyncSession = Depends(get_db_session)) -> dict:
    rows = (await db.execute(select(RoutePolicy).order_by(RoutePolicy.created_at.desc()))).scalars().all()
    return {"data": [RoutePolicyRead.model_validate(x, from_attributes=True).model_dump() for x in rows]}


@router.put("/route-policies/{policy_id}")
async def update_route_policy(policy_id: str, payload: RoutePolicyCreate, db: AsyncSession = Depends(get_db_session)) -> dict:
    item = await db.get(RoutePolicy, policy_id)
    if not item:
        raise HTTPException(status_code=404, detail="route policy not found")
    for k, v in payload.model_dump().items():
        setattr(item, k, v)
    await db.commit()
    await db.refresh(item)
    return {"data": RoutePolicyRead.model_validate(item, from_attributes=True).model_dump()}


@router.delete("/route-policies/{policy_id}")
async def delete_route_policy(policy_id: str, db: AsyncSession = Depends(get_db_session)) -> dict:
    item = await db.get(RoutePolicy, policy_id)
    if not item:
        raise HTTPException(status_code=404, detail="route policy not found")
    await db.delete(item)
    await db.commit()
    return {"data": {"id": policy_id, "deleted": True}}
