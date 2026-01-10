"""
Information Extraction Module
Extracts structured data from tender descriptions and fields
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from utils import DateParser, LanguageDetector, TenderTypeDetector, TextSanitizer


class TenderExtractor:
    """Extract structured information from tender data"""

    def __init__(self):
        self.birr_pattern = r'[Bb]irr\s+([0-9,]+(?:\.[0-9]{2})?)'
        self.email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        # Comprehensive Ethiopian phone pattern: handles mobile (09XXXXXXXX) and landline (011 XXX XXXX)
        # with spaces, dashes, and international format (+251)
        self.phone_pattern = r'(?:\+?251[\s\-]?|0)(?:\d[\s\-]?){8,10}\d'
        self.po_box_pattern = r'P\.?O\.?\s*Box\s*[0-9]+'

        # Patterns for filtering non-requirements
        self.non_requirement_patterns = [
            # Organization/Entity info
            r'^(?:Procuring Entity|Organization|Company|Institution|Agency|Authority)\s*[:\-]',
            r'^(?:Country|Town|City|Street|Address|Region|Location)\s*[:\-]',
            r'^Code\s*[:\-]?\s*\d+',

            # Contact info
            r'^(?:Telephone|Phone|Tel|Fax|Mobile|Email|E-mail)\s*[:\-]',
            r'^(?:P\.?O\.?\s*Box|Postal Address)\s*[:\-]?',
            r'^\+?251[\d\s\-]+$',
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',

            # Date/Schedule info
            r'^(?:Clarification|Clarification Request)\s*(?:Deadline|Date)\s*[:\-]',
            r'^(?:Bid|Tender)\s*(?:Opening|Closing)\s*(?:Schedule|Date|Deadline|Time)\s*[:\-]',
            r'^(?:Site Visit|Pre-?Bid Conference|Technical Meeting)\s*(?:Schedule|Date|Deadline)\s*[:\-]',
            r'^(?:Submission|Document|Opening)\s*(?:Deadline|Date|Time)\s*[:\-]',

            # Terms and conditions
            r'^(?:Terms and Conditions|General Conditions|Special Conditions)\s*[:\-]?',
            r'^(?:Please note|Note|NB|N\.B\.)\s*[:\-]',

            # Metadata
            r'^(?:Tender|Bid)\s*(?:Number|No|Reference|Ref)\s*[:\-]',
            r'^(?:Source|Published|Posted|Advertised)\s*[:\-]',
        ]

        # Compile patterns for efficiency
        self.compiled_non_req_patterns = [re.compile(p, re.IGNORECASE) for p in self.non_requirement_patterns]

    def extract_all(self, tender: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract all structured information from a tender

        Args:
            tender: Tender dictionary from CSV

        Returns:
            Dictionary with all extracted information
        """
        # Detect language and tender type
        combined_text = f"{tender.get('Title', '')} {tender.get('Description', '')}"
        language_flag, is_non_english = LanguageDetector.detect_language(combined_text)
        tender_type, is_award = TenderTypeDetector.detect_tender_type(
            tender.get('Title', ''),
            tender.get('Description', '')
        )

        return {
            'financial': self._extract_financial(tender),
            'contact': self._extract_contact(tender),
            'dates': self._extract_dates(tender),
            'requirements': self._extract_requirements(tender),
            'specifications': self._extract_specifications(tender),
            'organization': self._extract_organization(tender),
            'addresses': self._extract_addresses(tender),
            'language_flag': language_flag,
            'tender_type': tender_type,
            'is_award_notification': is_award
        }

    def _extract_financial(self, tender: Dict[str, str]) -> Dict[str, Any]:
        """Extract financial information (bid security, fees, amounts)"""
        description = tender.get('Description', '')
        financial = {
            'bid_security_amount': None,
            'bid_security_currency': 'ETB',
            'document_fee': None,
            'fee_currency': 'ETB',
            'other_amounts': []
        }

        # Extract all Birr amounts
        matches = re.finditer(self.birr_pattern, description)
        amounts = []

        for match in matches:
            amount_str = match.group(1).replace(',', '')
            try:
                amount = float(amount_str)
                amounts.append({
                    'value': amount,
                    'context': description[max(0, match.start()-50):min(len(description), match.end()+50)]
                })
            except ValueError:
                continue

        # Try to identify bid security (usually larger amounts)
        if amounts:
            sorted_amounts = sorted(amounts, key=lambda x: x['value'], reverse=True)

            # Bid security is usually the first large amount
            if len(sorted_amounts) > 0:
                financial['bid_security_amount'] = sorted_amounts[0]['value']

            # Document fee is usually smaller, look for "fee" or "non-refundable"
            for amount in sorted_amounts[1:]:
                if 'fee' in amount['context'].lower() or 'non-refundable' in amount['context'].lower():
                    financial['document_fee'] = amount['value']
                    break

            # Store other amounts
            financial['other_amounts'] = [a['value'] for a in sorted_amounts[2:]]

        return financial

    def _extract_contact(self, tender: Dict[str, str]) -> Dict[str, List[str]]:
        """Extract contact information (emails, phones, addresses)"""
        description = tender.get('Description', '')

        # Extract unique emails and phones
        emails = list(set(re.findall(self.email_pattern, description)))
        phones = list(set(re.findall(self.phone_pattern, description)))

        # Deduplicate and clean emails (remove near-duplicates like typos)
        emails = self._deduplicate_emails(emails)

        # Clean and validate phones (remove too short, invalid, or label-only matches)
        phones = self._clean_phones(phones)

        contact = {
            'emails': emails,
            'phones': phones,
        }

        return contact

    def _deduplicate_emails(self, emails: List[str]) -> List[str]:
        """
        Remove duplicate or near-duplicate emails (handles typos)

        Args:
            emails: List of email addresses

        Returns:
            Deduplicated list of emails
        """
        if len(emails) <= 1:
            return emails

        # Use Levenshtein distance to find similar emails
        def similarity(s1: str, s2: str) -> float:
            """Calculate similarity ratio between two strings (0-1)"""
            # Simple implementation: count matching characters
            s1, s2 = s1.lower(), s2.lower()
            matches = sum(1 for a, b in zip(s1, s2) if a == b)
            return matches / max(len(s1), len(s2)) if max(len(s1), len(s2)) > 0 else 0

        deduplicated = []
        threshold = 0.85  # 85% similarity = likely duplicate

        for email in emails:
            is_duplicate = False
            for existing in deduplicated:
                if similarity(email, existing) >= threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                deduplicated.append(email)

        return deduplicated

    def _clean_phones(self, phones: List[str]) -> List[str]:
        """
        Clean and validate phone numbers

        Args:
            phones: List of extracted phone numbers

        Returns:
            Cleaned and validated phone numbers
        """
        cleaned = []

        for phone in phones:
            # Remove all spaces and dashes for validation
            digits_only = re.sub(r'[\s\-]', '', phone)

            # Skip if too short (less than 9 digits) or too long (more than 13 digits)
            if len(digits_only) < 9 or len(digits_only) > 13:
                continue

            # Skip if it's just a label like "Tel: " or "phone "
            if len(digits_only) < 9:
                continue

            # Skip if contains too many non-digit characters (likely a label)
            digit_count = sum(c.isdigit() for c in phone)
            if digit_count < 9:  # Must have at least 9 digits
                continue

            # Valid phone number
            cleaned.append(phone)

        return list(set(cleaned))  # Remove duplicates

    def _extract_dates(self, tender: Dict[str, str]) -> Dict[str, Optional[str]]:
        """
        Extract and normalize dates to ISO 8601 format

        Returns:
            Dictionary with formatted dates for frontend display
        """
        # Parse published date first for relative date calculation
        published_str = tender.get('Published On', '')
        published_date = self._parse_date(published_str)

        # Parse closing date (may be relative to published date)
        closing_str = tender.get('Closing Date', '')
        # Pass published_str (raw) for relative date parsing
        closing_date = self._parse_closing_date(closing_str, published_str)

        # Extract additional dates from description
        description = tender.get('Description', '')
        additional_dates = self._extract_additional_dates(description, published_str)

        dates = {
            'closing_date': closing_date,
            'published_date': published_date,
            'clarification_deadline': additional_dates.get('clarification_deadline'),
            'bid_opening': additional_dates.get('bid_opening'),
            'site_visit': additional_dates.get('site_visit'),
            'pre_bid_conference': additional_dates.get('pre_bid_conference'),
        }
        return dates

    def _extract_additional_dates(self, description: str, published_date: str = None) -> Dict[str, Optional[str]]:
        """
        Extract additional dates from tender description HTML

        Args:
            description: HTML description
            published_date: Published date for relative date calculation

        Returns:
            Dictionary with additional dates
        """
        if not description:
            return {}

        # Get clean text from HTML
        soup = BeautifulSoup(description, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        dates = {
            'clarification_deadline': None,
            'bid_opening': None,
            'site_visit': None,
            'pre_bid_conference': None,
        }

        # Patterns for different date types
        date_patterns = {
            'clarification_deadline': [
                r'(?:Clarification|Clarification Request)\s*(?:Deadline|Date)\s*[:\-]?\s*([A-Za-z]+\.?\s+\d{1,2},?\s+\d{4})',
                r'(?:Clarification|Clarification Request)\s*(?:Deadline|Date)\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                r'(?:Clarification|Questions)\s*(?:must be|should be|to be)\s*(?:submitted|received)?\s*(?:by|before|no later than)\s*[:\-]?\s*([A-Za-z]+\.?\s+\d{1,2},?\s+\d{4})',
            ],
            'bid_opening': [
                r'(?:Bid|Tender)\s*(?:Opening|will be opened)\s*(?:Schedule|Date|Time)?\s*[:\-]?\s*([A-Za-z]+\.?\s+\d{1,2},?\s+\d{4}(?:\s+at\s+\d{1,2}[:\.]?\d{0,2}\s*(?:AM|PM|am|pm)?)?)',
                r'(?:Bid|Tender)\s*(?:Opening|will be opened)\s*(?:Schedule|Date|Time)?\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                r'opening\s*(?:will|shall)\s*(?:take place|be|occur)\s*(?:on|at)?\s*[:\-]?\s*([A-Za-z]+\.?\s+\d{1,2},?\s+\d{4})',
            ],
            'site_visit': [
                r'(?:Site Visit|Site Inspection)\s*(?:Schedule|Date)?\s*[:\-]?\s*([A-Za-z]+\.?\s+\d{1,2},?\s+\d{4})',
                r'(?:Site Visit|Site Inspection)\s*(?:Schedule|Date)?\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                r'visit\s*(?:the)?\s*site\s*(?:on|from|between)?\s*[:\-]?\s*([A-Za-z]+\.?\s+\d{1,2},?\s+\d{4})',
            ],
            'pre_bid_conference': [
                r'(?:Pre-?[Bb]id|Pre-?[Tt]ender)\s*(?:Conference|Meeting)\s*(?:Schedule|Date)?\s*[:\-]?\s*([A-Za-z]+\.?\s+\d{1,2},?\s+\d{4})',
                r'(?:Pre-?[Bb]id|Pre-?[Tt]ender)\s*(?:Conference|Meeting)\s*(?:Schedule|Date)?\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            ],
        }

        for date_type, patterns in date_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    date_str = match.group(1)
                    parsed = self._parse_date(date_str)
                    if parsed:
                        dates[date_type] = parsed
                        break

        return dates

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse a date string to ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"""
        if not date_str or date_str == 'Not found':
            return None

        try:
            # Clean up common formats
            cleaned = date_str.strip()
            # Remove trailing periods
            cleaned = cleaned.rstrip('.')
            # Handle "at" in time (e.g., "April 22, 2025 at 14:00:00")
            cleaned = re.sub(r'\s+at\s+', ' ', cleaned, flags=re.IGNORECASE)
            # Handle "(2:00PM)" style annotations
            cleaned = re.sub(r'\s*\([^)]*\)', '', cleaned)

            parsed = date_parser.parse(cleaned, fuzzy=True)
            # Format as ISO 8601: 2025-04-24T10:00:00
            return parsed.isoformat()
        except (ValueError, TypeError):
            return None

    def _parse_closing_date(self, date_str: str, published_date: Optional[str] = None) -> Optional[str]:
        """
        Parse closing date with special handling for relative dates and complex formats

        Args:
            date_str: Date string to parse
            published_date: Published date for calculating relative dates

        Returns:
            ISO 8601 formatted date (YYYY-MM-DDTHH:MM:SS) or None
        """
        if not date_str or date_str == 'Not found':
            return None

        # First try to parse relative dates using the utility
        parsed_date = DateParser.parse_relative_date(date_str, published_date)
        if parsed_date:
            # Add default time in ISO 8601 format
            return f"{parsed_date}T00:00:00"

        # Pre-process the date string for common edge cases
        cleaned = date_str.strip()
        # Remove trailing periods
        cleaned = cleaned.rstrip('.')
        # Handle "at" in time (e.g., "April 22, 2025 at 14:00:00")
        cleaned = re.sub(r'\s+at\s+', ' ', cleaned, flags=re.IGNORECASE)
        # Handle "(2:00PM)" style annotations - extract time but remove annotation
        time_annotation = re.search(r'\((\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\)', cleaned)
        cleaned = re.sub(r'\s*\([^)]*\)', '', cleaned)

        # Handle "No later than" prefix
        cleaned = re.sub(r'^(?:No later than|Before|Until|By)\s+', '', cleaned, flags=re.IGNORECASE)

        # Handle date separators like "/" in "April 29/2025"
        cleaned = re.sub(r'(\w+)\s*[/]\s*(\d{4})', r'\1, \2', cleaned)

        # Fall back to standard date parsing with time preservation
        try:
            parsed = date_parser.parse(cleaned, fuzzy=True)
            # Format as ISO 8601: 2025-04-24T10:00:00
            # Include time if it exists
            if parsed.hour != 0 or parsed.minute != 0 or parsed.second != 0:
                # Has time information
                return parsed.isoformat()
            else:
                # No time, use date only with midnight as default
                return f"{parsed.strftime('%Y-%m-%d')}T00:00:00"
        except (ValueError, TypeError):
            return None

    def _extract_requirements(self, tender: Dict[str, str]) -> List[str]:
        """Extract requirements from HTML description with proper filtering"""
        description = tender.get('Description', '')

        if not description:
            return []

        try:
            soup = BeautifulSoup(description, 'html.parser')

            requirements = []

            # Extract from lists
            for li in soup.find_all('li'):
                text = li.get_text(strip=True)
                if text and len(text) > 10:
                    # Filter out non-requirements
                    if not self._is_non_requirement(text):
                        requirements.append(text)

            # Remove duplicates while preserving order
            seen = set()
            unique_requirements = []
            for req in requirements:
                # Normalize for comparison
                normalized = req.lower().strip()
                if normalized not in seen:
                    seen.add(normalized)
                    unique_requirements.append(req)

            return unique_requirements[:20]  # Limit to top 20 requirements

        except Exception as e:
            print(f"Error extracting requirements: {e}")
            return []

    def _is_non_requirement(self, text: str) -> bool:
        """
        Check if text is NOT a requirement (should be filtered out)

        Args:
            text: Text to check

        Returns:
            True if text should be filtered out
        """
        # Check against compiled patterns
        for pattern in self.compiled_non_req_patterns:
            if pattern.search(text):
                return True

        # Additional keyword-based filtering
        text_lower = text.lower().strip()

        # Filter out pure contact info
        if re.match(r'^[\+\d\s\-\(\)]+$', text):  # Just phone numbers
            return True

        # Filter out pure codes
        if re.match(r'^code\s*:\s*\d+$', text_lower):
            return True

        # Filter out location-only entries
        location_only_patterns = [
            r'^(?:ethiopia|addis ababa|oromia|amhara|tigray|snnpr)\s*$',
            r'^(?:country|city|town|region|zone|woreda)\s*$',
        ]
        for pattern in location_only_patterns:
            if re.match(pattern, text_lower):
                return True

        # Filter out terms and conditions references
        if text_lower in ['terms and conditions', 'general conditions', 'special conditions']:
            return True

        # Filter out very short generic text
        if len(text) < 15 and text_lower in [
            'factor', 'n/a', 'na', 'none', 'nil', '-', '--', 'tbd', 'tba'
        ]:
            return True

        return False

    def _extract_specifications(self, tender: Dict[str, str]) -> List[Dict[str, Any]]:
        """Extract technical specifications from HTML tables with validation"""
        description = tender.get('Description', '')

        if not description:
            return []

        try:
            soup = BeautifulSoup(description, 'html.parser')
            specifications = []

            # Useless values to filter out
            useless_values = {
                '', 'factor', 'n/a', 'na', 'none', 'nil', '-', '--', 'tbd', 'tba',
                'required', 'mandatory', 'yes', 'no', 'x', '✓', '✗'
            }

            # Find all tables
            for table in soup.find_all('table'):
                rows = table.find_all('tr')

                if len(rows) > 1:
                    # Get headers from first row
                    headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]

                    # Skip if headers are empty or have too many empty columns
                    if not headers or len([h for h in headers if h.strip()]) == 0:
                        continue

                    # Clean headers - remove duplicates by appending index
                    clean_headers = []
                    header_counts = {}
                    for h in headers:
                        h = h.strip()
                        if h in header_counts:
                            header_counts[h] += 1
                            clean_headers.append(f"{h}_{header_counts[h]}")
                        else:
                            header_counts[h] = 0
                            clean_headers.append(h)
                    headers = clean_headers

                    # Get data rows
                    for row in rows[1:]:
                        cols = [td.get_text(strip=True) for td in row.find_all('td')]

                        if cols and len([c for c in cols if c.strip()]) > 0:  # Has at least one non-empty column
                            spec = {}
                            for i, header in enumerate(headers):
                                if i < len(cols):
                                    col_value = cols[i].strip()
                                    # Only add non-empty values that are not useless
                                    if col_value and header.strip():
                                        # Check if value is useless
                                        if col_value.lower() not in useless_values:
                                            spec[header] = col_value

                            # Only add if spec has at least one meaningful key-value pair
                            if spec and len(spec) > 0:
                                specifications.append(spec)

            # Remove duplicate specifications (exact same content)
            unique_specs = []
            seen_specs = set()
            for spec in specifications:
                spec_str = str(sorted(spec.items()))
                if spec_str not in seen_specs:
                    seen_specs.add(spec_str)
                    unique_specs.append(spec)

            return unique_specs[:50]  # Limit to 50 specifications

        except Exception as e:
            print(f"Error extracting specifications: {e}")
            return []

    def _extract_organization(self, tender: Dict[str, str]) -> Dict[str, str]:
        """Extract organization information"""
        description = tender.get('Description', '')
        title = tender.get('Title', '')

        organization = {
            'name': self._extract_org_name(description, title),
            'type': ''  # Could be enhanced with ML classification
        }

        return organization

    def _extract_org_name(self, description: str, title: str) -> str:
        """Extract organization name from description or title"""
        # First, try to extract from HTML using BeautifulSoup
        if description:
            soup = BeautifulSoup(description, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)

            # Priority 1: Look for "Procuring Entity:" pattern
            procuring_match = re.search(
                r'(?:Procuring Entity|Procuring Organization|Purchaser|Client|Employer)\s*[:\-]\s*([^,\n]+?)(?:\s*(?:Telephone|Phone|Tel|Email|Address|P\.?O|Code)|\s*$)',
                text, re.IGNORECASE
            )
            if procuring_match:
                org_name = procuring_match.group(1).strip()
                # Validate - should not be a requirement text
                if len(org_name) > 5 and not org_name.lower().startswith(('having', 'being', 'must', 'should', 'shall')):
                    return org_name

        # Priority 2: Extract from title using specific patterns
        title_patterns = [
            # "Organization Name invites/announces/seeks"
            r'^([^,]+?)(?:\s+(?:invites?|announces?|seeks?|is calling|would like|requests?))',
            # "Organization Name - Description"
            r'^([^-]+?)(?:\s*[-–—]\s*)',
        ]

        for pattern in title_patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                org_name = match.group(1).strip()
                # Validate - should be a reasonable org name
                if len(org_name) > 3 and len(org_name) < 200:
                    return org_name

        # Priority 3: Look for common organization patterns in description
        org_patterns = [
            r'(Ministry of [A-Za-z\s&]+)',
            r'(Ethiopian [A-Za-z\s&]+(?:Company|Corporation|Bank|Authority|Agency|Institute|University|Hospital)?)',
            r'([A-Z][A-Za-z\s&]+(?:Share Company|S\.?C\.?|PLC|Ltd|Corporation|Bank|University|Hospital|Institute|Authority|Agency|Commission|Organization))',
            r'((?:The\s+)?[A-Z][A-Za-z\s&]+(?:of Ethiopia|of Addis Ababa))',
        ]

        combined_text = f"{title} {description}"
        for pattern in org_patterns:
            match = re.search(pattern, combined_text)
            if match:
                org_name = match.group(1).strip()
                # Validate
                if len(org_name) > 5 and not org_name.lower().startswith(('having', 'being', 'must')):
                    return org_name

        return 'Not specified'

    def _extract_addresses(self, tender: Dict[str, str]) -> Dict[str, List[str]]:
        """Extract address information"""
        description = tender.get('Description', '')
        region = tender.get('Region', '')

        addresses = {
            'po_boxes': re.findall(self.po_box_pattern, description, re.IGNORECASE),
            'regions': [region] if region and region != 'Not found' else []
        }

        return addresses

    def clean_html_content(self, html_content: str) -> str:
        """
        Convert HTML to clean text while preserving structure

        Args:
            html_content: Raw HTML string

        Returns:
            Cleaned text content
        """
        if not html_content:
            return ''

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()

            # Get text
            text = soup.get_text(separator='\n', strip=True)

            # Clean up excessive whitespace
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            return '\n'.join(lines)

        except Exception as e:
            print(f"Error cleaning HTML: {e}")
            return html_content


if __name__ == "__main__":
    # Test extractor
    test_tender = {
        'Description': '''
        <p><strong>Birr 50,000.00</strong> bid security</p>
        <p>non-refundable fee of <strong>Birr 300.00</strong></p>
        <p>Contact: example@email.com</p>
        <p>Phone: +251911234567</p>
        <ul>
            <li>Trade License required</li>
            <li>Tax clearance certificate</li>
        </ul>
        ''',
        'Title': 'Ministry of Health invites bidders',
        'Closing Date': 'April 24, 2025 at 10:00 AM',
        'Published On': 'Apr 13, 2025',
        'Region': 'Addis Ababa'
    }

    extractor = TenderExtractor()
    extracted = extractor.extract_all(test_tender)

    print("Extracted Data:")
    for key, value in extracted.items():
        print(f"\n{key}:")
        print(f"  {value}")
