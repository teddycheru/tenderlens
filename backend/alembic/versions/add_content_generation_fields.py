"""Add content generation fields to tenders table

Revision ID: content_gen_001
Revises: z9b7zo0to4ym
Create Date: 2025-11-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'content_gen_001'
down_revision = 'z9b7zo0to4ym'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add content generation fields to tenders table.

    These fields store results from the offline LLM content generation pipeline:
    - clean_description: LLM-generated clean, well-formatted description
    - highlights: LLM-generated key highlights/bullet points
    - extracted_data: Structured extraction (financial, contact, dates, requirements, specs)
    - content_generated_at: Timestamp of when content was generated
    - content_generation_errors: Any errors during generation
    """
    # Add content generation fields
    op.add_column('tenders', sa.Column('clean_description', sa.Text(), nullable=True))
    op.add_column('tenders', sa.Column('highlights', sa.Text(), nullable=True))
    op.add_column('tenders', sa.Column('extracted_data', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('tenders', sa.Column('content_generated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tenders', sa.Column('content_generation_errors', postgresql.JSON(astext_type=sa.Text()), nullable=True))

    # Create index on content_generated_at for efficient filtering
    op.create_index(op.f('ix_tenders_content_generated_at'), 'tenders', ['content_generated_at'], unique=False)


def downgrade() -> None:
    """
    Remove content generation fields from tenders table.
    """
    # Drop index
    op.drop_index(op.f('ix_tenders_content_generated_at'), table_name='tenders')

    # Drop content generation fields in reverse order
    op.drop_column('tenders', 'content_generation_errors')
    op.drop_column('tenders', 'content_generated_at')
    op.drop_column('tenders', 'extracted_data')
    op.drop_column('tenders', 'highlights')
    op.drop_column('tenders', 'clean_description')
