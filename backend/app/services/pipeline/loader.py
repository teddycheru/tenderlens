# backend/app/services/pipeline/loader.py
"""
Loader service for inserting validated tenders into production database.
"""

from typing import Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.models.tender import Tender, TenderStatus
from app.models.tender_staging import TenderStaging


class TenderLoader:
    """Load validated and deduplicated tenders into production."""

    def load(
        self,
        db: Session,
        tender_data: Dict,
        staging_record: TenderStaging
    ) -> Optional[Tender]:
        """
        Load tender data into production tenders table.

        Args:
            db: Database session
            tender_data: Transformed and validated tender data
            staging_record: Original staging record

        Returns:
            Created Tender instance or None
        """
        try:
            # Create new tender
            tender = Tender(
                id=uuid.uuid4(),
                title=tender_data['title'],
                description=tender_data.get('description', ''),
                category=tender_data.get('category'),
                region=tender_data.get('region'),
                source=tender_data.get('source', 'scraped'),
                source_url=tender_data.get('source_url'),
                budget=tender_data.get('budget'),
                budget_currency=tender_data.get('budget_currency', 'ETB'),
                published_date=tender_data.get('published_date'),
                deadline=tender_data.get('deadline'),
                status=TenderStatus.PUBLISHED,
                external_id=tender_data.get('external_id'),
                content_hash=tender_data.get('content_hash'),
                data_quality_score=staging_record.quality_score or 100.0,
                scraped_at=datetime.utcnow(),
                scrape_run_id=staging_record.scrape_run_id
            )

            db.add(tender)
            db.commit()
            db.refresh(tender)

            return tender

        except Exception as e:
            db.rollback()
            print(f"Error loading tender: {str(e)}")
            return None


tender_loader = TenderLoader()
