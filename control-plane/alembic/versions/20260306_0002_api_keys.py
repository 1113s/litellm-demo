"""add api_keys table

Revision ID: 20260306_0002
Revises: 20260306_0001
Create Date: 2026-03-06 00:02:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260306_0002"
down_revision = "20260306_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "api_keys",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("litellm_key_alias", sa.String(length=255), nullable=False),
        sa.Column("litellm_generated_key", sa.String(length=255), nullable=False),
        sa.Column("allowed_models", sa.JSON(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("api_keys")
