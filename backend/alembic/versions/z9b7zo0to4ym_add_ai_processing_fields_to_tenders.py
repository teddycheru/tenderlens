"""add_ai_processing_fields_to_tenders

Revision ID: z9b7zo0to4ym
Revises: 655187dea582
Create Date: 2025-11-07 21:11:26.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'z9b7zo0to4ym'
down_revision = '655187dea582'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add AI processing fields to tenders table.

    Phase 2: AI Processing Infrastructure
    - AI summary (GPT-4 generated)
    - Processing status and timestamp
    - Extracted entities (JSON)
    - Raw text from document parsing
    - Word count metric
    """
    # Add AI summary field
    op.add_column('tenders', sa.Column('ai_summary', sa.Text(), nullable=True))

    # Add AI processing status fields
    op.add_column('tenders', sa.Column('ai_processed', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('tenders', sa.Column('ai_processed_at', sa.DateTime(timezone=True), nullable=True))

    # Add extracted entities (JSON structure)
    op.add_column('tenders', sa.Column('extracted_entities', postgresql.JSON(astext_type=sa.Text()), nullable=True))

    # Add document processing fields
    op.add_column('tenders', sa.Column('raw_text', sa.Text(), nullable=True))
    op.add_column('tenders', sa.Column('word_count', sa.Integer(), nullable=True))

    # Create index on ai_processed for efficient querying
    op.create_index(op.f('ix_tenders_ai_processed'), 'tenders', ['ai_processed'], unique=False)


def downgrade() -> None:
    """
    Remove AI processing fields from tenders table.
    """
    # Drop index
    op.drop_index(op.f('ix_tenders_ai_processed'), table_name='tenders')

    # Drop AI fields in reverse order
    op.drop_column('tenders', 'word_count')
    op.drop_column('tenders', 'raw_text')
    op.drop_column('tenders', 'extracted_entities')
    op.drop_column('tenders', 'ai_processed_at')
    op.drop_column('tenders', 'ai_processed')
    op.drop_column('tenders', 'ai_summary')
