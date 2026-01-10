"""
Tests for the flexible date parser utility.
"""

import pytest
from datetime import date

from app.utils.date_parser import parse_flexible_date, validate_date_range


class TestParseFlexibleDate:
    """Test cases for parse_flexible_date function."""

    def test_iso_format(self):
        """Test ISO date format: YYYY-MM-DD"""
        result = parse_flexible_date("2024-01-15")
        assert result == date(2024, 1, 15)

    def test_iso_format_with_time(self):
        """Test ISO format with time: YYYY-MM-DDTHH:MM:SS"""
        result = parse_flexible_date("2024-01-15T14:30:00")
        assert result == date(2024, 1, 15)

    def test_slash_format(self):
        """Test DD/MM/YYYY format"""
        result = parse_flexible_date("15/01/2024")
        assert result == date(2024, 1, 15)

    def test_dash_format(self):
        """Test DD-MM-YYYY format"""
        result = parse_flexible_date("15-01-2024")
        assert result == date(2024, 1, 15)

    def test_month_name_format(self):
        """Test 'Month DD, YYYY' format"""
        result = parse_flexible_date("January 15, 2024")
        assert result == date(2024, 1, 15)

    def test_abbreviated_month_format(self):
        """Test 'Mon DD, YYYY' format"""
        result = parse_flexible_date("Jan 15, 2024")
        assert result == date(2024, 1, 15)

    def test_day_month_year_format(self):
        """Test 'DD Month YYYY' format"""
        result = parse_flexible_date("15 January 2024")
        assert result == date(2024, 1, 15)

    def test_day_abbreviated_month_year_format(self):
        """Test 'DD Mon YYYY' format"""
        result = parse_flexible_date("15 Jan 2024")
        assert result == date(2024, 1, 15)

    def test_month_with_12hour_time(self):
        """Test 'Mon DD, YYYY HH:MM AM/PM' format"""
        result = parse_flexible_date("Jan 26, 2009 3:00 PM")
        assert result == date(2009, 1, 26)

    def test_month_with_12hour_time_seconds(self):
        """Test 'Mon DD, YYYY, HH:MM:SS AM/PM' format"""
        result = parse_flexible_date("Apr 30, 2025, 8:12:28 PM")
        assert result == date(2025, 4, 30)

    def test_none_input(self):
        """Test None input returns None"""
        result = parse_flexible_date(None)
        assert result is None

    def test_empty_string(self):
        """Test empty string returns None"""
        result = parse_flexible_date("")
        assert result is None

    def test_whitespace_string(self):
        """Test whitespace string returns None"""
        result = parse_flexible_date("   ")
        assert result is None

    def test_not_found_string(self):
        """Test 'not found' string returns None"""
        result = parse_flexible_date("not found")
        assert result is None

    def test_na_string(self):
        """Test 'N/A' string returns None"""
        result = parse_flexible_date("N/A")
        assert result is None

    def test_invalid_date_format(self):
        """Test invalid date format returns None"""
        result = parse_flexible_date("invalid-date-string")
        assert result is None

    def test_invalid_numeric_date(self):
        """Test invalid numeric date returns None"""
        result = parse_flexible_date("99/99/9999")
        assert result is None

    def test_single_digit_day_and_month(self):
        """Test single digit day and month"""
        result = parse_flexible_date("5/3/2024")
        assert result == date(2024, 3, 5)

    def test_leading_and_trailing_whitespace(self):
        """Test that leading/trailing whitespace is handled"""
        result = parse_flexible_date("  2024-01-15  ")
        assert result == date(2024, 1, 15)

    def test_month_without_comma(self):
        """Test 'Month DD YYYY' without comma"""
        result = parse_flexible_date("Jan 15 2024")
        assert result == date(2024, 1, 15)


class TestValidateDateRange:
    """Test cases for validate_date_range function."""

    def test_valid_date_in_range(self):
        """Test date within default range (2000-2050)"""
        test_date = date(2024, 1, 15)
        assert validate_date_range(test_date) is True

    def test_date_at_min_boundary(self):
        """Test date at minimum boundary"""
        test_date = date(2000, 1, 1)
        assert validate_date_range(test_date) is True

    def test_date_at_max_boundary(self):
        """Test date at maximum boundary"""
        test_date = date(2050, 12, 31)
        assert validate_date_range(test_date) is True

    def test_date_below_min(self):
        """Test date below minimum year"""
        test_date = date(1999, 12, 31)
        assert validate_date_range(test_date) is False

    def test_date_above_max(self):
        """Test date above maximum year"""
        test_date = date(2051, 1, 1)
        assert validate_date_range(test_date) is False

    def test_custom_range(self):
        """Test custom date range"""
        test_date = date(2010, 6, 15)
        assert validate_date_range(test_date, min_year=2010, max_year=2020) is True

    def test_custom_range_outside(self):
        """Test date outside custom range"""
        test_date = date(2025, 1, 1)
        assert validate_date_range(test_date, min_year=2010, max_year=2020) is False

    def test_none_input(self):
        """Test None input returns False"""
        assert validate_date_range(None) is False


class TestRealWorldExamples:
    """Test cases with real-world date formats from tender sites."""

    def test_merkato_format_1(self):
        """Test common 2merkato.com format"""
        result = parse_flexible_date("Apr 30, 2025, 8:12:28 PM")
        assert result == date(2025, 4, 30)

    def test_merkato_format_2(self):
        """Test another 2merkato.com format"""
        result = parse_flexible_date("Jan 26, 2009 3:00 PM")
        assert result == date(2009, 1, 26)

    def test_ethiopian_format_1(self):
        """Test Ethiopian tender site format"""
        result = parse_flexible_date("15/01/2024")
        assert result == date(2024, 1, 15)

    def test_international_format(self):
        """Test international ISO format"""
        result = parse_flexible_date("2024-01-15")
        assert result == date(2024, 1, 15)

    def test_mixed_format_with_extra_text(self):
        """Test date with surrounding text (should still extract date)"""
        result = parse_flexible_date("Published: 2024-01-15 (Deadline)")
        assert result == date(2024, 1, 15)
