"""add dpt_id to datapemilih

Revision ID: 662514e201a2
Revises: aff04ab0cb4d
Create Date: 2024-10-01 11:32:05.070486

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '662514e201a2'
down_revision = 'aff04ab0cb4d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('data_pemilih', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dpt_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'dpts', ['dpt_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('data_pemilih', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('dpt_id')

    # ### end Alembic commands ###
