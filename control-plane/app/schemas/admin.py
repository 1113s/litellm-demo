from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class RouteStrategySchema(str, Enum):
    fixed = "fixed"
    weighted = "weighted"
    fallback = "fallback"


class TenantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    status: str = "active"


class TenantRead(BaseModel):
    id: str
    name: str
    status: str
    created_at: datetime


class ProviderCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    base_url: str | None = None
    enabled: bool = True


class ProviderRead(BaseModel):
    id: str
    name: str
    base_url: str | None
    enabled: bool
    created_at: datetime


class ModelCatalogCreate(BaseModel):
    model_key: str = Field(min_length=1, max_length=128)
    display_name: str = Field(min_length=1, max_length=255)
    provider_id: str
    upstream_model: str
    enabled: bool = True


class ModelCatalogRead(BaseModel):
    id: str
    model_key: str
    display_name: str
    provider_id: str
    upstream_model: str
    enabled: bool
    created_at: datetime


class RoutePolicyCreate(BaseModel):
    policy_name: str = Field(min_length=1, max_length=128)
    target_models: list[str]
    fallback_models: list[str] = Field(default_factory=list)
    strategy: RouteStrategySchema
    weights: dict[str, float] = Field(default_factory=dict)


class RoutePolicyRead(BaseModel):
    id: str
    policy_name: str
    target_models: list[str]
    fallback_models: list[str]
    strategy: RouteStrategySchema
    weights: dict[str, float]
    created_at: datetime


class ApiKeyCreate(BaseModel):
    tenant_id: str
    display_name: str = Field(min_length=1, max_length=255)
    litellm_key_alias: str = Field(min_length=1, max_length=255)
    allowed_models: list[str] = Field(default_factory=list)
    metadata_json: dict = Field(default_factory=dict)


class ApiKeyRead(BaseModel):
    id: str
    tenant_id: str
    display_name: str
    litellm_key_alias: str
    litellm_generated_key: str
    allowed_models: list[str]
    metadata_json: dict
    is_active: bool
    created_at: datetime
