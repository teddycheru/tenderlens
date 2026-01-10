"""
Content Generator Module
Uses Ollama with Llama 3.2 3B to generate clean, user-friendly tender content
Memory-optimized for 8GB RAM systems
"""

import json
import ollama
from typing import Dict, Any, Optional
import time
from utils import TextSanitizer


class ContentGenerator:
    """Generate clean content using Qwen 2.5 7B via Ollama"""

    def __init__(self, model: str = "qwen2.5:7b", check_running: bool = True):
        self.model = model
        self.max_tokens = 512  # Memory efficient
        self.temperature = 0.1  # Very low temperature for deterministic, structured output

        if check_running:
            self._check_ollama_running()

    def _check_ollama_running(self) -> bool:
        """Check if Ollama is running"""
        try:
            # Try to list models to check if Ollama is running
            models = ollama.list()
            print(f"✓ Ollama is running")
            print(f"  Model: {self.model}")
            return True
        except Exception as e:
            print(f"⚠ Warning: Ollama may not be running: {e}")
            print(f"  Please make sure Ollama is running: ollama serve")
            return False

    def generate_summary(self, description: str, title: str, extracted_data: Dict[str, Any] = None) -> Optional[str]:
        """
        Generate a 2-3 sentence executive summary

        Args:
            description: Raw HTML description
            title: Tender title
            extracted_data: Extracted structured data with dates

        Returns:
            Generated summary or None if failed
        """
        # Clean HTML first
        from extractor import TenderExtractor
        extractor = TenderExtractor()
        clean_text = extractor.clean_html_content(description)

        # Sanitize text to remove problematic content
        clean_text = TextSanitizer.sanitize_for_llm(clean_text)
        title = TextSanitizer.sanitize_for_llm(title)

        # Build context from extracted data
        context_parts = []
        if extracted_data:
            dates = extracted_data.get('dates', {})
            if dates.get('closing_date'):
                context_parts.append(f"Bid Submission Deadline: {dates['closing_date']}")
            if dates.get('bid_opening'):
                context_parts.append(f"Bid Opening: {dates['bid_opening']}")

            financial = extracted_data.get('financial', {})
            if financial.get('bid_security_amount'):
                context_parts.append(f"Bid Security: {financial['bid_security_amount']} {financial.get('bid_security_currency', 'ETB')}")

            org = extracted_data.get('organization', {})
            if org.get('name') and org.get('name') != 'Not specified':
                context_parts.append(f"Organization: {org['name']}")

        context_info = "\n".join(context_parts) if context_parts else ""

        prompt = f"""<task>Generate a concise executive summary for this tender</task>

<instructions>
- Write exactly 2-3 sentences
- Include: what is being procured, key requirements, and bid submission deadline
- Use the EXACT deadline from the extracted data below (NOT document availability date)
- Be specific and factual
- Do not add any headers or labels
</instructions>

<title>{title}</title>

<description>
{clean_text[:1500]}
</description>

<extracted_data>
{context_info}
</extracted_data>

<summary>"""

        result = self._call_ollama(prompt, max_tokens=200)
        # Clean up any trailing markers
        if result:
            result = result.replace('</summary>', '').strip()
        return result

    def generate_clean_description(self, description: str) -> Optional[str]:
        """
        Generate a clean, well-formatted description without HTML
        Preserves all important details from the original description

        Args:
            description: Raw HTML description

        Returns:
            Clean formatted description
        """
        from extractor import TenderExtractor
        extractor = TenderExtractor()
        clean_text = extractor.clean_html_content(description)

        # Sanitize text to remove problematic content
        clean_text = TextSanitizer.sanitize_for_llm(clean_text)

        # Use the full text, up to reasonable length
        text_to_process = TextSanitizer.truncate_for_llm(clean_text, max_length=3500)

        prompt = f"""<task>Reformat tender document into clear, structured text</task>

<instructions>
- Organize into clear sections with headers (##)
- Use bullet points for lists
- Preserve ALL important details, dates, amounts, and requirements
- Remove HTML artifacts and fix formatting
- Keep professional tone
- Do not add information not present in original
- Do not repeat information
</instructions>

<raw_content>
{text_to_process}
</raw_content>

<formatted_content>"""

        result = self._call_ollama(prompt, max_tokens=800)
        if result:
            result = result.replace('</formatted_content>', '').strip()
        return result

    def extract_key_highlights(self, extracted_data: Dict[str, Any], title: str) -> Optional[str]:
        """
        Generate key highlights based on extracted data

        Args:
            extracted_data: Extracted structured data
            title: Tender title

        Returns:
            Key highlights as bullet points
        """
        highlights_prompt = self._build_highlights_prompt(extracted_data, title)

        prompt = f"""<task>Generate key highlights for this tender</task>

<instructions>
- List 5-7 most important points as bullet points
- MUST include financial information (bid security, fees) if available
- Include key deadlines and dates
- Include main requirements
- Be concise and specific
- Use format: • Point here
</instructions>

{highlights_prompt}

<highlights>"""

        result = self._call_ollama(prompt, max_tokens=350)
        if result:
            result = result.replace('</highlights>', '').strip()
        return result

    def _build_highlights_prompt(self, extracted_data: Dict[str, Any], title: str) -> str:
        """Build prompt with extracted data for highlights"""
        info_lines = [
            f"Tender Title: {title}",
            f"Category: {extracted_data.get('category', 'Not specified')}"
        ]

        financial = extracted_data.get('financial', {})
        if financial.get('bid_security_amount'):
            info_lines.append(f"Bid Security: {financial['bid_security_amount']:,.2f} {financial.get('bid_security_currency', 'ETB')}")

        if financial.get('document_fee'):
            info_lines.append(f"Document Fee: {financial['document_fee']:,.2f} {financial.get('fee_currency', 'ETB')}")

        dates = extracted_data.get('dates', {})
        if dates.get('closing_date'):
            info_lines.append(f"Submission Deadline: {dates['closing_date']}")
        if dates.get('clarification_deadline'):
            info_lines.append(f"Clarification Deadline: {dates['clarification_deadline']}")
        if dates.get('bid_opening'):
            info_lines.append(f"Bid Opening: {dates['bid_opening']}")
        if dates.get('site_visit'):
            info_lines.append(f"Site Visit: {dates['site_visit']}")
        if dates.get('pre_bid_conference'):
            info_lines.append(f"Pre-bid Conference: {dates['pre_bid_conference']}")

        org = extracted_data.get('organization', {})
        if org.get('name') and org.get('name') != 'Not specified':
            info_lines.append(f"Organization: {org['name']}")

        region = extracted_data.get('region', '')
        if region:
            info_lines.append(f"Location: {region}")

        contact = extracted_data.get('contact', {})
        if contact.get('emails'):
            info_lines.append(f"Contact Email: {', '.join(contact['emails'][:2])}")
        if contact.get('phones'):
            info_lines.append(f"Contact Phone: {', '.join(contact['phones'][:2])}")

        requirements = extracted_data.get('requirements', [])
        if requirements:
            info_lines.append(f"Key Requirements: {', '.join(requirements[:5])}")

        return "<tender_information>\n" + "\n".join(info_lines) + "\n</tender_information>"

    def _call_ollama(self, prompt: str, max_tokens: int = 512) -> Optional[str]:
        """
        Call Ollama API with memory-efficient settings

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text or None if failed
        """
        try:
            # Use ollama library to call the model
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={
                    'temperature': self.temperature,
                    'top_k': 40,
                    'top_p': 0.9
                }
            )

            if response and 'response' in response:
                output = response['response'].strip()
                if output:
                    return output
                else:
                    print(f"⚠ Empty response from model")
                    return None
            else:
                print(f"⚠ Unexpected response format from Ollama")
                return None

        except Exception as e:
            print(f"⚠ Error calling Ollama: {e}")
            return None

    def batch_generate(self, tenders: list, extracted_data_list: list, skip_on_error: bool = True) -> list:
        """
        Generate content for multiple tenders with memory management

        Args:
            tenders: List of tender dictionaries
            extracted_data_list: List of extracted data dictionaries
            skip_on_error: Skip on error instead of failing

        Returns:
            List of generated content dictionaries
        """
        results = []

        for idx, (tender, extracted) in enumerate(zip(tenders, extracted_data_list)):
            print(f"\n[{idx+1}/{len(tenders)}] Generating content...")

            generated = {
                'summary': None,
                'clean_description': None,
                'highlights': None,
                'generation_errors': []
            }

            try:
                # Generate summary
                print(f"  - Generating summary...")
                summary = self.generate_summary(
                    tender.get('Description', ''),
                    tender.get('Title', '')
                )
                generated['summary'] = summary

                # Generate clean description
                print(f"  - Generating clean description...")
                clean_desc = self.generate_clean_description(
                    tender.get('Description', '')
                )
                generated['clean_description'] = clean_desc

                # Extract highlights
                print(f"  - Extracting highlights...")
                highlights = self.extract_key_highlights(
                    extracted,
                    tender.get('Title', '')
                )
                generated['highlights'] = highlights

            except Exception as e:
                error_msg = f"Error generating content: {str(e)}"
                print(f"  ✗ {error_msg}")
                generated['generation_errors'].append(error_msg)

                if not skip_on_error:
                    raise

            results.append(generated)

            # Memory management: garbage collection
            if (idx + 1) % 10 == 0:
                import gc
                gc.collect()
                print(f"  [Memory cleanup after batch]")

        return results


if __name__ == "__main__":
    # Test content generator
    generator = ContentGenerator()

    test_tender = {
        'Description': '''<p>Ministry of Health invites qualified bidders to supply medical equipment.</p>
        <p>Bid security: <strong>Birr 50,000</strong></p>
        <p>Document fee: <strong>Birr 300</strong></p>
        <ul><li>Trade License required</li><li>Tax certificate</li></ul>''',
        'Title': 'Ministry of Health - Medical Equipment Supply'
    }

    test_extracted = {
        'financial': {'bid_security_amount': 50000},
        'organization': {'name': 'Ministry of Health'},
        'region': 'Addis Ababa',
        'requirements': ['Trade License', 'Tax Certificate']
    }

    print("Testing content generation...")
    print("\nGenerating summary...")
    summary = generator.generate_summary(test_tender['Description'], test_tender['Title'])
    print(f"Summary: {summary}")

    print("\nGenerating clean description...")
    clean = generator.generate_clean_description(test_tender['Description'])
    print(f"Clean description: {clean}")

    print("\nExtracting highlights...")
    highlights = generator.extract_key_highlights(test_extracted, test_tender['Title'])
    print(f"Highlights: {highlights}")
