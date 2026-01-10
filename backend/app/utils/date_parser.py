"""
Flexible date parser for handling various date formats from different sources.
"""

from datetime import datetime, date
from typing import Optional
import re
import logging

logger = logging.getLogger(__name__)

# Common date format patterns
DATE_PATTERNS = [
    # Pattern with time: "Apr 30, 2025, 8:12:28 PM"
    (r'([A-Za-z]{3})\s+(\d{1,2}),\s+(\d{4}),\s+(\d{1,2}):(\d{2}):(\d{2})\s+(AM|PM)',
     lambda m: datetime.strptime(f"{m.group(1)} {m.group(2)}, {m.group(3)} {m.group(4)}:{m.group(5)}:{m.group(6)} {m.group(7)}", "%b %d, %Y %I:%M:%S %p").date()),

    # Pattern without seconds: "Jan 26, 2009 3:00 PM"
    (r'([A-Za-z]{3})\s+(\d{1,2}),\s+(\d{4})\s+(\d{1,2}):(\d{2})\s+(AM|PM)',
     lambda m: datetime.strptime(f"{m.group(1)} {m.group(2)}, {m.group(3)} {m.group(4)}:{m.group(5)} {m.group(6)}", "%b %d, %Y %I:%M %p").date()),

    # ISO format: "2025-04-30" or "2025-04-30T14:30:00"
    (r'(\d{4})-(\d{2})-(\d{2})',
     lambda m: date(int(m.group(1)), int(m.group(2)), int(m.group(3)))),

    # Format: "30/04/2025" or "30-04-2025"
    (r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})',
     lambda m: date(int(m.group(3)), int(m.group(2)), int(m.group(1)))),

    # Format: "April 30, 2025" or "Apr 30, 2025"
    (r'([A-Za-z]{3,})\s+(\d{1,2}),?\s+(\d{4})',
     lambda m: datetime.strptime(f"{m.group(1)} {m.group(2)}, {m.group(3)}", "%B %d, %Y").date()
               if len(m.group(1)) > 3
               else datetime.strptime(f"{m.group(1)} {m.group(2)}, {m.group(3)}", "%b %d, %Y").date()),

    # Format: "30 April 2025" or "30 Apr 2025"
    (r'(\d{1,2})\s+([A-Za-z]{3,})\s+(\d{4})',
     lambda m: datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", "%d %B %Y").date()
               if len(m.group(2)) > 3
               else datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", "%d %b %Y").date()),
]


def parse_flexible_date(date_string: str) -> Optional[date]:
    """
    Parse a date string with flexible format handling.

    Supports various date formats commonly found in tender listings:
    - "Apr 30, 2025, 8:12:28 PM"
    - "Jan 26, 2009 3:00 PM"
    - "2025-04-30"
    - "30/04/2025"
    - "April 30, 2025"
    - "30 April 2025"

    Args:
        date_string: The date string to parse

    Returns:
        A date object if parsing succeeds, None otherwise
    """
    if not date_string or not isinstance(date_string, str):
        return None

    # Clean the input
    date_string = date_string.strip()

    # Skip obvious non-dates
    if not date_string or date_string.lower() in ['not found', 'n/a', 'na', '', 'none']:
        return None

    # Try each pattern
    for pattern, parser in DATE_PATTERNS:
        match = re.search(pattern, date_string)
        if match:
            try:
                parsed_date = parser(match)
                return parsed_date
            except (ValueError, AttributeError) as e:
                logger.debug(f"Failed to parse date '{date_string}' with pattern {pattern}: {e}")
                continue

    # If all patterns fail, log and return None
    logger.warning(f"Could not parse date string: '{date_string}'")
    return None


def validate_date_range(date_value: Optional[date], min_year: int = 2000, max_year: int = 2050) -> bool:
    """
    Validate that a date falls within a reasonable range.

    Args:
        date_value: The date to validate
        min_year: Minimum acceptable year (default: 2000)
        max_year: Maximum acceptable year (default: 2050)

    Returns:
        True if date is valid and within range, False otherwise
    """
    if date_value is None:
        return False

    return min_year <= date_value.year <= max_year
