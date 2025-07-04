"""Polls creation date adding

Revision ID: df0332fb3255
Revises: 6eeb5bf33b07
Create Date: 2025-04-24 23:22:18.249028

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df0332fb3255'
down_revision: Union[str, None] = '6eeb5bf33b07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('polls', sa.Column('creation_date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('polls', 'creation_date')
    # ### end Alembic commands ###
