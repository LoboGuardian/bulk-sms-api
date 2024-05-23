"""empty message

Revision ID: 97c2b868f0e0
Revises: fe1a5737802f
Create Date: 2024-05-09 11:14:11.981160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '97c2b868f0e0'
down_revision: Union[str, None] = 'fe1a5737802f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('phone_number', sa.String(length=20), nullable=False))
    op.add_column('users', sa.Column('company_address', sa.String(length=100), nullable=False))
    op.add_column('users', sa.Column('company_name', sa.String(length=100), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'company_name')
    op.drop_column('users', 'company_address')
    op.drop_column('users', 'phone_number')
    # ### end Alembic commands ###