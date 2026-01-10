"""
Validation Layer for Extracted Entities
Validates and fixes common extraction errors
"""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dateutil import parser as date_parser


class ExtractionValidator:
    """Validate extracted entities and fix common errors"""

    # Invalid organization names that indicate extraction errors
    INVALID_ORG_NAMES = {
        "Unconditional Bank",
        "Bank Guarantee",
        "Commercial Bank",
        "Not specified",
        "Unknown",
        "N/A",
        "NA",
        "",
        "Unconditional Bank Guarantee",
        "CPO",
        "Cashier's Payment Order"
    }

    # Common organization patterns in Ethiopian tenders
    ORG_PATTERNS = [
        # "X invites...", "X now invites...", "X announces...", "X seeks...", "X, a local organization, invites..."
        r'^([^,]+?)\s*,?\s*(?:a\s+local\s+organization\s*,\s*)?\s*(?:now\s+)?(?:invites?|invite|announces?|announce|seeks?|seek|is\s+calling|would\s+like|requests?|request|has\s+received|intends?|wants?)',
        # "The X Bureau/Office/Department now invites..." - allows commas in org names
        r'^(The\s+.+?(?:Bureau|Office|Department|Authority|Agency|Commission))\s+(?:now\s+)?(?:invites?|has|have|intends?|wants?|announces?|seeks?)',
        # "The X Foundation/Organization/Company now invites..."
        r'^(The\s+[^,]+?(?:Foundation|Organization|Company|Corporation|Bank))\s+(?:now\s+)?(?:invites?|has|have|intends?|wants?|announces?|seeks?)',
        # Ministry/Bureau/Authority patterns (broader match)
        r'^((?:The\s+)?(?:Ministry|Bureau|Authority|Agency|Commission|Office|Department)\s+(?:of\s+)?[A-Za-z\s&,]+?(?:Bureau|Office|Department|Authority|Agency|Commission|Ministry))',
        # Government entities: "GOVERNMENT OF ETHIOPIA", "FEDERAL GOVERNMENT OF ETHIOPIA"
        r'((?:Federal\s+)?Government\s+of\s+Ethiopia)',
        # "NOTICE FOR/OF X" - extract X entity
        r'(?:NOTICE|TENDER)\s+(?:FOR|OF)\s+(?:SALE\s+OF\s+)?((?:Federal\s+)?Government\s+of\s+Ethiopia)',
        # "X - Description"
        r'^([^-]+?)(?:\s*[-–—]\s*)',
        # Ethiopian specific patterns
        r'(Ethiopian\s+[A-Za-z\s&]+(?:Company|Corporation|Bank|Authority|Agency|Institute|University|Hospital))',
        # Pattern for abbreviated names with full expansion
        r'([A-Z][a-z]+(?:\s+[a-z]+)?\s+(?:for|&)\s+[A-Z][a-z]+(?:\s+[A-Za-z]+)*)\s*\(([A-Z]+)\)',
        # Oromifa/Amharic patterns: "Waajjirri X" or "Mootummaa X Waajjirri Y"
        r'(Mootummaa\s+[A-Za-z\s]+?\s+Waajjirri\s+[A-Za-z\s]+)',
        r'(Waajjirri\s+[A-Za-z\s]+)',
    ]

    def __init__(self):
        self.compiled_org_patterns = [re.compile(p, re.IGNORECASE) for p in self.ORG_PATTERNS]

    def validate_all(self, extracted: Dict[str, Any], tender: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate all extracted entities

        Args:
            extracted: Extracted data from LLM or regex
            tender: Original tender data

        Returns:
            Validated and corrected extraction
        """
        validated = extracted.copy()

        # Validate organization
        validated['organization'] = self.validate_organization(
            extracted.get('organization', {}),
            tender.get('Title', tender.get('title', '')),
            tender.get('Description', tender.get('description', ''))
        )

        # Validate dates - handle both naming conventions
        published_raw = tender.get('Published On', tender.get('published_on', ''))
        closing_raw = tender.get('Closing Date', tender.get('closing_date_raw', ''))

        validated['dates'] = self.validate_dates(
            extracted.get('dates', {}),
            published_raw,
            closing_raw
        )

        # Validate financial data
        validated['financial'] = self.validate_financial(
            extracted.get('financial', {}),
            tender.get('Description', tender.get('description', ''))
        )

        # Validate contact info
        validated['contact'] = self.validate_contact(
            extracted.get('contact', {})
        )

        # Validate requirements
        validated['requirements'] = self.validate_requirements(
            extracted.get('requirements', [])
        )

        return validated

    def validate_organization(
        self,
        org: Dict[str, str],
        title: str,
        description: str
    ) -> Dict[str, str]:
        """
        Fix common organization extraction errors

        Args:
            org: Organization dict with 'name' and 'type'
            title: Tender title
            description: Tender description

        Returns:
            Corrected organization dict
        """
        org_name = org.get('name', '').strip()

        # Check if organization name is invalid
        if org_name in self.INVALID_ORG_NAMES or len(org_name) < 3:
            # Try to extract from title first (most reliable)
            org_name = self._extract_org_from_title(title)

            # If still invalid, try description
            if org_name in self.INVALID_ORG_NAMES:
                org_name = self._extract_org_from_description(description)

        # Additional validation: check if org name contains financial keywords
        if any(keyword in org_name.lower() for keyword in ['guarantee', 'bank guarantee', 'cpo', 'payment order', 'unconditional bank']):
            # This is likely a false positive, try to re-extract
            org_name = self._extract_org_from_title(title)

            # If still invalid after re-extraction, try description
            if org_name in self.INVALID_ORG_NAMES or len(org_name) < 3:
                org_name = self._extract_org_from_description(description)

        return {
            'name': org_name,
            'type': org.get('type', '')
        }

    def _extract_org_from_title(self, title: str) -> str:
        """Extract organization name from title using regex patterns"""
        if not title:
            return 'Not specified'

        # Try each pattern
        for pattern in self.compiled_org_patterns:
            match = pattern.search(title)
            if match:
                org_name = match.group(1).strip()
                # Validate: should not be too short or too long
                if 5 < len(org_name) < 200:
                    # Additional check: shouldn't start with common non-org words
                    if not org_name.lower().startswith(('having', 'being', 'must', 'should', 'shall', 'the following')):
                        return org_name

        return 'Not specified'

    def _extract_org_from_description(self, description: str) -> str:
        """Extract organization from description using 'Procuring Entity' pattern"""
        if not description:
            return 'Not specified'

        # Remove HTML tags
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(description, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        # Look for "Procuring Entity:" pattern
        procuring_match = re.search(
            r'(?:Procuring Entity|Procuring Organization|Purchaser|Client|Employer)\s*[:\-]\s*([^,\n]+?)(?:\s*(?:Telephone|Phone|Tel|Email|Address|P\.?O|Code)|\s*$)',
            text,
            re.IGNORECASE
        )

        if procuring_match:
            org_name = procuring_match.group(1).strip()
            if len(org_name) > 5 and len(org_name) < 200:
                return org_name

        return 'Not specified'

    def validate_dates(
        self,
        dates: Dict[str, Optional[str]],
        published_raw: str,
        closing_raw: str
    ) -> Dict[str, Optional[str]]:
        """
        Validate and fix date extraction errors

        Args:
            dates: Extracted dates dict
            published_raw: Raw published date string
            closing_raw: Raw closing date string

        Returns:
            Validated dates dict
        """
        validated = dates.copy()

        # Parse published date if not already done
        if not validated.get('published_date') and published_raw:
            validated['published_date'] = self._parse_date(published_raw)

        # Validate closing date
        closing_date = validated.get('closing_date')
        published_date = validated.get('published_date')

        if closing_date and published_date:
            try:
                closing_dt = datetime.fromisoformat(closing_date.replace('Z', '+00:00'))
                published_dt = datetime.fromisoformat(published_date.replace('Z', '+00:00'))

                # Check if closing date is unreasonably far (>6 months) or in the past
                days_diff = (closing_dt - published_dt).days

                if days_diff > 180 or days_diff < 0:
                    # Try to parse relative date from raw closing string
                    corrected_date = self._parse_relative_closing_date(
                        closing_raw,
                        published_date
                    )
                    if corrected_date:
                        validated['closing_date'] = corrected_date

            except (ValueError, TypeError):
                pass

        # If closing date is still invalid, try parsing raw string
        if not validated.get('closing_date') and closing_raw:
            validated['closing_date'] = self._parse_relative_closing_date(
                closing_raw,
                published_date or datetime.now().isoformat()
            )

        return validated

    def _parse_relative_closing_date(
        self,
        date_str: str,
        published_date: str
    ) -> Optional[str]:
        """
        Parse relative dates like '7 consecutive days from announcement'

        Args:
            date_str: Date string that may contain relative reference
            published_date: Published date to calculate from

        Returns:
            ISO formatted date or None
        """
        if not date_str or not published_date:
            return None

        try:
            # Parse published date as base
            if isinstance(published_date, str):
                base_date = date_parser.parse(published_date, fuzzy=True)
            else:
                base_date = published_date
        except:
            return None

        # Relative date patterns
        patterns = [
            # "7 consecutive days from announcement" or "starting from"
            (r'(\d+)\s+consecutive\s+days', lambda m: base_date + timedelta(days=int(m.group(1)))),
            # "11th calendar days from the last advertisement date"
            (r'(\d+)(?:th|st|nd|rd)?\s+calendar\s+days?\s+from', lambda m: base_date + timedelta(days=int(m.group(1)))),
            # "10th day from this notice"
            (r'(\d+)(?:th|st|nd|rd)?\s+days?\s+(?:from|after)', lambda m: base_date + timedelta(days=int(m.group(1)))),
            # "within 15 days"
            (r'within\s+(\d+)\s+days', lambda m: base_date + timedelta(days=int(m.group(1)))),
            # "15 days from publication/announcement/notice"
            (r'(\d+)\s+days?\s+(?:from|after)\s+(?:publication|announcement|notice|advertisement)',
             lambda m: base_date + timedelta(days=int(m.group(1)))),
            # "on or before 11th calendar days"
            (r'on\s+or\s+before\s+(\d+)(?:th|st|nd|rd)?\s+calendar\s+days?',
             lambda m: base_date + timedelta(days=int(m.group(1)))),
        ]

        for pattern, calculator in patterns:
            match = re.search(pattern, date_str, re.IGNORECASE)
            if match:
                try:
                    calculated_date = calculator(match)
                    return calculated_date.isoformat()
                except:
                    continue

        # If no relative pattern found, try standard parsing
        return self._parse_date(date_str)

    def _fix_month_typos(self, date_str: str) -> str:
        """
        Fix common month name typos using fuzzy matching

        Args:
            date_str: Date string that may contain typos

        Returns:
            Date string with corrected month names
        """
        # Common month typos and corrections
        month_corrections = {
            # Double letters
            r'\bAprill\b': 'April',
            r'\bJanuarry\b': 'January',
            r'\bFeburary\b': 'February',
            r'\bFebuary\b': 'February',
            r'\bOctobber\b': 'October',
            r'\bDecembber\b': 'December',
            # Missing letters
            r'\bJan\b(?!uary)': 'January',
            r'\bFeb\b(?!ruary)': 'February',
            r'\bMar\b(?!ch)': 'March',
            r'\bApr\b(?!il)': 'April',
            r'\bJun\b(?!e)': 'June',
            r'\bJul\b(?!y)': 'July',
            r'\bAug\b(?!ust)': 'August',
            r'\bSep\b(?!tember)': 'September',
            r'\bOct\b(?!ober)': 'October',
            r'\bNov\b(?!ember)': 'November',
            r'\bDec\b(?!ember)': 'December',
            # Common misspellings
            r'\bSeptemeber\b': 'September',
            r'\bSeptmber\b': 'September',
            r'\bOctoner\b': 'October',
            r'\bNovemeber\b': 'November',
        }

        corrected = date_str
        for typo_pattern, correct_month in month_corrections.items():
            corrected = re.sub(typo_pattern, correct_month, corrected, flags=re.IGNORECASE)

        return corrected

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse a date string to ISO 8601 format"""
        if not date_str or date_str == 'Not found':
            return None

        try:
            # Clean up common formats
            cleaned = date_str.strip().rstrip('.')
            cleaned = re.sub(r'\s+at\s+', ' ', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'\s*\([^)]*\)', '', cleaned)
            # Replace hyphens between date and time with space (e.g., "2025-05:00 PM")
            cleaned = re.sub(r'(\d{4})-(\d{1,2}:\d{2})', r'\1 \2', cleaned)
            # Fix am/pm variations (11am, 11:am, 11 am) to standard format (11:00 AM)
            cleaned = re.sub(r'(\d+):?([ap])m', r'\1:00 \2M', cleaned, flags=re.IGNORECASE)
            # Fix common month typos
            cleaned = self._fix_month_typos(cleaned)

            parsed = date_parser.parse(cleaned, fuzzy=True)

            # Check if date is reasonable (not in far past or future)
            now = datetime.now()
            if parsed.year < 2020 or parsed.year > 2030:
                return None

            return parsed.isoformat()
        except (ValueError, TypeError):
            return None

    def validate_financial(
        self,
        financial: Dict[str, Any],
        description: str
    ) -> Dict[str, Any]:
        """
        Validate financial data and fix common errors

        Args:
            financial: Extracted financial dict
            description: Tender description for context

        Returns:
            Validated financial dict
        """
        validated = financial.copy()

        # Ensure all required fields exist
        if 'bid_security_amount' not in validated:
            validated['bid_security_amount'] = None
        if 'bid_security_currency' not in validated:
            validated['bid_security_currency'] = 'ETB'
        if 'document_fee' not in validated:
            validated['document_fee'] = None
        if 'fee_currency' not in validated:
            validated['fee_currency'] = 'ETB'
        if 'other_amounts' not in validated:
            validated['other_amounts'] = []

        # Fix common confusion: bid security vs document fee
        # Document fee is typically 100-1000 ETB, bid security is larger
        bid_security = validated.get('bid_security_amount')
        doc_fee = validated.get('document_fee')

        if bid_security and bid_security < 1000 and not doc_fee:
            # Likely confused - small amount marked as bid security
            # Check context
            if 'fee' in description.lower() or 'non-refundable' in description.lower():
                validated['document_fee'] = bid_security
                validated['bid_security_amount'] = None

        if doc_fee and doc_fee > 10000 and not bid_security:
            # Likely confused - large amount marked as doc fee
            if 'security' in description.lower() or 'guarantee' in description.lower():
                validated['bid_security_amount'] = doc_fee
                validated['document_fee'] = None

        return validated

    def validate_contact(self, contact: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Validate contact information

        Args:
            contact: Contact dict with emails and phones

        Returns:
            Validated contact dict
        """
        validated = {
            'emails': [],
            'phones': []
        }

        # Validate emails
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        for email in contact.get('emails', []):
            if email and email_pattern.match(email):
                validated['emails'].append(email)

        # Validate phones (Ethiopian format)
        phone_pattern = re.compile(r'^(?:\+251|0)[1-9]\d{8,9}$')
        for phone in contact.get('phones', []):
            # Clean phone number
            clean_phone = re.sub(r'[^\d+]', '', str(phone))
            if clean_phone and (phone_pattern.match(clean_phone) or len(clean_phone) >= 10):
                validated['phones'].append(clean_phone)

        # Remove duplicates
        validated['emails'] = list(set(validated['emails']))
        validated['phones'] = list(set(validated['phones']))

        return validated

    def validate_requirements(self, requirements: List[str]) -> List[str]:
        """
        Validate and clean requirements list

        Args:
            requirements: List of requirement strings

        Returns:
            Cleaned requirements list
        """
        validated = []

        # Patterns to filter out (these are not requirements)
        filter_patterns = [
            r'^(?:Bid Documents?|Document)',
            r'^(?:Submission|Deadline|Date)',
            r'^(?:Contact|Inquiries|For further)',
            r'^(?:The|A|An)\s+(?:bidder|supplier)',
            r'^(?:Interested|Eligible)\s+(?:bidders|suppliers)',
            r'may obtain',
            r'will be available',
            r'must be submitted',
        ]

        compiled_filters = [re.compile(p, re.IGNORECASE) for p in filter_patterns]

        for req in requirements:
            if not req or len(req.strip()) < 5:
                continue

            # Skip if matches filter pattern
            should_filter = False
            for pattern in compiled_filters:
                if pattern.search(req):
                    should_filter = True
                    break

            if should_filter:
                continue

            # If requirement is too long (>150 chars), try to extract key part
            if len(req) > 150:
                # Try to extract the actual requirement part
                # Look for patterns like "must have X", "requires X", etc.
                match = re.search(r'(?:must\s+(?:have|include|submit|provide)|requires?|need)\s+(.+)', req, re.IGNORECASE)
                if match:
                    req = match.group(1).strip()
                else:
                    # Skip overly long requirements
                    continue

            validated.append(req.strip())

        # Limit to 15 most important requirements
        return validated[:15]


class ExtractionConfidenceScorer:
    """Calculate confidence scores for extracted entities"""

    def score_extraction(self, extracted: Dict[str, Any], tender: Dict[str, str]) -> Dict[str, float]:
        """
        Calculate confidence scores for each entity type

        Args:
            extracted: Extracted entities
            tender: Original tender data

        Returns:
            Dict of confidence scores (0-1)
        """
        scores = {}

        # Organization confidence
        org = extracted.get('organization', {})
        org_name = org.get('name', '')
        if org_name and org_name not in ExtractionValidator.INVALID_ORG_NAMES:
            # Higher confidence if found in title
            if org_name in tender.get('Title', ''):
                scores['organization'] = 0.95
            else:
                scores['organization'] = 0.75
        else:
            scores['organization'] = 0.3

        # Contact confidence
        contact = extracted.get('contact', {})
        emails = contact.get('emails', [])
        phones = contact.get('phones', [])

        if emails or phones:
            scores['contact'] = 0.9  # Regex extraction is highly reliable
        else:
            scores['contact'] = 0.0

        # Financial confidence
        financial = extracted.get('financial', {})
        if financial.get('bid_security_amount') or financial.get('document_fee'):
            scores['financial'] = 0.85
        else:
            scores['financial'] = 0.0

        # Dates confidence
        dates = extracted.get('dates', {})
        if dates.get('closing_date'):
            try:
                closing = datetime.fromisoformat(dates['closing_date'].replace('Z', '+00:00'))
                published = datetime.fromisoformat(dates.get('published_date', '').replace('Z', '+00:00')) if dates.get('published_date') else datetime.now()

                # Check if date is reasonable
                days_diff = (closing - published).days
                if 0 <= days_diff <= 180:
                    scores['dates'] = 0.9
                else:
                    scores['dates'] = 0.5
            except:
                scores['dates'] = 0.4
        else:
            scores['dates'] = 0.0

        # Requirements confidence
        requirements = extracted.get('requirements', [])
        if requirements and len(requirements) > 0:
            # Lower confidence if requirements are too verbose
            avg_length = sum(len(r) for r in requirements) / len(requirements)
            if avg_length < 100:
                scores['requirements'] = 0.8
            else:
                scores['requirements'] = 0.6
        else:
            scores['requirements'] = 0.0

        # Overall confidence (weighted average)
        weights = {
            'organization': 0.2,
            'contact': 0.15,
            'financial': 0.25,
            'dates': 0.25,
            'requirements': 0.15
        }

        overall = sum(scores.get(k, 0) * v for k, v in weights.items())
        scores['overall'] = overall

        return scores
