"""add session places

Revision ID: 5d1c0a8b2f41
Revises: 0769fd2d0bf2
Create Date: 2026-05-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d1c0a8b2f41'
down_revision: Union[str, Sequence[str], None] = '0769fd2d0bf2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'session_places',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('place_number', sa.Integer(), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('place_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id', 'place_number')
    )
    op.execute(
        """
        INSERT INTO session_places (place_number, price, place_type, status, session_id)
        SELECT p.number, p.price, p.place_type, p.status, s.id
        FROM sessions s
        JOIN halls h ON h.number_hall = s.number_hall
        JOIN places p ON p.hall_id = h.id
        """
    )


def downgrade() -> None:
    op.drop_table('session_places')
