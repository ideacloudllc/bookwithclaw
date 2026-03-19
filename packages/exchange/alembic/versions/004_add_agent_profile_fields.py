"""Add profile fields to agent model

Revision ID: 004
Revises: 003
Create Date: 2026-03-19 16:21:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add profile fields to agents table
    op.add_column('agents', sa.Column('address', sa.String(500), nullable=True))
    op.add_column('agents', sa.Column('phone', sa.String(20), nullable=True))
    op.add_column('agents', sa.Column('check_in_time', sa.String(10), default='14:00', nullable=True))
    op.add_column('agents', sa.Column('check_out_time', sa.String(10), default='11:00', nullable=True))


def downgrade() -> None:
    op.drop_column('agents', 'check_out_time')
    op.drop_column('agents', 'check_in_time')
    op.drop_column('agents', 'phone')
    op.drop_column('agents', 'address')
