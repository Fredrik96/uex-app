"""initial migration

Revision ID: e3c966d586de
Revises: 1c3db60eb7b0
Create Date: 2022-03-29 17:59:41.443726

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3c966d586de'
down_revision = '1c3db60eb7b0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'datatable', type_='foreignkey')
    op.drop_column('datatable', 'users_data_id')
    op.add_column('user_data', sa.Column('users_table_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'user_data', 'datatable', ['users_table_id'], ['id_table'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_data', type_='foreignkey')
    op.drop_column('user_data', 'users_table_id')
    op.add_column('datatable', sa.Column('users_data_id', sa.INTEGER(), nullable=True))
    op.create_foreign_key(None, 'datatable', 'user_data', ['users_data_id'], ['id'])
    # ### end Alembic commands ###
