# backend/app/services/alerts/matcher.py
"""
Alert matching engine to find relevant tenders for user alerts.
"""

from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from uuid import UUID

from app.models.tender import Tender
from app.models.alert import Alert, TenderAlert


class AlertMatcher:
    """Match new tenders against user alert criteria."""

    def match_tender_to_alerts(self, db: Session, tender_id: UUID) -> List[Alert]:
        """
        Find all alerts that match a tender.

        Args:
            db: Database session
            tender_id: ID of tender to match

        Returns:
            List of matching alerts
        """
        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            return []

        # Get all active alerts
        alerts = db.query(Alert).filter(Alert.is_active == True).all()

        matching_alerts = []

        for alert in alerts:
            if self._does_tender_match_alert(tender, alert):
                matching_alerts.append(alert)

                # Create tender-alert association
                tender_alert = TenderAlert(
                    tender_id=tender.id,
                    alert_id=alert.id
                )
                db.add(tender_alert)

        db.commit()
        return matching_alerts

    def _does_tender_match_alert(self, tender: Tender, alert: Alert) -> bool:
        """
        Check if a tender matches an alert's criteria.

        Args:
            tender: Tender to check
            alert: Alert with criteria

        Returns:
            True if tender matches alert criteria
        """
        criteria = alert.criteria or {}

        # Check keywords in title/description
        if criteria.get('keywords'):
            keywords = [k.lower() for k in criteria['keywords']]
            tender_text = f"{tender.title} {tender.description}".lower()

            if not any(keyword in tender_text for keyword in keywords):
                return False

        # Check categories
        if criteria.get('categories') and tender.category:
            if tender.category not in criteria['categories']:
                return False

        # Check regions
        if criteria.get('regions') and tender.region:
            if tender.region not in criteria['regions']:
                return False

        # Check min budget
        if criteria.get('min_budget') and tender.budget:
            if tender.budget < criteria['min_budget']:
                return False

        # Check max budget
        if criteria.get('max_budget') and tender.budget:
            if tender.budget > criteria['max_budget']:
                return False

        return True


alert_matcher = AlertMatcher()
