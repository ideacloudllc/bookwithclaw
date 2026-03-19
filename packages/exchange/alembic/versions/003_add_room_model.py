"""Add room model for seller inventory

Revision ID: 003
Revises: 002
Create Date: 2026-03-19 16:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create rooms table
    op.create_table(
        'rooms',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('seller_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('base_price', sa.Float(), nullable=False),
        sa.Column('floor_price', sa.Float(), nullable=False),
        sa.Column('max_occupancy', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['seller_id'], ['agents.agent_id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rooms_seller_id'), 'rooms', ['seller_id'], unique=False)
    op.create_index(op.f('ix_rooms_id'), 'rooms', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_rooms_id'), table_name='rooms')
    op.drop_index(op.f('ix_rooms_seller_id'), table_name='rooms')
    op.drop_table('rooms')
