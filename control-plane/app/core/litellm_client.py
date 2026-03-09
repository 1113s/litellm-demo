from __future__ import annotations

import httpx

from app.core.config import settings


class LiteLLMClientError(Exception):
    pass


async def generate_virtual_key(*, key_alias: str, allowed_models: list[str], metadata_json: dict) -> dict:
    if not settings.litellm_admin_key:
        raise LiteLLMClientError("litellm admin key not configured")

    url = f"{settings.litellm_base_url.rstrip('/')}/key/generate"
    payload = {
        "key_alias": key_alias,
        "models": allowed_models,
        "metadata": metadata_json,
    }
    headers = {"Authorization": f"Bearer {settings.litellm_admin_key}"}

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(url, json=payload, headers=headers)

    if resp.status_code >= 400:
        raise LiteLLMClientError(f"litellm key generation failed: status={resp.status_code}")

    data = resp.json()
    generated_key = data.get("key") or data.get("data", {}).get("key")
    if not generated_key:
        raise LiteLLMClientError("litellm response missing generated key")

    return {"raw": data, "key": generated_key}
