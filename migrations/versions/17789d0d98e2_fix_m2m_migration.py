"""Fix m2m migration

Revision ID: 17789d0d98e2
Revises: 0905e8394486
Create Date: 2022-02-28 12:42:01.549385

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '17789d0d98e2'
down_revision = '0905e8394486'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('User_Table',
    sa.Column('id_table', sa.Integer(), nullable=False),
    sa.Column('date_time_added', sa.DateTime(), nullable=True),
    sa.Column('expname', sa.String(length=20), nullable=True),
    sa.Column('tools', sa.String(length=40), nullable=True),
    sa.Column('number', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('data_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['data_id'], ['user_data.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id_table')
    )
    op.drop_table('user_table')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_table',
    sa.Column('id_table', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('date_time_added', mysql.DATETIME(), nullable=True),
    sa.Column('expname', mysql.VARCHAR(length=20), nullable=True),
    sa.Column('tools', mysql.VARCHAR(length=40), nullable=True),
    sa.Column('number', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('data_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['data_id'], ['user_data.id'], name='user_table_ibfk_1'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='user_table_ibfk_2'),
    sa.PrimaryKeyConstraint('id_table'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('User_Table')
    # ### end Alembic commands ###
