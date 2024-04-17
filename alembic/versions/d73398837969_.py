"""empty message

Revision ID: d73398837969
Revises: d0c2dd8971ed
Create Date: 2024-04-16 13:09:10.999431

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'd73398837969'
down_revision: Union[str, None] = 'd0c2dd8971ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('payment_modes', 'transaction_uuid')
    op.add_column('transactions', sa.Column('transaction_uuid', sa.String(length=255), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('transactions', 'transaction_uuid')
    op.add_column('payment_modes', sa.Column('transaction_uuid', mysql.VARCHAR(length=255), nullable=False))
    # ### end Alembic commands ###