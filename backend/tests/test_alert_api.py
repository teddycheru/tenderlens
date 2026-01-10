"""
Tests for the Alert API endpoints.
"""

import pytest
from uuid import uuid4

from app.models.alert import Alert
from app.models.company import Company
from app.models.user import User
from app.schemas.alert import AlertCreate, AlertUpdate


class TestAlertAPI:
    """Test cases for Alert API endpoints."""

    def test_alert_create_schema(self):
        """Test AlertCreate schema validation"""
        alert_data = AlertCreate(
            name="IT Tenders Alert",
            keywords=["software", "development"],
            category_filter="IT & Technology",
            min_budget=10000.0,
            max_budget=100000.0,
            is_active=True
        )

        assert alert_data.name == "IT Tenders Alert"
        assert len(alert_data.keywords) == 2
        assert alert_data.category_filter == "IT & Technology"

    def test_alert_update_schema(self):
        """Test AlertUpdate schema validation"""
        alert_data = AlertUpdate(
            name="Updated Alert Name",
            is_active=False
        )

        assert alert_data.name == "Updated Alert Name"
        assert alert_data.is_active is False

    def test_alert_create_with_empty_keywords(self):
        """Test creating alert with empty keywords list"""
        alert_data = AlertCreate(
            name="No Keywords Alert",
            keywords=[],
            is_active=True
        )

        assert alert_data.keywords == []

    def test_alert_create_minimal(self):
        """Test creating alert with minimal required fields"""
        alert_data = AlertCreate(
            name="Minimal Alert"
        )

        assert alert_data.name == "Minimal Alert"
        assert alert_data.keywords == []
        assert alert_data.is_active is True

    def test_alert_model_creation(self, test_db):
        """Test creating alert model in database"""
        # Create a company first
        company = Company(
            name="Test Company",
            email="test@company.com"
        )
        test_db.add(company)
        test_db.commit()
        test_db.refresh(company)

        # Create alert
        alert = Alert(
            name="Test Alert",
            company_id=company.id,
            keywords=["test", "keyword"],
            category_filter="IT & Technology",
            is_active=True
        )
        test_db.add(alert)
        test_db.commit()
        test_db.refresh(alert)

        # Verify
        assert alert.id is not None
        assert alert.name == "Test Alert"
        assert alert.company_id == company.id
        assert len(alert.keywords) == 2
        assert alert.is_active is True

    def test_alert_list_by_company(self, test_db):
        """Test listing alerts filtered by company"""
        # Create two companies
        company1 = Company(name="Company 1", email="c1@test.com")
        company2 = Company(name="Company 2", email="c2@test.com")
        test_db.add_all([company1, company2])
        test_db.commit()

        # Create alerts for each company
        alert1 = Alert(
            name="Alert 1",
            company_id=company1.id,
            keywords=["keyword1"],
            is_active=True
        )
        alert2 = Alert(
            name="Alert 2",
            company_id=company1.id,
            keywords=["keyword2"],
            is_active=True
        )
        alert3 = Alert(
            name="Alert 3",
            company_id=company2.id,
            keywords=["keyword3"],
            is_active=True
        )

        test_db.add_all([alert1, alert2, alert3])
        test_db.commit()

        # Query alerts for company1
        company1_alerts = test_db.query(Alert).filter(Alert.company_id == company1.id).all()

        assert len(company1_alerts) == 2
        assert all(a.company_id == company1.id for a in company1_alerts)

    def test_alert_active_filter(self, test_db):
        """Test filtering alerts by active status"""
        # Create company
        company = Company(name="Test Company", email="test@company.com")
        test_db.add(company)
        test_db.commit()

        # Create active and inactive alerts
        active_alert = Alert(
            name="Active Alert",
            company_id=company.id,
            keywords=["active"],
            is_active=True
        )
        inactive_alert = Alert(
            name="Inactive Alert",
            company_id=company.id,
            keywords=["inactive"],
            is_active=False
        )

        test_db.add_all([active_alert, inactive_alert])
        test_db.commit()

        # Query only active alerts
        active_alerts = test_db.query(Alert).filter(
            Alert.company_id == company.id,
            Alert.is_active == True
        ).all()

        assert len(active_alerts) == 1
        assert active_alerts[0].name == "Active Alert"

    def test_alert_update(self, test_db):
        """Test updating an alert"""
        # Create company and alert
        company = Company(name="Test Company", email="test@company.com")
        test_db.add(company)
        test_db.commit()

        alert = Alert(
            name="Original Name",
            company_id=company.id,
            keywords=["original"],
            is_active=True
        )
        test_db.add(alert)
        test_db.commit()
        test_db.refresh(alert)

        # Update alert
        alert.name = "Updated Name"
        alert.keywords = ["updated", "keywords"]
        alert.is_active = False

        test_db.commit()
        test_db.refresh(alert)

        # Verify
        assert alert.name == "Updated Name"
        assert alert.keywords == ["updated", "keywords"]
        assert alert.is_active is False

    def test_alert_deletion(self, test_db):
        """Test deleting an alert"""
        # Create company and alert
        company = Company(name="Test Company", email="test@company.com")
        test_db.add(company)
        test_db.commit()

        alert = Alert(
            name="To Be Deleted",
            company_id=company.id,
            keywords=["delete"],
            is_active=True
        )
        test_db.add(alert)
        test_db.commit()
        alert_id = alert.id

        # Delete alert
        test_db.delete(alert)
        test_db.commit()

        # Verify deletion
        deleted_alert = test_db.query(Alert).filter(Alert.id == alert_id).first()
        assert deleted_alert is None


class TestAlertValidation:
    """Test cases for alert validation."""

    def test_alert_name_min_length(self):
        """Test alert name minimum length validation"""
        with pytest.raises(ValueError):
            AlertCreate(name="Ab")  # Too short (min 3 chars)

    def test_alert_budget_validation(self):
        """Test budget must be non-negative"""
        with pytest.raises(ValueError):
            AlertCreate(
                name="Test Alert",
                min_budget=-1000.0  # Negative budget not allowed
            )

    def test_alert_keywords_type(self):
        """Test keywords must be a list"""
        alert = AlertCreate(
            name="Test Alert",
            keywords=["valid", "list"]
        )
        assert isinstance(alert.keywords, list)
