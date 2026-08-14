"""fee rule provenance columns

Adds provenance/confidence and fulfilment columns to fee_rules so every fee
value can carry its source, source type, verification status, and last-verified
date (research reproducibility). Existing rows default to source_type
ILLUSTRATIVE and verification_status ASSUMED — placeholder data is never
mislabelled as verified.

Revision ID: b2e7c3d94a01
Revises: 9a1c4b7f2d10
Create Date: 2026-08-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.db.types  # custom column types (ExactNumeric) may appear in migrations

# revision identifiers, used by Alembic.
revision: str = "b2e7c3d94a01"
down_revision: Union[str, None] = "9a1c4b7f2d10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("fee_rules") as batch:
        batch.add_column(sa.Column("fulfillment_type", sa.String(length=30), nullable=True))
        batch.add_column(sa.Column("source_name", sa.String(length=200), nullable=True))
        batch.add_column(
            sa.Column(
                "source_type",
                sa.String(length=20),
                nullable=False,
                server_default="ILLUSTRATIVE",
            )
        )
        batch.add_column(
            sa.Column(
                "verification_status",
                sa.String(length=30),
                nullable=False,
                server_default="ASSUMED",
            )
        )
        batch.add_column(sa.Column("last_verified", sa.Date(), nullable=True))
        batch.add_column(sa.Column("notes", sa.String(length=500), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("fee_rules") as batch:
        batch.drop_column("notes")
        batch.drop_column("last_verified")
        batch.drop_column("verification_status")
        batch.drop_column("source_type")
        batch.drop_column("source_name")
        batch.drop_column("fulfillment_type")
