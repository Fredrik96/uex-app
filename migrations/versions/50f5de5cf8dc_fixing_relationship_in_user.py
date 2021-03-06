"""fixing relationship in user

Revision ID: 50f5de5cf8dc
Revises: 136b4f3322c0
Create Date: 2022-03-30 16:30:03.449605

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '50f5de5cf8dc'
down_revision = '136b4f3322c0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('datatable', schema=None) as batch_op:
        batch_op.drop_constraint('fk_datatable_users_data_id_user_data', type_='foreignkey')
        batch_op.drop_column('users_data_id')

    with op.batch_alter_table('user_data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('users_table_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_user_data_users_table_id_user_data'), 'user_data', ['users_table_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_data', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_user_data_users_table_id_user_data'), type_='foreignkey')
        batch_op.drop_column('users_table_id')

    with op.batch_alter_table('datatable', schema=None) as batch_op:
        batch_op.add_column(sa.Column('users_data_id', sa.INTEGER(), nullable=True))
        batch_op.create_foreign_key('fk_datatable_users_data_id_user_data', 'user_data', ['users_data_id'], ['id'])

    # ### end Alembic commands ###
