"""add content hash to PDFs

Revision ID: ea7f591e8a31
Revises: 40958a20f7db
Create Date: 2026-07-28
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ea7f591e8a31"
down_revision: Union[str, Sequence[str], None] = "40958a20f7db"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("pdfs", sa.Column("content_sha256", sa.String(length=64), nullable=True))
    op.create_unique_constraint("uq_pdfs_content_sha256", "pdfs", ["content_sha256"])


def downgrade() -> None:
    op.drop_constraint("uq_pdfs_content_sha256", "pdfs", type_="unique")
    op.drop_column("pdfs", "content_sha256")
