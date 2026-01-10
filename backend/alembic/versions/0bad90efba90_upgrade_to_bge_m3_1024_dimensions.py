"""upgrade_to_bge_m3_1024_dimensions

Revision ID: 0bad90efba90
Revises: d332f563e07c
Create Date: 2026-01-01 10:56:11.891949

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision = '0bad90efba90'
down_revision = 'd332f563e07c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Upgrade embedding dimensions from 384 (all-MiniLM-L6-v2) to 1024 (BGE-M3)

    # Drop existing embeddings (they need to be regenerated anyway)
    op.execute("UPDATE tenders SET content_embedding = NULL WHERE content_embedding IS NOT NULL")
    op.execute("UPDATE company_tender_profiles SET profile_embedding = NULL WHERE profile_embedding IS NOT NULL")

    # Alter column types to new dimensions
    op.alter_column('tenders', 'content_embedding',
                    type_=Vector(1024),
                    existing_type=Vector(384),
                    existing_nullable=True)

    op.alter_column('company_tender_profiles', 'profile_embedding',
                    type_=Vector(1024),
                    existing_type=Vector(384),
                    existing_nullable=True)


def downgrade() -> None:
    # Downgrade from 1024 (BGE-M3) back to 384 (all-MiniLM-L6-v2)

    # Drop existing embeddings
    op.execute("UPDATE tenders SET content_embedding = NULL WHERE content_embedding IS NOT NULL")
    op.execute("UPDATE company_tender_profiles SET profile_embedding = NULL WHERE profile_embedding IS NOT NULL")

    # Alter column types back to old dimensions
    op.alter_column('tenders', 'content_embedding',
                    type_=Vector(384),
                    existing_type=Vector(1024),
                    existing_nullable=True)

    op.alter_column('company_tender_profiles', 'profile_embedding',
                    type_=Vector(384),
                    existing_type=Vector(1024),
                    existing_nullable=True)
