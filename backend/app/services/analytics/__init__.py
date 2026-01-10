# backend/app/services/analytics/__init__.py
"""
Analytics services for tender insights and trends.
"""

from app.services.analytics.aggregator import analytics_aggregator

__all__ = ["analytics_aggregator"]
