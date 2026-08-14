"""normalized fee_components table

Creates the normalized fee_components table (Option A). One row = one fee
component with its own provenance and confidence. The legacy fee_rules table is
intentionally preserved (not dropped) for backward compatibility during the
transition; fee_components becomes the authoritative research dataset.

Revision ID: c3f8a1b26d02
Revises: b2e7c3d94a01
Create Date: 2026-08-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.db.types  # custom column types (ExactNumeric) used below

# revision identifiers, used by Alembic.
revision: str = "c3f8a1b26d02"
down_revision: Union[str, None] = "b2e7c3d94a01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fee_components",
        sa.Column("component_id", sa.Integer(), primary_key=True),
        sa.Column("platform_id", sa.Integer(), sa.ForeignKey("platforms.platform_id"), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("price_band_min", app.db.types.ExactNumeric(12, 2), nullable=True),
        sa.Column("price_band_max", app.db.types.ExactNumeric(12, 2), nullable=True),
        sa.Column("fulfillment_type", sa.String(length=30), nullable=True),
        sa.Column("component_type", sa.String(length=20), nullable=False),
        sa.Column("value_kind", sa.String(length=20), nullable=False),
        sa.Column("unit", sa.String(length=5), nullable=True),
        sa.Column("value", app.db.types.ExactNumeric(12, 4), nullable=True),
        sa.Column("value_min", app.db.types.ExactNumeric(12, 4), nullable=True),
        sa.Column("value_max", app.db.types.ExactNumeric(12, 4), nullable=True),
        sa.Column("verification_status", sa.String(length=30), nullable=False),
        sa.Column("source_type", sa.String(length=20), nullable=False),
        sa.Column("source_name", sa.String(length=200), nullable=True),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("last_verified", sa.Date(), nullable=True),
        sa.Column("notes", sa.String(length=600), nullable=True),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("dataset_version", sa.String(length=20), nullable=False),
    )
    op.create_index("ix_fee_components_platform_id", "fee_components", ["platform_id"])
    op.create_index("ix_fee_components_category", "fee_components", ["category"])
    op.create_index("ix_fee_components_component_type", "fee_components", ["component_type"])
    op.create_index("ix_fee_components_effective_from", "fee_components", ["effective_from"])


def downgrade() -> None:
    op.drop_index("ix_fee_components_effective_from", table_name="fee_components")
    op.drop_index("ix_fee_components_component_type", table_name="fee_components")
    op.drop_index("ix_fee_components_category", table_name="fee_components")
    op.drop_index("ix_fee_components_platform_id", table_name="fee_components")
    op.drop_table("fee_components")
