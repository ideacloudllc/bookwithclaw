"""Add seller authentication fields

Revision ID: 002
Revises: 001
Create Date: 2026-03-19 11:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add password_hash and hotel_name columns to agents table
    op.add_column('agents', sa.Column('password_hash', sa.String(255), nullable=True))
    op.add_column('agents', sa.Column('hotel_name', sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column('agents', 'hotel_name')
    op.drop_column('agents', 'password_hash')
