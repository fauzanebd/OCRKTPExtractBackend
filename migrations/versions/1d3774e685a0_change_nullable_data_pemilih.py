"""change nullable data pemilih

Revision ID: 1d3774e685a0
Revises: a0c6ea0cb15b
Create Date: 2024-09-29 13:26:40.006204

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d3774e685a0'
down_revision = 'a0c6ea0cb15b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('data_pemilih', schema=None) as batch_op:
        batch_op.alter_column('ward_code',
               existing_type=sa.VARCHAR(length=13),
               nullable=True)
        batch_op.alter_column('village_code',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
        batch_op.alter_column('birth_date',
               existing_type=sa.DATE(),
               nullable=True)
        batch_op.alter_column('gender',
               existing_type=sa.VARCHAR(length=10),
               nullable=True)
        batch_op.alter_column('address',
               existing_type=sa.TEXT(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('data_pemilih', schema=None) as batch_op:
        batch_op.alter_column('address',
               existing_type=sa.TEXT(),
               nullable=False)
        batch_op.alter_column('gender',
               existing_type=sa.VARCHAR(length=10),
               nullable=False)
        batch_op.alter_column('birth_date',
               existing_type=sa.DATE(),
               nullable=False)
        batch_op.alter_column('village_code',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
        batch_op.alter_column('ward_code',
               existing_type=sa.VARCHAR(length=13),
               nullable=False)

    # ### end Alembic commands ###
