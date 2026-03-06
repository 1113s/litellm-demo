"""create admin resource tables

Revision ID: 20260306_0001
Revises:
Create Date: 2026-03-06 00:01:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260306_0001"
down_revision = None
branch_labels = None
depends_on = None


route_strategy = sa.Enum("fixed", "weighted", "fallback", name="route_strategy")


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "providers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("base_url", sa.String(length=512), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "model_catalog",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("model_key", sa.String(length=128), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("provider_id", sa.String(length=36), nullable=False),
        sa.Column("upstream_model", sa.String(length=255), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["provider_id"], ["providers.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("model_key"),
    )

    route_strategy.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "route_policies",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("policy_name", sa.String(length=128), nullable=False),
        sa.Column("strategy", route_strategy, nullable=False),
        sa.Column("target_models", sa.JSON(), nullable=False),
        sa.Column("fallback_models", sa.JSON(), nullable=False),
        sa.Column("weights", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("policy_name"),
    )


def downgrade() -> None:
    op.drop_table("route_policies")
    op.drop_table("model_catalog")
    op.drop_table("providers")
    op.drop_table("tenants")
    route_strategy.drop(op.get_bind(), checkfirst=True)
