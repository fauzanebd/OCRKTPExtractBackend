"""initial migration

Revision ID: 40282ef2e72f
Revises: 
Create Date: 2024-09-28 15:59:24.231892

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '40282ef2e72f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('data_pemilih',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nik', sa.String(length=16), nullable=False),
    sa.Column('nama', sa.String(length=100), nullable=False),
    sa.Column('alamat', sa.Text(), nullable=False),
    sa.Column('prov_kab', sa.String(length=100), nullable=False),
    sa.Column('rt_rw', sa.String(length=10), nullable=False),
    sa.Column('tempat_lahir', sa.String(length=50), nullable=False),
    sa.Column('tgl_lahir', sa.Date(), nullable=False),
    sa.Column('pekerjaan', sa.String(length=50), nullable=False),
    sa.Column('s3_filename', sa.String(length=255), nullable=False),
    sa.Column('phone_number', sa.String(length=20), nullable=True),
    sa.Column('reported_by', sa.String(length=80), nullable=False),
    sa.Column('reported_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nik')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('is_approved', sa.Boolean(), nullable=True),
    sa.Column('role', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    op.drop_table('data_pemilih')
    # ### end Alembic commands ###
