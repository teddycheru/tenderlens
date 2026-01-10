"""
Entity extraction service using spaCy NLP and regex patterns.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional


class EntityExtractor:
    """
    Extract structured entities from tender text using spaCy and regex.

    Note: Requires spacy and python-dateutil to be installed.
    Install with: pip install spacy==3.7.2 python-dateutil==2.8.2
    Download model: python -m spacy download en_core_web_sm
    """

    def __init__(self):
        """Initialize spaCy NLP model."""
        self.nlp = None
        try:
            import spacy
            from app.core.ai_config import ai_settings

            try:
                self.nlp = spacy.load(ai_settings.SPACY_MODEL)
            except OSError:
                print(f"spaCy model '{ai_settings.SPACY_MODEL}' not found.")
                print("Download with: python -m spacy download en_core_web_sm")
                self.nlp = None
        except ImportError:
            print("Warning: spacy not installed. Install with: pip install spacy==3.7.2")
            self.nlp = None

    def extract_entities(self, text: str) -> Dict:
        """
        Extract key entities from tender text.

        Args:
            text: Tender document text

        Returns:
            Dictionary containing extracted entities
        """
        if not text:
            return self._empty_entities()

        # Process with spaCy if available
        doc = self.nlp(text[:100000]) if self.nlp else None  # Limit to 100k chars for performance

        entities = {
            "deadline": self._extract_deadline(text, doc),
            "budget": self._extract_budget(text, doc),
            "requirements": self._extract_requirements(text),
            "qualifications": self._extract_qualifications(text),
            "organizations": self._extract_organizations(doc) if doc else [],
            "locations": self._extract_locations(doc) if doc else [],
            "contact_info": self._extract_contact_info(text)
        }

        return entities

    def _empty_entities(self) -> Dict:
        """Return empty entities structure."""
        return {
            "deadline": None,
            "budget": None,
            "requirements": [],
            "qualifications": [],
            "organizations": [],
            "locations": [],
            "contact_info": None
        }

    def _extract_deadline(self, text: str, doc=None) -> Optional[str]:
        """
        Extract deadline/closing date.

        Args:
            text: Tender text
            doc: spaCy Doc object (optional)

        Returns:
            Deadline date in ISO format (YYYY-MM-DD) or None
        """
        # Common deadline patterns
        patterns = [
            r'deadline[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'closing date[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'submission date[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'due date[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'last date[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    from dateutil import parser as date_parser
                    date_str = match.group(1)
                    parsed_date = date_parser.parse(date_str)
                    return parsed_date.strftime("%Y-%m-%d")
                except:
                    pass

        # Extract dates using spaCy
        if doc:
            for ent in doc.ents:
                if ent.label_ == "DATE":
                    try:
                        from dateutil import parser as date_parser
                        parsed_date = date_parser.parse(ent.text)
                        # Only return future dates (likely deadlines)
                        if parsed_date > datetime.now():
                            return parsed_date.strftime("%Y-%m-%d")
                    except:
                        pass

        return None

    def _extract_budget(self, text: str, doc=None) -> Optional[str]:
        """
        Extract budget/tender value.

        Args:
            text: Tender text
            doc: spaCy Doc object (optional)

        Returns:
            None - Budget information is not displayed per user requirements
        """
        # NOTE: Budget extraction disabled per user requirements
        # Budget information is not applicable to Ethiopian tenders and can be outdated
        # Use detailed extraction prompt instead for accurate financial requirements
        return None

    def _extract_requirements(self, text: str) -> List[str]:
        """
        Extract key requirements.

        Args:
            text: Tender text

        Returns:
            List of requirement strings
        """
        requirements = []

        # Look for requirement sections
        req_section = re.search(
            r'(?:requirements?|specifications?|eligibility|criteria)[:\s]+(.*?)(?:\n\n|\Z)',
            text,
            re.IGNORECASE | re.DOTALL
        )

        if req_section:
            req_text = req_section.group(1)
            # Split by bullets, numbers, or newlines
            items = re.split(r'[\n•\-]\s*(?:\d+[\.)]\s*)?', req_text)
            requirements = [
                item.strip()
                for item in items
                if len(item.strip()) > 20  # Filter out very short items
            ][:5]  # Limit to top 5

        return requirements

    def _extract_qualifications(self, text: str) -> List[str]:
        """
        Extract qualification criteria.

        Args:
            text: Tender text

        Returns:
            List of qualification strings
        """
        qualifications = []

        # Common qualification keywords
        keywords = [
            "certified", "licensed", "accredited", "registered",
            "experience", "years", "ISO", "certification",
            "qualified", "eligible", "approved"
        ]

        sentences = text.split('.')
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                clean_sentence = sentence.strip()
                if 20 < len(clean_sentence) < 200:
                    qualifications.append(clean_sentence)
                    if len(qualifications) >= 5:
                        break

        return qualifications

    def _extract_organizations(self, doc) -> List[str]:
        """
        Extract organization names using spaCy NER.

        Args:
            doc: spaCy Doc object

        Returns:
            List of organization names
        """
        if not doc:
            return []

        orgs = []
        for ent in doc.ents:
            if ent.label_ == "ORG":
                orgs.append(ent.text)

        # Return unique organizations, limit to 5
        return list(set(orgs))[:5]

    def _extract_locations(self, doc) -> List[str]:
        """
        Extract location names using spaCy NER.

        Args:
            doc: spaCy Doc object

        Returns:
            List of location names
        """
        if not doc:
            return []

        locations = []
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:  # Geopolitical entities and locations
                locations.append(ent.text)

        # Return unique locations, limit to 5
        return list(set(locations))[:5]

    def _extract_contact_info(self, text: str) -> Optional[Dict]:
        """
        Extract contact information (email, phone).

        Args:
            text: Tender text

        Returns:
            Dictionary with contact info or None
        """
        contact = {}

        # Email pattern
        email_match = re.search(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            text
        )
        if email_match:
            contact["email"] = email_match.group(0)

        # Phone extraction - prioritize numbers after phone-related keywords
        # First, look for explicit phone numbers with phone/tel/mobile keywords
        phone_keywords_pattern = r'(?:tel\.?|phone|mobile|tel\.?\s*no\.?|contact|call)[:\s]+(\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9})'

        phone_match = re.search(phone_keywords_pattern, text, re.IGNORECASE)
        if phone_match:
            phone_number = phone_match.group(1).strip()
            # Validate it's not too short (avoid matching reference numbers like "id 123")
            if len(phone_number.replace('-', '').replace('.', '').replace(' ', '').replace('+', '')) >= 7:
                contact["phone"] = phone_number
                return contact if contact else None

        # Fallback: Look for international format (+251, +256, etc.) which is typical in Africa
        intl_pattern = r'\+251[-.\s]?\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}'
        phone_match = re.search(intl_pattern, text)
        if phone_match:
            contact["phone"] = phone_match.group(0).strip()
            return contact if contact else None

        # Last fallback: Look for local phone format but avoid very short matches
        # This pattern looks for sequences of digits with separators
        local_pattern = r'(?:^|\s)(?:0|\d)[0-9\-.\s]{8,15}[0-9](?:\s|$)'
        phone_match = re.search(local_pattern, text, re.MULTILINE)
        if phone_match:
            phone_number = phone_match.group(0).strip()
            # Filter out patterns that are clearly NOT phone numbers
            # Avoid: "amce-02", "2024-25", dates, bid numbers, reference numbers
            if not re.match(r'.*\d{4}\-\d{2}.*', phone_number):  # Avoid YYYY-MM patterns
                if len(phone_number.replace('-', '').replace('.', '').replace(' ', '')) >= 7:
                    contact["phone"] = phone_number
                    return contact if contact else None

        return contact if contact else None

    def is_available(self) -> bool:
        """
        Check if entity extraction is available.

        Returns:
            True if spaCy model is loaded, False otherwise
        """
        return self.nlp is not None


# Global entity extractor instance
entity_extractor = EntityExtractor()
