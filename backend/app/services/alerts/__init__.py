# backend/app/services/alerts/__init__.py
"""
Alert matching and notification services.
"""

from app.services.alerts.matcher import alert_matcher

__all__ = ["alert_matcher"]
