# backend/app/services/pipeline/transformer.py
"""
Data transformation service for normalizing and cleaning scraped tender data.
"""

from typing import Dict, Any, Optional
from datetime import datetime, date
import hashlib
import re


class TenderTransformer:
    """Transform and normalize tender data."""

    def transform(self, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Transform raw tender data into normalized format.

        Args:
            raw_data: Raw tender data from validation

        Returns:
            Transformed data ready for deduplication and loading
        """
        try:
            transformed = {}

            # Clean and normalize title
            transformed['title'] = self._clean_text(raw_data.get('title', ''))

            # Clean and normalize description
            transformed['description'] = self._clean_text(raw_data.get('description', ''))

            # Parse and normalize dates
            transformed['deadline'] = self._parse_date(raw_data.get('deadline'))
            transformed['published_date'] = self._parse_date(raw_data.get('published_date'))

            # Normalize category
            transformed['category'] = self._normalize_category(raw_data.get('category'))

            # Normalize region
            transformed['region'] = self._normalize_region(raw_data.get('region'))

            # Clean URL
            transformed['source_url'] = raw_data.get('source_url', '').strip() if raw_data.get('source_url') else None

            # Parse budget
            transformed['budget'] = self._parse_budget(raw_data.get('budget'))
            transformed['budget_currency'] = raw_data.get('budget_currency', 'ETB')

            # Generate hashes for deduplication
            transformed['external_id'] = self._generate_external_id(transformed)
            transformed['content_hash'] = self._generate_content_hash(transformed.get('description', ''))

            # Source info
            transformed['source'] = raw_data.get('source', 'scraped')

            return transformed

        except Exception as e:
            print(f"Transformation error: {str(e)}")
            return None

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text fields."""
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep essential punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\-\(\)\[\]\'\"]', '', text)

        return text.strip()

    def _parse_date(self, date_value: Any) -> Optional[date]:
        """Parse date from various formats."""
        if not date_value:
            return None

        if isinstance(date_value, date):
            return date_value

        if isinstance(date_value, datetime):
            return date_value.date()

        if isinstance(date_value, str):
            # Try common date formats
            formats = [
                "%Y-%m-%d",
                "%d/%m/%Y",
                "%m/%d/%Y",
                "%Y/%m/%d",
                "%d-%m-%Y",
                "%B %d, %Y",
                "%d %B %Y"
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(date_value, fmt).date()
                except ValueError:
                    continue

        return None

    def _normalize_category(self, category: Optional[str]) -> Optional[str]:
        """Normalize category names."""
        if not category:
            return None

        category = category.strip().title()

        # Category mapping for common variations
        category_map = {
            "Information Technology": "IT",
            "Information Tech": "IT",
            "Technology": "IT",
            "Construction & Building": "Construction",
            "Building": "Construction",
            "Health": "Healthcare",
            "Medical": "Healthcare",
            "Education & Training": "Education",
            "Training": "Education",
            "Consulting Services": "Consulting",
            "Advisory": "Consulting"
        }

        return category_map.get(category, category)

    def _normalize_region(self, region: Optional[str]) -> Optional[str]:
        """Normalize region names."""
        if not region:
            return None

        region = region.strip().title()

        # Common region name variations
        region_map = {
            "Addis": "Addis Ababa",
            "Aa": "Addis Ababa",
            "Nationwide": "National",
            "All Regions": "National",
            "Country Wide": "National"
        }

        return region_map.get(region, region)

    def _parse_budget(self, budget_value: Any) -> Optional[float]:
        """Parse budget from various formats."""
        if not budget_value:
            return None

        if isinstance(budget_value, (int, float)):
            return float(budget_value)

        if isinstance(budget_value, str):
            # Remove currency symbols and commas
            budget_str = re.sub(r'[^\d\.]', '', budget_value)
            try:
                return float(budget_str)
            except ValueError:
                return None

        return None

    def _generate_external_id(self, data: Dict[str, Any]) -> str:
        """Generate unique external ID for deduplication."""
        # Combine title, deadline, and source for unique hash
        id_string = f"{data.get('title', '')}_{data.get('deadline', '')}_{data.get('source_url', '')}"
        return hashlib.md5(id_string.encode()).hexdigest()

    def _generate_content_hash(self, content: str) -> str:
        """Generate hash of content for similarity matching."""
        if not content:
            return ""
        return hashlib.md5(content.encode()).hexdigest()


tender_transformer = TenderTransformer()
