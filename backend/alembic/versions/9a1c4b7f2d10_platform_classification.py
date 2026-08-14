"""platform classification columns

Adds slug, platform_category, business_model, website, and seller_supported to
the platforms table so platforms carry their business model and seller-support
status. Existing rows default to seller_supported = True (Amazon/Flipkart), and
a re-seed backfills the remaining metadata.

Revision ID: 9a1c4b7f2d10
Revises: 82d35e3c78ec
Create Date: 2026-08-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.db.types  # custom column types (ExactNumeric) may appear in migrations

# revision identifiers, used by Alembic.
revision: str = "9a1c4b7f2d10"
down_revision: Union[str, None] = "82d35e3c78ec"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("platforms") as batch:
        batch.add_column(sa.Column("slug", sa.String(length=120), nullable=True))
        batch.add_column(sa.Column("platform_category", sa.String(length=50), nullable=True))
        batch.add_column(sa.Column("business_model", sa.String(length=100), nullable=True))
        batch.add_column(sa.Column("website", sa.String(length=255), nullable=True))
        batch.add_column(
            sa.Column(
                "seller_supported",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("1"),
            )
        )
        batch.create_index("ix_platforms_slug", ["slug"], unique=True)
        batch.create_index("ix_platforms_platform_category", ["platform_category"])


def downgrade() -> None:
    with op.batch_alter_table("platforms") as batch:
        batch.drop_index("ix_platforms_platform_category")
        batch.drop_index("ix_platforms_slug")
        batch.drop_column("seller_supported")
        batch.drop_column("website")
        batch.drop_column("business_model")
        batch.drop_column("platform_category")
        batch.drop_column("slug")
