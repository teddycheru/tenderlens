"""
AI Summarization service using OpenAI GPT-4 or Anthropic Claude.

Note: For offline processing without API keys, use the content-generator script
which processes tenders via Ollama with Llama 3.2 3B LLM and generates JSON output
that is then imported into the database via JSONContentImporter.

Prompts are loaded from app.core.ai_prompts for easy customization.
"""

from app.core.ai_config import ai_settings
from app.core import ai_prompts
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class Summarizer:
    """
    Generate summaries using OpenAI GPT-4 or Anthropic Claude.

    For offline processing without API keys, use the content-generator script instead.
    That script processes tenders via Ollama with Llama 3.2 3B and outputs JSON that
    can be imported via JSONContentImporter.

    Note: Requires openai or anthropic package to be installed.
    Install with: pip install openai==1.3.0 or pip install anthropic==0.7.0
    """

    def __init__(self):
        """Initialize AI client based on available API keys."""
        self.client = None
        self.provider = None

        # Try OpenAI first
        if ai_settings.OPENAI_API_KEY and ai_settings.OPENAI_API_KEY != "your-openai-api-key-here":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=ai_settings.OPENAI_API_KEY)
                self.provider = "openai"
                logger.info("✅ OpenAI client initialized")
            except ImportError:
                print("Warning: openai package not installed. Install with: pip install openai==1.3.0")
            except Exception as e:
                print(f"Warning: Failed to initialize OpenAI client: {e}")

        # Fallback to Anthropic
        elif ai_settings.ANTHROPIC_API_KEY:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=ai_settings.ANTHROPIC_API_KEY)
                self.provider = "anthropic"
                logger.info("✅ Anthropic client initialized")
            except ImportError:
                print("Warning: anthropic package not installed. Install with: pip install anthropic==0.7.0")
            except Exception as e:
                print(f"Warning: Failed to initialize Anthropic client: {e}")

    def summarize_tender(self, text: str, max_words: int = None) -> str:
        """
        Generate a concise summary of tender document.

        Requires OpenAI/Anthropic API to be configured.
        For offline processing, use the content-generator script instead.

        Args:
            text: Tender document text to summarize
            max_words: Maximum number of words in summary (default from config)

        Returns:
            Generated summary text

        Raises:
            RuntimeError: If API is not configured
        """
        if not self.client or not self.provider:
            raise RuntimeError(
                "No AI API configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY.\n"
                "Alternatively, use the content-generator script for offline processing:\n"
                "  1. Run: python content-generator/process_tenders.py your_file.csv\n"
                "  2. Import JSON: JSONContentImporter.import_from_json('output/processed_tenders.json')"
            )

        if max_words is None:
            max_words = ai_settings.SUMMARY_MAX_LENGTH

        # Truncate input text to avoid token limits (roughly 4 chars per token)
        max_input_chars = ai_settings.MAX_TOKENS_PER_REQUEST * 4
        text = text[:max_input_chars]

        try:
            user_prompt = ai_prompts.TENDER_SUMMARY_USER_PROMPT.format(
                max_words=max_words,
                text=text
            )

            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=ai_settings.OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": ai_prompts.TENDER_SUMMARY_SYSTEM_MESSAGE
                        },
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ],
                    max_tokens=ai_settings.OPENAI_MAX_TOKENS,
                    temperature=ai_settings.OPENAI_TEMPERATURE
                )
                summary = response.choices[0].message.content.strip()
                logger.info("✅ Summary generated via OpenAI")
                return summary

            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=ai_settings.ANTHROPIC_MODEL,
                    max_tokens=ai_settings.OPENAI_MAX_TOKENS,
                    temperature=ai_settings.OPENAI_TEMPERATURE,
                    system=ai_prompts.TENDER_SUMMARY_SYSTEM_MESSAGE,
                    messages=[
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ]
                )
                summary = response.content[0].text.strip()
                logger.info("✅ Summary generated via Anthropic")
                return summary

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise

    def extract_tender_details(self, text: str) -> str:
        """
        Extract detailed tender information (scope, qualifications, issuer, etc).

        Returns structured details NOT including budget.
        Requires OpenAI/Anthropic API to be configured.

        Args:
            text: Tender document text

        Returns:
            Structured details as formatted string

        Raises:
            RuntimeError: If API is not configured
        """
        if not self.client or not self.provider:
            raise RuntimeError(
                "No AI API configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY.\n"
                "Alternatively, use the content-generator script for offline processing."
            )

        # Truncate input
        max_input_chars = ai_settings.MAX_TOKENS_PER_REQUEST * 4
        text = text[:max_input_chars]

        try:
            user_prompt = ai_prompts.TENDER_DETAILS_USER_PROMPT.format(text=text)

            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=ai_settings.OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": ai_prompts.TENDER_DETAILS_SYSTEM_MESSAGE
                        },
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ],
                    max_tokens=1500,  # Larger for detailed output
                    temperature=0.2   # Lower temperature for factual accuracy
                )
                logger.info("✅ Details extracted via OpenAI")
                return response.choices[0].message.content.strip()

            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=ai_settings.ANTHROPIC_MODEL,
                    max_tokens=1500,
                    temperature=0.2,
                    system=ai_prompts.TENDER_DETAILS_SYSTEM_MESSAGE,
                    messages=[
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ]
                )
                logger.info("✅ Details extracted via Anthropic")
                return response.content[0].text.strip()

        except Exception as e:
            logger.error(f"Error extracting details: {e}")
            raise

    def quick_scan(self, title: str, description: str) -> str:
        """
        Generate a quick 1-2 sentence scan for tender cards.

        Requires OpenAI/Anthropic API to be configured.
        If API is not available, returns a simple title preview.

        Args:
            title: Tender title
            description: Tender description (will be truncated)

        Returns:
            Quick insight text (max 25 words), or title preview if API unavailable
        """
        # Truncate description to save tokens
        description = description[:500]

        # If no client available, return simple fallback
        if not self.client or not self.provider:
            logger.debug("No AI API configured, returning title preview for quick scan")
            return f"{title[:50]}... Click to view details."

        try:
            user_prompt = ai_prompts.QUICK_SCAN_USER_PROMPT.format(
                max_words=ai_settings.QUICK_SCAN_MAX_LENGTH,
                title=title,
                description=description
            )

            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=ai_settings.OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": ai_prompts.QUICK_SCAN_SYSTEM_MESSAGE
                        },
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ],
                    max_tokens=100,
                    temperature=ai_settings.OPENAI_TEMPERATURE
                )
                logger.info("✅ Quick scan generated via OpenAI")
                return response.choices[0].message.content.strip()

            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=ai_settings.ANTHROPIC_MODEL,
                    max_tokens=100,
                    temperature=ai_settings.OPENAI_TEMPERATURE,
                    system=ai_prompts.QUICK_SCAN_SYSTEM_MESSAGE,
                    messages=[
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ]
                )
                logger.info("✅ Quick scan generated via Anthropic")
                return response.content[0].text.strip()

        except Exception as e:
            logger.warning(f"Error generating quick scan: {e}")
            # Return simple fallback if API fails
            return f"{title[:50]}... Click to view details."

    def is_available(self) -> bool:
        """
        Check if AI summarization is available.

        Returns:
            True if AI client is configured, False otherwise
        """
        return self.client is not None and ai_settings.AI_ENABLED


# Global summarizer instance - initialized lazily to avoid blocking app startup
_summarizer_instance = None

def get_summarizer():
    """
    Get or initialize Summarizer lazily.

    This prevents blocking app startup when AI models are initializing.
    The service is loaded on first use instead of at import time.
    """
    global _summarizer_instance
    if _summarizer_instance is None:
        _summarizer_instance = Summarizer()
    return _summarizer_instance

# For backwards compatibility, create a property-like object
class _LazySummarizer:
    """Lazy loader for Summarizer service."""
    def __getattr__(self, name):
        return getattr(get_summarizer(), name)

summarizer = _LazySummarizer()
