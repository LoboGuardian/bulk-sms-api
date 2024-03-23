"""create account table

Revision ID: 1b5e21b39e7a
Revises: b0d511301bd8
Create Date: 2024-03-20 16:07:33.080653

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '1b5e21b39e7a'
down_revision: Union[str, None] = 'b0d511301bd8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password', sa.String(length=255), nullable=False))
    op.alter_column('users', 'user_name',
               existing_type=mysql.VARCHAR(length=150),
               type_=sa.String(length=255),
               nullable=False)
    op.alter_column('users', 'user_type',
               existing_type=mysql.VARCHAR(length=150),
               type_=sa.String(length=255),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'user_type',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=150),
               nullable=True)
    op.alter_column('users', 'user_name',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=150),
               nullable=True)
    op.drop_column('users', 'password')
    # ### end Alembic commands ###
