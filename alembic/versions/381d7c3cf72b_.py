"""empty message

Revision ID: 381d7c3cf72b
Revises: de9b606102e9
Create Date: 2024-05-15 15:35:12.420595

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '381d7c3cf72b'
down_revision: Union[str, None] = 'de9b606102e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('user_token_ibfk_1', 'user_token', type_='foreignkey')
    op.create_foreign_key(None, 'user_token', 'user_details', ['userDetailId'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_token', type_='foreignkey')
    op.create_foreign_key('user_token_ibfk_1', 'user_token', 'users', ['userDetailId'], ['id'])
    # ### end Alembic commands ###