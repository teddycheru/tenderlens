"""
LLM-Based Information Extraction Module
Uses LLM to extract structured data from tender descriptions with high accuracy
Replaces regex-based extraction for better context understanding
"""

import json
import ollama
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup


class LLMExtractor:
    """Extract structured information from tender data using LLM"""

    def __init__(self, model: str = "llama3.2:3b", check_running: bool = True):
        self.model = model
        self.temperature = 0.1  # Low temperature for consistent, accurate extraction

        if check_running:
            self._check_ollama_running()

    def _check_ollama_running(self) -> bool:
        """Check if Ollama is running"""
        try:
            models = ollama.list()
            print(f"✓ Ollama is running with model: {self.model}")
            return True
        except Exception as e:
            print(f"⚠ Warning: Ollama may not be running: {e}")
            return False

    def _clean_html(self, html_content: str) -> str:
        """Convert HTML to clean text"""
        if not html_content:
            return ''

        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            for script in soup(['script', 'style']):
                script.decompose()
            text = soup.get_text(separator='\n', strip=True)
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            return '\n'.join(lines)
        except Exception:
            return html_content

    def _build_extraction_prompt(self, tender: Dict[str, str]) -> str:
        """Build comprehensive extraction prompt for LLM"""

        title = tender.get('Title', '')
        description = self._clean_html(tender.get('Description', ''))
        closing_date_raw = tender.get('Closing Date', '')
        published_on = tender.get('Published On', '')
        region = tender.get('Region', '')
        category = tender.get('Category', '')

        # Truncate description if too long but keep enough for context
        if len(description) > 6000:
            description = description[:6000] + "\n...[truncated]"

        prompt = f"""<task>Extract structured information from this Ethiopian tender document</task>

<critical_rules>
1. ORGANIZATION NAME - Extract the entity ISSUING the tender:
   STEP 1: Look at the TITLE FIRST for patterns like:
     - "X invites...", "X announces...", "X seeks...", "X would like..."
     - Example: "Action for Development (AFD), a local organization, invites..." → "Action for Development (AFD)"

   STEP 2: If title is unclear, look for "Procuring Entity:" in description

   NEVER extract:
     - Banks mentioned for guarantees (e.g., "Unconditional Bank Guarantee" - this is NOT an organization!)
     - Financial institutions mentioned for payments (e.g., "Commercial Bank of Ethiopia" in payment context)
     - Partner organizations or funders (unless they are the main issuer)
     - Generic terms like "Bank Guarantee", "CPO", "Cashier's Payment Order"

2. DATES:
   - If a date is RELATIVE (e.g., "7 consecutive days from announcement", "10th day from this notice", "within 15 days"), set is_relative=true and keep the original text
   - For Ethiopian Calendar dates (e.g., "2017 E.C."), convert to Gregorian by adding 7-8 years (2017 E.C. ≈ 2024/2025 G.C.)
   - Extract time if mentioned (e.g., "at 10:00 AM", "at 2:00 PM")

3. FINANCIAL:
   - BID SECURITY: Usually larger amounts (10,000+ Birr), required as guarantee
   - DOCUMENT FEE: Usually smaller amounts (100-1000 Birr), non-refundable fee to purchase bid documents
   - Do NOT confuse these two - look at context words like "security", "guarantee", "bond" vs "fee", "purchase", "non-refundable"

4. REQUIREMENTS: Extract ONLY actual eligibility criteria as CONCISE bullets:
   ✅ GOOD examples:
     - "Valid Trade License"
     - "Tax Clearance Certificate"
     - "5+ years experience in similar projects"
     - "VAT Registration Certificate"

   ❌ BAD examples (DO NOT INCLUDE):
     - "Bid Documents: Interested bidders may obtain..." (This is instructions, not a requirement)
     - "Submission of Bids: Both the Technical..." (This is procedure, not a requirement)
     - Contact information, dates, or procedural instructions
     - Long paragraphs (keep requirements concise, max 100 characters each)

5. TENDER TYPE:
   - "bid_invitation": Standard invitation to bid/tender
   - "bid_modification": Amendment, correction, extension of existing bid
   - "pre_qualification": Expression of Interest (EOI), pre-qualification
   - "award_notification": Announcement of winner/contract award
</critical_rules>

<tender_metadata>
Title: {title}
Published On: {published_on}
Raw Closing Date: {closing_date_raw}
Region: {region}
Category: {category}
</tender_metadata>

<tender_content>
{description}
</tender_content>

<output_format>
Return a valid JSON object with this exact structure (no markdown, no explanation, just JSON):
{{
  "organization": {{
    "name": "Full organization name issuing the tender",
    "type": "government/private/ngo/international/bank"
  }},
  "financial": {{
    "bid_security_amount": null or number,
    "bid_security_currency": "ETB" or "USD",
    "document_fee": null or number,
    "fee_currency": "ETB" or "USD",
    "other_amounts": [list of other amounts mentioned with context]
  }},
  "dates": {{
    "closing_date": "YYYY-MM-DDTHH:MM:SS or null",
    "closing_date_is_relative": true/false,
    "closing_date_raw": "original text if relative",
    "published_date": "YYYY-MM-DDTHH:MM:SS or null",
    "bid_opening": "YYYY-MM-DDTHH:MM:SS or null",
    "clarification_deadline": "YYYY-MM-DDTHH:MM:SS or null",
    "site_visit": "YYYY-MM-DDTHH:MM:SS or null",
    "pre_bid_conference": "YYYY-MM-DDTHH:MM:SS or null"
  }},
  "contact": {{
    "emails": ["list of email addresses"],
    "phones": ["list of phone numbers"],
    "address": "physical address if mentioned",
    "po_box": "P.O. Box number if mentioned"
  }},
  "requirements": [
    "Requirement 1 (e.g., Valid Trade License)",
    "Requirement 2 (e.g., Tax Clearance Certificate)",
    "Keep each requirement concise, max 100 chars"
  ],
  "specifications": [
    {{
      "item": "Item name",
      "description": "Description",
      "quantity": "Quantity",
      "unit": "Unit"
    }}
  ],
  "tender_type": "bid_invitation/bid_modification/pre_qualification/award_notification",
  "is_award_notification": true/false,
  "language": "english/amharic/oromifa/tigrinya/mixed",
  "procurement_method": "open/restricted/direct/framework",
  "bid_submission_method": "sealed/electronic/both",
  "key_items_being_procured": ["item1", "item2"]
}}
</output_format>

<json_output>"""

        return prompt

    def extract_all(self, tender: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract all structured information from a tender using LLM

        Args:
            tender: Tender dictionary with Title, Description, etc.

        Returns:
            Dictionary with all extracted information
        """
        prompt = self._build_extraction_prompt(tender)

        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={
                    'temperature': self.temperature,
                    'top_k': 40,
                    'top_p': 0.9,
                    'num_predict': 2000,  # Enough for full JSON response
                }
            )

            if response and 'response' in response:
                raw_output = response['response'].strip()

                # Parse JSON from response
                extracted = self._parse_json_response(raw_output)

                if extracted:
                    # Post-process and validate
                    return self._post_process(extracted, tender)
                else:
                    print(f"⚠ Failed to parse JSON from LLM response")
                    return self._get_empty_extraction()
            else:
                print(f"⚠ Empty response from LLM")
                return self._get_empty_extraction()

        except Exception as e:
            print(f"⚠ Error in LLM extraction: {e}")
            return self._get_empty_extraction()

    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """Parse JSON from LLM response, handling common issues"""

        # Try to extract JSON from response
        json_str = response.strip()

        # Remove markdown code blocks if present
        if json_str.startswith('```'):
            json_str = re.sub(r'^```(?:json)?\n?', '', json_str)
            json_str = re.sub(r'\n?```$', '', json_str)

        # Remove any trailing text after JSON
        try:
            # Find the last closing brace
            brace_count = 0
            end_index = 0
            for i, char in enumerate(json_str):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_index = i + 1
                        break

            if end_index > 0:
                json_str = json_str[:end_index]
        except:
            pass

        # Try to parse
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            # Try to fix common JSON issues
            json_str = json_str.replace("'", '"')  # Single to double quotes
            json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
            json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays

            try:
                return json.loads(json_str)
            except:
                print(f"JSON parse error: {e}")
                print(f"Response preview: {json_str[:500]}...")
                return None

    def _post_process(self, extracted: Dict, tender: Dict) -> Dict:
        """Post-process and validate extracted data"""

        # Ensure all required fields exist
        result = {
            'financial': extracted.get('financial', {}),
            'contact': {
                'emails': extracted.get('contact', {}).get('emails', []),
                'phones': extracted.get('contact', {}).get('phones', []),
            },
            'dates': self._process_dates(extracted.get('dates', {})),
            'requirements': extracted.get('requirements', []),
            'specifications': extracted.get('specifications', []),
            'organization': extracted.get('organization', {'name': 'Not specified', 'type': ''}),
            'addresses': {
                'po_boxes': [extracted.get('contact', {}).get('po_box')] if extracted.get('contact', {}).get('po_box') else [],
                'regions': [tender.get('Region', '')] if tender.get('Region', '') else [],
            },
            'language_flag': extracted.get('language', 'english'),
            'tender_type': extracted.get('tender_type', 'bid_invitation'),
            'is_award_notification': extracted.get('is_award_notification', False),
            'procurement_method': extracted.get('procurement_method', 'open'),
            'bid_submission_method': extracted.get('bid_submission_method', 'sealed'),
            'key_items': extracted.get('key_items_being_procured', []),
        }

        # Ensure financial has all required fields
        if 'bid_security_amount' not in result['financial']:
            result['financial']['bid_security_amount'] = None
        if 'bid_security_currency' not in result['financial']:
            result['financial']['bid_security_currency'] = 'ETB'
        if 'document_fee' not in result['financial']:
            result['financial']['document_fee'] = None
        if 'fee_currency' not in result['financial']:
            result['financial']['fee_currency'] = 'ETB'
        if 'other_amounts' not in result['financial']:
            result['financial']['other_amounts'] = []

        # Validate organization name
        org_name = result['organization'].get('name', '')
        if not org_name or org_name.lower() in ['not specified', 'unknown', 'n/a', '']:
            result['organization']['name'] = 'Not specified'

        # Clean phone numbers
        result['contact']['phones'] = [
            self._clean_phone(p) for p in result['contact']['phones'] if p
        ]

        return result

    def _process_dates(self, dates: Dict) -> Dict:
        """Process and validate dates"""
        processed = {
            'closing_date': None,
            'published_date': None,
            'clarification_deadline': None,
            'bid_opening': None,
            'site_visit': None,
            'pre_bid_conference': None,
        }

        # Handle closing date
        if dates.get('closing_date_is_relative', False):
            # Keep as None for relative dates - they need manual calculation
            processed['closing_date'] = None
            processed['closing_date_raw'] = dates.get('closing_date_raw', '')
        else:
            processed['closing_date'] = self._validate_date(dates.get('closing_date'))

        processed['published_date'] = self._validate_date(dates.get('published_date'))
        processed['clarification_deadline'] = self._validate_date(dates.get('clarification_deadline'))
        processed['bid_opening'] = self._validate_date(dates.get('bid_opening'))
        processed['site_visit'] = self._validate_date(dates.get('site_visit'))
        processed['pre_bid_conference'] = self._validate_date(dates.get('pre_bid_conference'))

        return processed

    def _validate_date(self, date_str: Optional[str]) -> Optional[str]:
        """Validate and normalize date string"""
        if not date_str:
            return None

        try:
            # Try to parse the date
            if 'T' in str(date_str):
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                from dateutil import parser
                dt = parser.parse(date_str)

            # Check if date is reasonable (not in far past or future)
            now = datetime.now()
            if dt.year < 2020 or dt.year > 2030:
                return None

            return dt.isoformat()
        except:
            return None

    def _clean_phone(self, phone: str) -> str:
        """Clean and normalize phone number"""
        if not phone:
            return ''

        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        return cleaned

    def _get_empty_extraction(self) -> Dict:
        """Return empty extraction structure"""
        return {
            'financial': {
                'bid_security_amount': None,
                'bid_security_currency': 'ETB',
                'document_fee': None,
                'fee_currency': 'ETB',
                'other_amounts': []
            },
            'contact': {
                'emails': [],
                'phones': [],
            },
            'dates': {
                'closing_date': None,
                'published_date': None,
                'clarification_deadline': None,
                'bid_opening': None,
                'site_visit': None,
                'pre_bid_conference': None,
            },
            'requirements': [],
            'specifications': [],
            'organization': {
                'name': 'Not specified',
                'type': ''
            },
            'addresses': {
                'po_boxes': [],
                'regions': [],
            },
            'language_flag': 'english',
            'tender_type': 'bid_invitation',
            'is_award_notification': False,
        }

    def clean_html_content(self, html_content: str) -> str:
        """Public method for cleaning HTML (used by content generator)"""
        return self._clean_html(html_content)


class ContentGenerator:
    """Generate clean content using LLM"""

    def __init__(self, model: str = "llama3.2:3b", check_running: bool = True):
        self.model = model
        self.temperature = 0.1

        if check_running:
            self._check_ollama_running()

    def _check_ollama_running(self) -> bool:
        """Check if Ollama is running"""
        try:
            ollama.list()
            return True
        except:
            return False

    def generate_content(self, tender: Dict, extracted: Dict) -> Dict[str, str]:
        """
        Generate summary, clean description, and highlights in a single LLM call

        Args:
            tender: Original tender data
            extracted: Extracted structured data

        Returns:
            Dictionary with summary, clean_description, highlights
        """

        # Build context from extracted data
        context = self._build_context(tender, extracted)

        prompt = f"""<task>Generate user-friendly content for this tender</task>

<tender_context>
{context}
</tender_context>

<instructions>
Generate three pieces of content:

1. SUMMARY (2-3 sentences):
   - What is being procured
   - Who is procuring it
   - Key deadline (use EXACT date from extracted data, or say "relative deadline" if not fixed)
   - Any critical financial requirements

2. CLEAN_DESCRIPTION (well-formatted markdown):
   - Use ## for main sections, ### for subsections
   - Start with # heading (never skip to ## or ###)
   - Include all important details from the tender
   - Use bullet points for lists
   - Preserve ALL dates, amounts, requirements
   - Professional tone
   - End with complete sentences (don't truncate)

3. HIGHLIGHTS (5-7 bullet points using •):
   - Use ONLY • for bullets (not -, *, or numbers)
   - Bid security amount (if available)
   - Document fee (if available)
   - Submission deadline
   - Key requirements
   - Contact information
   - Do NOT say "not provided" if data exists in extracted fields
</instructions>

<output_format>
Return a valid JSON object (no markdown, no explanation):
{{
  "summary": "2-3 sentence summary here",
  "clean_description": "# Title\\n\\n## Section\\n\\nContent here...",
  "highlights": "• Point 1\\n• Point 2\\n• Point 3"
}}
</output_format>

<json_output>"""

        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={
                    'temperature': self.temperature,
                    'top_k': 40,
                    'top_p': 0.9,
                    'num_predict': 2500,
                }
            )

            if response and 'response' in response:
                raw_output = response['response'].strip()
                result = self._parse_json_response(raw_output)

                if result:
                    return {
                        'summary': result.get('summary', ''),
                        'clean_description': result.get('clean_description', ''),
                        'highlights': result.get('highlights', ''),
                    }

            return {'summary': '', 'clean_description': '', 'highlights': ''}

        except Exception as e:
            print(f"⚠ Error generating content: {e}")
            return {'summary': '', 'clean_description': '', 'highlights': ''}

    def _build_context(self, tender: Dict, extracted: Dict) -> str:
        """Build context string from tender and extracted data"""

        lines = [
            f"Title: {tender.get('Title', '')}",
            f"Category: {tender.get('Category', '')}",
            f"Region: {tender.get('Region', '')}",
        ]

        # Organization
        org = extracted.get('organization', {})
        if org.get('name') and org.get('name') != 'Not specified':
            lines.append(f"Organization: {org['name']}")

        # Dates
        dates = extracted.get('dates', {})
        if dates.get('closing_date'):
            lines.append(f"Submission Deadline: {dates['closing_date']}")
        if dates.get('bid_opening'):
            lines.append(f"Bid Opening: {dates['bid_opening']}")
        if dates.get('clarification_deadline'):
            lines.append(f"Clarification Deadline: {dates['clarification_deadline']}")

        # Financial
        financial = extracted.get('financial', {})
        if financial.get('bid_security_amount'):
            lines.append(f"Bid Security: {financial['bid_security_amount']:,.2f} {financial.get('bid_security_currency', 'ETB')}")
        if financial.get('document_fee'):
            lines.append(f"Document Fee: {financial['document_fee']:,.2f} {financial.get('fee_currency', 'ETB')}")

        # Contact
        contact = extracted.get('contact', {})
        if contact.get('emails'):
            lines.append(f"Email: {', '.join(contact['emails'][:2])}")
        if contact.get('phones'):
            lines.append(f"Phone: {', '.join(contact['phones'][:2])}")

        # Requirements
        requirements = extracted.get('requirements', [])
        if requirements:
            lines.append(f"Key Requirements: {', '.join(requirements[:5])}")

        # Original description (cleaned)
        extractor = LLMExtractor(check_running=False)
        clean_desc = extractor.clean_html_content(tender.get('Description', ''))
        if clean_desc:
            # Truncate if too long
            if len(clean_desc) > 4000:
                clean_desc = clean_desc[:4000] + "..."
            lines.append(f"\nOriginal Description:\n{clean_desc}")

        return '\n'.join(lines)

    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """Parse JSON from LLM response"""
        json_str = response.strip()

        if json_str.startswith('```'):
            json_str = re.sub(r'^```(?:json)?\n?', '', json_str)
            json_str = re.sub(r'\n?```$', '', json_str)

        try:
            brace_count = 0
            end_index = 0
            for i, char in enumerate(json_str):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_index = i + 1
                        break

            if end_index > 0:
                json_str = json_str[:end_index]
        except:
            pass

        try:
            return json.loads(json_str)
        except:
            json_str = json_str.replace("'", '"')
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)

            try:
                return json.loads(json_str)
            except:
                return None


if __name__ == "__main__":
    # Test LLM extractor
    test_tender = {
        'Title': 'Action for Development (AFD), a local organization, invites interested bidders for the Supply of Veterinary Equipment',
        'Description': '''
        <p><strong>Invitation for Bid</strong></p>
        <p>Bid Reference Number: AFDA-09/2025</p>
        <p>Financed by: EHF/Plan International</p>
        <p>Eligible bidders invited to take part in the bid are expected to submit copies of renewed trade license and Tax Payer's Identification certificates.</p>
        <p>The bid document can be purchased from Action for Development (AFD) against payment of non-refundable fee of Birr 300.00 during office hours.</p>
        <p>All bids must be accompanied by a bid bond amounting 1% of the total bid amount in the form of C.P.O. or Unconditional Bank Guarantee.</p>
        <p>All bids must be submitted at or before 2:00 P.M local time on 28th April, 2025.</p>
        <p>Bids will be opened in the presence of bidders on 28th April, 2025 at 12:30 P.M.</p>
        <p>Contact: Tel 011 662 5976/0939655371</p>
        ''',
        'Closing Date': 'At 2:00 P.M local time on 28th April, 2025.',
        'Published On': 'Apr 13, 2025',
        'Region': 'Addis Ababa',
        'Category': 'Corporate Services'
    }

    print("Testing LLM Extractor...")
    print("=" * 60)

    extractor = LLMExtractor(model="llama3.2:3b")
    extracted = extractor.extract_all(test_tender)

    print("\nExtracted Data:")
    print(json.dumps(extracted, indent=2, default=str))

    print("\n" + "=" * 60)
    print("Testing Content Generator...")

    generator = ContentGenerator(model="llama3.2:3b")
    content = generator.generate_content(test_tender, extracted)

    print("\nGenerated Content:")
    print(f"\nSummary:\n{content['summary']}")
    print(f"\nHighlights:\n{content['highlights']}")
