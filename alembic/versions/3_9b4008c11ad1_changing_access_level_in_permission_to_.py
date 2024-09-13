"""changing access_level in Permission to Enum

Revision ID: 9b4008c11ad1
Revises: 7026c9bcdb24
Create Date: 2024-09-13 17:42:26.816668

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '9b4008c11ad1'
down_revision: Union[str, None] = '7026c9bcdb24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    permissionname_enum = postgresql.ENUM(
        'CREATE_TASK',
        'UPDATE_TASK',
        'DELETE_TASK',
        'READ_TASK',
        name='permissionname'
    )
    permissionname_enum.create(op.get_bind(), checkfirst=True)

    op.alter_column(
        'permissions',
        'access_level',
        existing_type=sa.VARCHAR(),
        type_=permissionname_enum,
        existing_nullable=False,
        postgresql_using='access_level::permissionname'
    )

    op.create_unique_constraint(None, 'permissions', ['access_level'])
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_constraint(None, 'permissions', type_='unique')

    op.alter_column(
        'permissions',
        'access_level',
        type_=sa.VARCHAR(),
        existing_type=postgresql.ENUM(
            'CREATE_TASK',
            'UPDATE_TASK',
            'DELETE_TASK',
            'READ_TASK',
            name='permissionname'
        ),
        existing_nullable=False,
        postgresql_using='access_level::varchar'
    )

    permissionname_enum = postgresql.ENUM(
        'CREATE_TASK',
        'UPDATE_TASK',
        'DELETE_TASK',
        'READ_TASK',
        name='permissionname'
    )
    permissionname_enum.drop(op.get_bind(), checkfirst=True)
    # ### end Alembic commands ###
