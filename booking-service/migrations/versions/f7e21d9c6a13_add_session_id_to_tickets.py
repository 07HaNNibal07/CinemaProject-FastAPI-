"""add session id to tickets

Revision ID: f7e21d9c6a13
Revises: eb0547d791ad
Create Date: 2026-05-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7e21d9c6a13'
down_revision: Union[str, Sequence[str], None] = 'eb0547d791ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tickets', sa.Column('session_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('tickets', 'session_id')
