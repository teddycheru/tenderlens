"""add_recommendation_fields

Revision ID: d332f563e07c
Revises: ae041464a9f5
Create Date: 2025-12-27 13:52:42.415510

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision = 'd332f563e07c'
down_revision = 'ae041464a9f5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add recommendation_status field
    op.add_column('tenders',
        sa.Column('recommendation_status', sa.String(20), server_default='active')
    )

    # Add content_embedding field (384 dimensions for all-MiniLM-L6-v2)
    # Can be changed to 1024 when switching to BGE-M3
    op.add_column('tenders',
        sa.Column('content_embedding', Vector(384), nullable=True)
    )

    # Add embedding_updated_at timestamp
    op.add_column('tenders',
        sa.Column('embedding_updated_at', sa.DateTime(timezone=True), nullable=True)
    )

    # Create indexes for performance
    op.create_index('idx_tenders_recommendation_status', 'tenders', ['recommendation_status'])
    op.create_index('idx_tenders_active_deadline', 'tenders', ['recommendation_status', 'deadline'])

    # Mark existing tenders based on deadline
    op.execute("""
        UPDATE tenders
        SET recommendation_status =
            CASE
                WHEN deadline < NOW() THEN 'expired'
                ELSE 'active'
            END
    """)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_tenders_active_deadline', 'tenders')
    op.drop_index('idx_tenders_recommendation_status', 'tenders')

    # Drop columns
    op.drop_column('tenders', 'embedding_updated_at')
    op.drop_column('tenders', 'content_embedding')
    op.drop_column('tenders', 'recommendation_status')
