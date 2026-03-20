"""Add phone field to agents table.

Revision ID: 003
Revises: 002_add_seller_auth
Create Date: 2026-03-20 09:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002_add_seller_auth'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add phone column to agents table
    op.add_column('agents', sa.Column('phone', sa.String(20), nullable=True))


def downgrade() -> None:
    # Remove phone column from agents table
    op.drop_column('agents', 'phone')
