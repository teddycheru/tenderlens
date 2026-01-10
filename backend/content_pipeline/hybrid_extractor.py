"""
Hybrid Extractor - Combines Regex and LLM for Optimal Extraction
Uses regex for structured data (fast, accurate) and LLM for complex understanding
"""

from typing import Dict, Any, Optional
import logging
from extractor import TenderExtractor
from llm_extractor import LLMExtractor
from validation import ExtractionValidator, ExtractionConfidenceScorer


class HybridExtractor:
    """
    Hybrid extraction combining regex and LLM strengths

    Strategy:
    1. Regex extraction for structured data (emails, phones, amounts, dates)
    2. LLM extraction for complex understanding (organization, requirements, type)
    3. Validation layer to fix common errors
    4. Confidence scoring for quality assurance
    """

    def __init__(self, model: str = "llama3.2:3b", use_llm: bool = True):
        """
        Initialize hybrid extractor

        Args:
            model: LLM model to use for complex extraction
            use_llm: Whether to use LLM (if False, falls back to regex only)
        """
        self.regex_extractor = TenderExtractor()
        self.llm_extractor = LLMExtractor(model=model) if use_llm else None
        self.validator = ExtractionValidator()
        self.scorer = ExtractionConfidenceScorer()
        self.use_llm = use_llm

        logging.info(f"HybridExtractor initialized with model={model}, use_llm={use_llm}")

    def extract_all(self, tender: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract all structured information using hybrid approach

        Args:
            tender: Tender dictionary with Title, Description, etc.

        Returns:
            Dictionary with extracted and validated information
        """
        # STEP 1: Regex extraction (fast, reliable for structured data)
        regex_result = self.regex_extractor.extract_all(tender)

        if not self.use_llm:
            # No LLM mode - just use regex + validation
            validated = self.validator.validate_all(regex_result, tender)
            confidence = self.scorer.score_extraction(validated, tender)
            validated['extraction_confidence'] = confidence
            validated['extraction_method'] = 'regex_only'
            return validated

        # STEP 2: LLM extraction (smart, handles complex cases)
        try:
            llm_result = self.llm_extractor.extract_all(tender)
        except Exception as e:
            logging.error(f"LLM extraction failed: {e}. Falling back to regex only.")
            validated = self.validator.validate_all(regex_result, tender)
            confidence = self.scorer.score_extraction(validated, tender)
            validated['extraction_confidence'] = confidence
            validated['extraction_method'] = 'regex_fallback'
            return validated

        # STEP 3: Merge results (prioritize based on reliability)
        merged = self._merge_results(regex_result, llm_result, tender)

        # STEP 4: Validation layer (fix common errors)
        validated = self.validator.validate_all(merged, tender)

        # STEP 5: Calculate confidence scores
        confidence = self.scorer.score_extraction(validated, tender)
        validated['extraction_confidence'] = confidence
        validated['extraction_method'] = 'hybrid'

        # Flag for manual review if confidence is low
        if confidence.get('overall', 0) < 0.6:
            validated['needs_manual_review'] = True
        else:
            validated['needs_manual_review'] = False

        return validated

    def _merge_results(
        self,
        regex_result: Dict[str, Any],
        llm_result: Dict[str, Any],
        tender: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Merge regex and LLM results, prioritizing based on reliability

        Strategy:
        - Contact info (emails, phones): Trust regex 100%
        - Financial data: Prefer regex (better context awareness)
        - Dates: Prefer regex for standard formats, LLM for complex
        - Organization: Prefer LLM (better semantic understanding) with regex validation
        - Requirements: Use LLM with regex filtering
        - Type/Language: Trust LLM

        Args:
            regex_result: Results from regex extraction
            llm_result: Results from LLM extraction
            tender: Original tender data

        Returns:
            Merged results
        """
        merged = {}

        # FINANCIAL: Prefer regex (uses context-aware heuristics)
        regex_financial = regex_result.get('financial', {})
        llm_financial = llm_result.get('financial', {})

        merged['financial'] = {
            'bid_security_amount': regex_financial.get('bid_security_amount') or llm_financial.get('bid_security_amount'),
            'bid_security_currency': regex_financial.get('bid_security_currency', 'ETB'),
            'document_fee': regex_financial.get('document_fee') or llm_financial.get('document_fee'),
            'fee_currency': regex_financial.get('fee_currency', 'ETB'),
            'other_amounts': regex_financial.get('other_amounts', [])
        }

        # CONTACT: Trust regex 100% (deterministic patterns)
        merged['contact'] = regex_result.get('contact', {})

        # DATES: Prefer regex for standard formats, validate against LLM
        regex_dates = regex_result.get('dates', {})
        llm_dates = llm_result.get('dates', {})

        merged['dates'] = {
            'closing_date': self._choose_best_date(
                regex_dates.get('closing_date'),
                llm_dates.get('closing_date'),
                regex_dates.get('published_date')
            ),
            'published_date': regex_dates.get('published_date') or llm_dates.get('published_date'),
            'clarification_deadline': regex_dates.get('clarification_deadline') or llm_dates.get('clarification_deadline'),
            'bid_opening': regex_dates.get('bid_opening') or llm_dates.get('bid_opening'),
            'site_visit': regex_dates.get('site_visit') or llm_dates.get('site_visit'),
            'pre_bid_conference': regex_dates.get('pre_bid_conference') or llm_dates.get('pre_bid_conference'),
        }

        # ORGANIZATION: Prefer LLM (better semantic understanding)
        # But will be validated by validation layer
        llm_org = llm_result.get('organization', {})
        regex_org = regex_result.get('organization', {})

        # Use LLM org unless it's clearly wrong
        if llm_org.get('name') and llm_org.get('name') not in self.validator.INVALID_ORG_NAMES:
            merged['organization'] = llm_org
        else:
            merged['organization'] = regex_org

        # REQUIREMENTS: Use LLM (better extraction) but will be filtered by validation
        merged['requirements'] = llm_result.get('requirements', []) or regex_result.get('requirements', [])

        # SPECIFICATIONS: Prefer regex (table extraction is rule-based)
        merged['specifications'] = regex_result.get('specifications', []) or llm_result.get('specifications', [])

        # ADDRESSES: Combine both
        regex_addresses = regex_result.get('addresses', {})
        llm_addresses = llm_result.get('addresses', {})

        merged['addresses'] = {
            'po_boxes': list(set(regex_addresses.get('po_boxes', []) + llm_addresses.get('po_boxes', []))),
            'regions': list(set(regex_addresses.get('regions', []) + llm_addresses.get('regions', [])))
        }

        # LANGUAGE & TYPE: Trust LLM (semantic understanding)
        merged['language_flag'] = llm_result.get('language_flag') or regex_result.get('language_flag', 'english')
        merged['tender_type'] = llm_result.get('tender_type') or regex_result.get('tender_type', 'bid_invitation')
        merged['is_award_notification'] = llm_result.get('is_award_notification', False)

        # LLM-specific fields
        merged['procurement_method'] = llm_result.get('procurement_method', 'open')
        merged['bid_submission_method'] = llm_result.get('bid_submission_method', 'sealed')
        merged['key_items'] = llm_result.get('key_items', [])

        return merged

    def _choose_best_date(
        self,
        regex_date: Optional[str],
        llm_date: Optional[str],
        published_date: Optional[str]
    ) -> Optional[str]:
        """
        Choose the most reliable date between regex and LLM extraction

        Args:
            regex_date: Date from regex extraction
            llm_date: Date from LLM extraction
            published_date: Published date for validation

        Returns:
            Best date choice
        """
        # If both are None, return None
        if not regex_date and not llm_date:
            return None

        # If only one exists, use it
        if regex_date and not llm_date:
            return regex_date
        if llm_date and not regex_date:
            return llm_date

        # Both exist - validate which is more reasonable
        if published_date:
            try:
                from datetime import datetime
                pub_dt = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                regex_dt = datetime.fromisoformat(regex_date.replace('Z', '+00:00'))
                llm_dt = datetime.fromisoformat(llm_date.replace('Z', '+00:00'))

                # Calculate days difference
                regex_diff = (regex_dt - pub_dt).days
                llm_diff = (llm_dt - pub_dt).days

                # Prefer date that's within reasonable range (1-180 days)
                regex_reasonable = 1 <= regex_diff <= 180
                llm_reasonable = 1 <= llm_diff <= 180

                if regex_reasonable and not llm_reasonable:
                    return regex_date
                elif llm_reasonable and not regex_reasonable:
                    return llm_date
                elif regex_reasonable and llm_reasonable:
                    # Both reasonable, prefer regex (more deterministic)
                    return regex_date
                else:
                    # Neither reasonable, prefer regex as fallback
                    return regex_date
            except:
                # Parsing failed, prefer regex
                return regex_date

        # No published date to validate against, prefer regex
        return regex_date


class ContentGeneratorWrapper:
    """
    Wrapper for content generation that uses hybrid extraction results
    """

    def __init__(self, model: str = "llama3.2:3b"):
        """
        Initialize content generator wrapper

        Args:
            model: LLM model to use
        """
        from llm_extractor import ContentGenerator
        self.generator = ContentGenerator(model=model)

    def generate_content(self, tender: Dict, extracted: Dict) -> Dict[str, str]:
        """
        Generate content using hybrid extraction results

        Args:
            tender: Original tender data
            extracted: Extracted and validated data from hybrid extractor

        Returns:
            Dictionary with summary, clean_description, highlights
        """
        return self.generator.generate_content(tender, extracted)


if __name__ == "__main__":
    """Test hybrid extractor"""
    logging.basicConfig(level=logging.INFO)

    # Test tender
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

    print("Testing Hybrid Extractor...")
    print("=" * 60)

    # Test with LLM
    print("\n1. Testing with LLM (hybrid mode):")
    extractor = HybridExtractor(model="llama3.2:3b", use_llm=True)
    result = extractor.extract_all(test_tender)

    print(f"\nOrganization: {result['organization']}")
    print(f"Financial: {result['financial']}")
    print(f"Contact: {result['contact']}")
    print(f"Dates: {result['dates']}")
    print(f"Confidence Scores: {result.get('extraction_confidence', {})}")
    print(f"Extraction Method: {result.get('extraction_method')}")
    print(f"Needs Manual Review: {result.get('needs_manual_review', False)}")

    # Test without LLM
    print("\n" + "=" * 60)
    print("\n2. Testing without LLM (regex only mode):")
    extractor_no_llm = HybridExtractor(use_llm=False)
    result_no_llm = extractor_no_llm.extract_all(test_tender)

    print(f"\nOrganization: {result_no_llm['organization']}")
    print(f"Financial: {result_no_llm['financial']}")
    print(f"Contact: {result_no_llm['contact']}")
    print(f"Extraction Method: {result_no_llm.get('extraction_method')}")
