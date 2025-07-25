"""Add total_points and ensure badge relationship

Revision ID: 5fdf10da1c7d
Revises: 87e6e01ac296
Create Date: 2025-07-09 21:03:25.049728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5fdf10da1c7d'
down_revision: Union[str, Sequence[str], None] = '87e6e01ac296'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('total_points', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'total_points')
    # ### end Alembic commands ###
