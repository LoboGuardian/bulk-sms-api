"""empty message

Revision ID: d78301d8a5f6
Revises: 97c2b868f0e0
Create Date: 2024-05-09 12:36:56.295306

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd78301d8a5f6'
down_revision: Union[str, None] = '97c2b868f0e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'contacts', ['email'])
    op.create_unique_constraint(None, 'contacts', ['phone'])
    op.create_unique_constraint(None, 'contacts', ['whatsapp'])
    op.create_unique_constraint(None, 'users', ['company_address'])
    op.create_unique_constraint(None, 'users', ['email'])
    op.create_unique_constraint(None, 'users', ['company_name'])
    op.create_unique_constraint(None, 'users', ['phone_number'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_constraint(None, 'contacts', type_='unique')
    op.drop_constraint(None, 'contacts', type_='unique')
    op.drop_constraint(None, 'contacts', type_='unique')
    # ### end Alembic commands ###