"""Add Stripe Connect fields to agents table.

Revision ID: 005
Revises: 004
Create Date: 2026-03-20 03:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add stripe_account_id column
    op.add_column('agents', sa.Column('stripe_account_id', sa.String(255), nullable=True))
    
    # Add stripe_status column with default value
    op.add_column('agents', sa.Column('stripe_status', sa.String(50), nullable=False, server_default='not_connected'))


def downgrade() -> None:
    op.drop_column('agents', 'stripe_status')
    op.drop_column('agents', 'stripe_account_id')
