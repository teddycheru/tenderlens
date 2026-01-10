"""
Utility Functions Module
Language detection, date parsing for relative dates, tender type detection, text sanitization
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple
from dateutil import parser as date_parser


class LanguageDetector:
    """Detect non-English content (Amharic, Oromia, etc.)"""

    # Amharic Unicode range: U+1200 to U+137F
    AMHARIC_PATTERN = re.compile(r'[\u1200-\u137F]')

    # Oromia/Afan Oromo patterns - often has specific patterns
    OROMIA_KEYWORDS = [
        'oromiffaa', 'afaan oromo', 'galmee', 'gaaffii',
        'dhaabbii', 'carraa', 'balaa', 'tuugii'
    ]

    @classmethod
    def detect_language(cls, text: str) -> Tuple[str, bool]:
        """
        Detect if text contains non-English content

        Args:
            text: Text to analyze

        Returns:
            Tuple of (language_flag, is_non_english)
            language_flag: 'amharic', 'oromia', 'english', or 'mixed'
            is_non_english: True if non-English content detected
        """
        if not text:
            return 'english', False

        # Check for Amharic
        amharic_count = len(cls.AMHARIC_PATTERN.findall(text))
        amharic_ratio = amharic_count / len(text) if text else 0

        # Check for Oromia keywords
        text_lower = text.lower()
        oromia_found = any(keyword in text_lower for keyword in cls.OROMIA_KEYWORDS)

        # Determine language
        if amharic_ratio > 0.1:  # More than 10% Amharic characters
            return 'amharic', True
        elif oromia_found or 'oromo' in text_lower:
            return 'oromia', True
        else:
            return 'english', False


class DateParser:
    """Parse relative and descriptive dates"""

    @staticmethod
    def parse_relative_date(date_str: str, reference_date: Optional[str] = None) -> Optional[str]:
        """
        Parse relative date formats like:
        - "10 consecutive days from publication"
        - "15 working days from publication"
        - "No later than April 29, 2025"
        - "within 10 days"
        - "14 calendar days"

        Returns relative dates only (not absolute dates - those should be handled by standard date parser)

        Args:
            date_str: Date string to parse
            reference_date: Published date (YYYY-MM-DD format) to calculate from

        Returns:
            Parsed date in YYYY-MM-DD format or None
        """
        if not date_str or date_str == 'Not found':
            return None

        lower_str = date_str.lower()

        # Pattern 1: "N consecutive days" or "N working days" or "N calendar days" with "from" keyword
        # Examples: "10 consecutive days from publication", "14 consecutive working days from published date"
        days_match = re.search(r'(\d+)\s+[\w\s]*?days\s+(?:from|after)\s+(?:publication|publish)',
                               lower_str, re.IGNORECASE)
        if days_match and reference_date:
            try:
                days = int(days_match.group(1))
                ref_date = datetime.strptime(reference_date.split()[0], '%Y-%m-%d')

                # If "working days", only count Mon-Fri
                if 'working' in lower_str:
                    target_date = DateParser._add_working_days(ref_date, days)
                else:
                    target_date = ref_date + timedelta(days=days)

                return target_date.strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                pass

        # Pattern 2: "within N days" or "after N days"
        # Examples: "within 10 days", "after 7 days"
        within_match = re.search(r'(?:within|after)\s+(\d+)\s+(?:consecutive|working|calendar)?\s*days',
                                lower_str, re.IGNORECASE)
        if within_match and reference_date:
            try:
                days = int(within_match.group(1))
                ref_date = datetime.strptime(reference_date.split()[0], '%Y-%m-%d')

                if 'working' in lower_str:
                    target_date = DateParser._add_working_days(ref_date, days)
                else:
                    target_date = ref_date + timedelta(days=days)

                return target_date.strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                pass

        # Pattern 3: "N days" or "N consecutive days" or "N working days" alone (no from keyword)
        # Examples: "10 days", "7 days", "30 working days"
        # But NOT if preceded by "no later than", "before", "until", "by"
        if not re.search(r'(?:no later than|before|until|by)\s+', lower_str):
            days_match = re.search(r'(\d+)\s+(?:consecutive|working|calendar)?\s*days\b',
                                   lower_str, re.IGNORECASE)
            if days_match and reference_date:
                try:
                    days = int(days_match.group(1))
                    ref_date = datetime.strptime(reference_date.split()[0], '%Y-%m-%d')

                    if 'working' in lower_str:
                        target_date = DateParser._add_working_days(ref_date, days)
                    else:
                        target_date = ref_date + timedelta(days=days)

                    return target_date.strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    pass

        # Pattern 4: "No later than DATE", "before DATE", "until DATE"
        # Examples: "No later than April 29, 2025", "before 30th June 2025"
        no_later_match = re.search(r'(?:no later than|before|until|by)\s+(.+?)(?:\s*$)',
                                   lower_str, re.IGNORECASE)
        if no_later_match:
            date_part = no_later_match.group(1).strip()
            try:
                parsed = date_parser.parse(date_part)
                return parsed.strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                pass

        # Don't try to parse absolute dates here - return None
        # Let the caller use standard date_parser for absolute dates
        return None

    @staticmethod
    def _add_working_days(start_date: datetime, num_days: int) -> datetime:
        """
        Add working days (Mon-Fri) to a date

        Args:
            start_date: Starting date
            num_days: Number of working days to add

        Returns:
            Target date after adding working days
        """
        current_date = start_date
        days_added = 0

        while days_added < num_days:
            current_date += timedelta(days=1)
            # Monday = 0, Sunday = 6
            if current_date.weekday() < 5:  # 0-4 = Mon-Fri
                days_added += 1

        return current_date


class TenderTypeDetector:
    """Detect tender type (invitation vs award notification)"""

    AWARD_KEYWORDS = [
        'award', 'winner', 'won', 'selected', 'announced',
        'successful bidder', 'contract awarded', 'result',
        'procurement result', 'bid result', 'tender result',
        'notify tender award', 'notify award', 'tender award notification',
        'award notification', 'awarded to', 'has been awarded'
    ]

    INVITATION_KEYWORDS = [
        'invites', 'invite', 'announces', 'call for', 'request for',
        'rfp', 'rfq', 'seeks', 'is calling for'
    ]

    @classmethod
    def detect_tender_type(cls, title: str, description: str) -> Tuple[str, bool]:
        """
        Detect if tender is an invitation or award notification

        Args:
            title: Tender title
            description: Tender description

        Returns:
            Tuple of (tender_type, is_award)
            tender_type: 'bid_invitation' or 'award_notification'
            is_award: True if award notification
        """
        combined_text = f"{title} {description}".lower()

        # Check for explicit award patterns first (highest priority)
        if any(keyword in combined_text for keyword in [
            'notify tender award', 'notify award', 'tender award notification',
            'award notification', 'awarded to', 'has been awarded'
        ]):
            return 'award_notification', True

        # Check for award keywords
        award_count = sum(1 for keyword in cls.AWARD_KEYWORDS
                         if keyword in combined_text)

        # Check for invitation keywords
        invitation_count = sum(1 for keyword in cls.INVITATION_KEYWORDS
                              if keyword in combined_text)

        # Award notification if: multiple award keywords AND fewer invitation keywords
        if award_count >= 2 and invitation_count == 0:
            return 'award_notification', True

        # Bid invitation if: explicit invitation keywords
        if invitation_count > 0:
            return 'bid_invitation', False

        # If has award keywords but also invitation keywords, likely invitation
        # (some documents might mention "award" in context of tender requirements)
        if award_count >= 1 and invitation_count > 0:
            return 'bid_invitation', False

        # Default to invitation
        return 'bid_invitation', False


class TextSanitizer:
    """Clean and sanitize text before feeding to LLM"""

    @staticmethod
    def sanitize_for_llm(text: str) -> str:
        """
        Clean text to be fed to LLM - remove excessive HTML, fix encoding issues

        Args:
            text: Raw text (possibly with HTML)

        Returns:
            Cleaned text suitable for LLM
        """
        if not text:
            return ''

        # Remove common HTML entities and tags that might confuse LLM
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        text = re.sub(r'&nbsp;', ' ', text)  # Non-breaking space
        text = re.sub(r'&quot;', '"', text)  # Quote
        text = re.sub(r'&amp;', '&', text)  # Ampersand
        text = re.sub(r'&#\d+;', '', text)  # Numeric entities

        # Fix common encoding issues
        text = text.replace('\u00c2\u00a0', ' ')  # Non-breaking space encoding
        text = text.replace('\x00', '')  # Null bytes

        # Fix multiple spaces/newlines
        text = re.sub(r'\n\n+', '\n', text)  # Multiple newlines to single
        text = re.sub(r' {2,}', ' ', text)  # Multiple spaces to single

        # Remove leading/trailing whitespace per line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)

        # Remove empty lines
        lines = [line for line in lines if line.strip()]
        text = '\n'.join(lines)

        return text.strip()

    @staticmethod
    def truncate_for_llm(text: str, max_length: int = 2000) -> str:
        """
        Truncate text to reasonable length for LLM while preserving readability

        Args:
            text: Text to truncate
            max_length: Maximum length

        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text

        # Try to cut at sentence boundary
        truncated = text[:max_length]
        last_period = truncated.rfind('.')

        if last_period > max_length * 0.8:  # If period is in last 20%
            return truncated[:last_period + 1]

        return truncated + '...'


if __name__ == "__main__":
    # Test language detection
    print("Testing Language Detection:")
    print(LanguageDetector.detect_language("This is English text"))
    print(LanguageDetector.detect_language("ይህ አማርኛ ጽሑፍ ነው"))  # Amharic
    print(LanguageDetector.detect_language("Kun walaloo oromiffaa dha"))  # Oromia

    # Test date parsing
    print("\nTesting Date Parsing:")
    print(DateParser.parse_relative_date("10 consecutive days from publication", "2025-04-13"))
    print(DateParser.parse_relative_date("15 working days from publication", "2025-04-13"))
    print(DateParser.parse_relative_date("No later than April 29, 2025"))

    # Test tender type detection
    print("\nTesting Tender Type Detection:")
    print(TenderTypeDetector.detect_tender_type("Supply Tender", "Invites bidders for supply"))
    print(TenderTypeDetector.detect_tender_type("Bid Result", "Winner announced for tender"))

    # Test text sanitization
    print("\nTesting Text Sanitization:")
    print(TextSanitizer.sanitize_for_llm("<p>Test &nbsp; text</p>"))
