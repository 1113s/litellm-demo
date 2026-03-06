from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class UsageTableMissingError(Exception):
    pass


@dataclass
class UsageSummaryFilters:
    tenant_id: str | None = None
    model: str | None = None
    provider: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None


TABLE_NAME = "litellm_spend_logs"


async def _table_exists(db: AsyncSession) -> bool:
    query = text(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = :table_name
        )
        """
    )
    try:
        result = await db.execute(query, {"table_name": TABLE_NAME})
        return bool(result.scalar())
    except SQLAlchemyError:
        # sqlite test fallback
        fallback = await db.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name"),
            {"table_name": TABLE_NAME},
        )
        return fallback.first() is not None


async def get_usage_summary(db: AsyncSession, filters: UsageSummaryFilters) -> dict:
    if not await _table_exists(db):
        logger.warning("usage summary skipped: table %s does not exist", TABLE_NAME)
        raise UsageTableMissingError(
            f"LiteLLM usage table '{TABLE_NAME}' does not exist. Please enable LiteLLM spend logs first."
        )

    query = text(
        f"""
        SELECT
            COUNT(*) AS request_count,
            SUM(CASE WHEN status_code >= 200 AND status_code < 400 THEN 1 ELSE 0 END) AS success_count,
            SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) AS error_count,
            COALESCE(SUM(input_tokens), 0) AS total_input_tokens,
            COALESCE(SUM(output_tokens), 0) AS total_output_tokens,
            COALESCE(SUM(spend), 0) AS total_spend
        FROM {TABLE_NAME}
        WHERE (:tenant_id IS NULL OR api_key_alias = :tenant_id)
          AND (:model IS NULL OR model = :model)
          AND (:provider IS NULL OR custom_llm_provider = :provider)
          AND (:start_time IS NULL OR startTime >= :start_time)
          AND (:end_time IS NULL OR startTime <= :end_time)
        """
    )
    params = {
        "tenant_id": filters.tenant_id,
        "model": filters.model,
        "provider": filters.provider,
        "start_time": filters.start_time,
        "end_time": filters.end_time,
    }
    row = (await db.execute(query, params)).mappings().one()
    return {
        "request_count": int(row["request_count"] or 0),
        "success_count": int(row["success_count"] or 0),
        "error_count": int(row["error_count"] or 0),
        "total_input_tokens": int(row["total_input_tokens"] or 0),
        "total_output_tokens": int(row["total_output_tokens"] or 0),
        "total_spend": float(row["total_spend"] or 0),
    }
