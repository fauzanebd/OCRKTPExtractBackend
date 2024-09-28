"""change key type

Revision ID: 422e6d0b409e
Revises: ad0ce2e0e852
Create Date: 2024-09-28 18:14:39.214873

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '422e6d0b409e'
down_revision = 'ad0ce2e0e852'
branch_labels = None
depends_on = None


def upgrade():
    # Use raw SQL to perform the type conversion
    op.execute('ALTER TABLE "user" ALTER COLUMN fernet_key TYPE BYTEA USING fernet_key::bytea')

def downgrade():
    # Convert back to VARCHAR if needed
    op.execute('ALTER TABLE "user" ALTER COLUMN fernet_key TYPE VARCHAR(255) USING fernet_key::varchar')