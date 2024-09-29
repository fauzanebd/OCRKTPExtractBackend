"""new schemes

Revision ID: c0fb0a7798f7
Revises: 422e6d0b409e
Create Date: 2024-09-29 10:20:53.688222

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c0fb0a7798f7'
down_revision = '422e6d0b409e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('app_settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=255), nullable=False),
    sa.Column('value', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key')
    )
    op.create_table('models',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('provinces',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sliders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_code', sa.String(length=255), nullable=False),
    sa.Column('image', sa.String(length=255), nullable=False),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('visi_misi',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_code', sa.String(length=255), nullable=False),
    sa.Column('image', sa.String(length=255), nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('regencies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('province_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['province_id'], ['provinces.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('subdistricts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('regency_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['regency_id'], ['regencies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('urban_villages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subdistrict_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['subdistrict_id'], ['subdistricts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('villages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('urban_village_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['urban_village_id'], ['urban_villages.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_code', sa.String(length=255), nullable=False),
    sa.Column('avatar', sa.String(length=255), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('no_phone', sa.String(length=20), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('nasional', sa.Boolean(), nullable=True),
    sa.Column('province_id', sa.Integer(), nullable=True),
    sa.Column('regency_id', sa.Integer(), nullable=True),
    sa.Column('subdistrict_id', sa.Integer(), nullable=True),
    sa.Column('urban_village_id', sa.Integer(), nullable=True),
    sa.Column('village_id', sa.Integer(), nullable=True),
    sa.Column('is_enumerator', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['province_id'], ['provinces.id'], ),
    sa.ForeignKeyConstraint(['regency_id'], ['regencies.id'], ),
    sa.ForeignKeyConstraint(['subdistrict_id'], ['subdistricts.id'], ),
    sa.ForeignKeyConstraint(['urban_village_id'], ['urban_villages.id'], ),
    sa.ForeignKeyConstraint(['village_id'], ['villages.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('model_used',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('model_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['model_id'], ['models.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('user')
    with op.batch_alter_table('data_pemilih', schema=None) as batch_op:
        batch_op.add_column(sa.Column('client_code', sa.String(length=255), nullable=False))
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('model_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('province_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('regency_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('subdistrict_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('urban_villages_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('village_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('s3_file', sa.String(length=255), nullable=False))
        batch_op.add_column(sa.Column('name', sa.String(length=100), nullable=False))
        batch_op.add_column(sa.Column('birth_date', sa.Date(), nullable=False))
        batch_op.add_column(sa.Column('gender', sa.String(length=10), nullable=False))
        batch_op.add_column(sa.Column('address', sa.Text(), nullable=False))
        batch_op.add_column(sa.Column('no_phone', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('no_tps', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('is_party_member', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('relation_to_candidate', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('confirmation_status', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('category', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('positioning_to_candidate', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('expectation_to_candidate', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
        batch_op.create_foreign_key(None, 'villages', ['village_id'], ['id'])
        batch_op.create_foreign_key(None, 'urban_villages', ['urban_villages_id'], ['id'])
        batch_op.create_foreign_key(None, 'subdistricts', ['subdistrict_id'], ['id'])
        batch_op.create_foreign_key(None, 'regencies', ['regency_id'], ['id'])
        batch_op.create_foreign_key(None, 'users', ['user_id'], ['id'])
        batch_op.create_foreign_key(None, 'models', ['model_id'], ['id'])
        batch_op.create_foreign_key(None, 'provinces', ['province_id'], ['id'])
        batch_op.drop_column('s3_filename')
        batch_op.drop_column('pekerjaan')
        batch_op.drop_column('rt_rw')
        batch_op.drop_column('nama')
        batch_op.drop_column('tempat_lahir')
        batch_op.drop_column('phone_number')
        batch_op.drop_column('alamat')
        batch_op.drop_column('tgl_lahir')
        batch_op.drop_column('prov_kab')
        batch_op.drop_column('reported_at')
        batch_op.drop_column('reported_by')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('data_pemilih', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reported_by', sa.VARCHAR(length=80), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('reported_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('prov_kab', sa.VARCHAR(length=100), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('tgl_lahir', sa.DATE(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('alamat', sa.TEXT(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('phone_number', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('tempat_lahir', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('nama', sa.VARCHAR(length=100), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('rt_rw', sa.VARCHAR(length=10), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('pekerjaan', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('s3_filename', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('expectation_to_candidate')
        batch_op.drop_column('positioning_to_candidate')
        batch_op.drop_column('category')
        batch_op.drop_column('confirmation_status')
        batch_op.drop_column('relation_to_candidate')
        batch_op.drop_column('is_party_member')
        batch_op.drop_column('no_tps')
        batch_op.drop_column('no_phone')
        batch_op.drop_column('address')
        batch_op.drop_column('gender')
        batch_op.drop_column('birth_date')
        batch_op.drop_column('name')
        batch_op.drop_column('s3_file')
        batch_op.drop_column('village_id')
        batch_op.drop_column('urban_villages_id')
        batch_op.drop_column('subdistrict_id')
        batch_op.drop_column('regency_id')
        batch_op.drop_column('province_id')
        batch_op.drop_column('model_id')
        batch_op.drop_column('user_id')
        batch_op.drop_column('client_code')

    op.create_table('user',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', sa.VARCHAR(length=80), autoincrement=False, nullable=False),
    sa.Column('password', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('is_approved', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('role', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('fernet_key', postgresql.BYTEA(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='user_pkey'),
    sa.UniqueConstraint('email', name='user_email_key'),
    sa.UniqueConstraint('username', name='user_username_key')
    )
    op.drop_table('model_used')
    op.drop_table('users')
    op.drop_table('villages')
    op.drop_table('urban_villages')
    op.drop_table('subdistricts')
    op.drop_table('regencies')
    op.drop_table('visi_misi')
    op.drop_table('sliders')
    op.drop_table('provinces')
    op.drop_table('models')
    op.drop_table('app_settings')
    # ### end Alembic commands ###
