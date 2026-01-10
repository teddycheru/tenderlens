"""
OpenAI Embedding Service - Alternative to local embeddings.

Uses OpenAI's text-embedding-3-small API for embeddings.
Requires OPENAI_API_KEY in environment.

To use this instead of local embeddings:
1. Set EMBEDDING_PROVIDER=openai in .env
2. Set AI_OPENAI_API_KEY in .env
3. Restart services

Cost: ~$0.02 per 1M tokens (~$5-10/month for 1,500 tenders/day)
"""

from openai import OpenAI
from typing import List
import os
from app.models.tender import Tender
from app.models.company_profile import CompanyTenderProfile
import logging

logger = logging.getLogger(__name__)


class OpenAIEmbeddingService:
    """
    Service for generating embeddings using OpenAI API.

    Model: text-embedding-3-small (1536 dimensions)
    - Fast: API call ~100-200ms
    - No download needed
    - Costs: $0.02 per 1M tokens
    """

    MODEL_NAME = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS = 1536

    _client: OpenAI = None

    @classmethod
    def get_client(cls) -> OpenAI:
        """Get or create OpenAI client."""
        if cls._client is None:
            api_key = os.getenv('AI_OPENAI_API_KEY')
            if not api_key:
                raise ValueError("AI_OPENAI_API_KEY not set in environment")
            cls._client = OpenAI(api_key=api_key)
        return cls._client

    @classmethod
    def generate_tender_embedding(cls, tender: Tender) -> List[float]:
        """
        Generate embedding for a tender using OpenAI API.

        Args:
            tender: Tender model instance

        Returns:
            List of floats (embedding vector, 1536 dimensions)
        """
        # Prepare text (same as local service)
        text_parts = []

        if tender.title:
            text_parts.append(tender.title)

        if tender.category:
            text_parts.append(f"Category: {tender.category}")
        if tender.region:
            text_parts.append(f"Region: {tender.region}")

        if tender.description:
            text_parts.append(tender.description[:2000])

        if tender.ai_summary:
            text_parts.append(tender.ai_summary)

        text = " ".join(text_parts).strip()

        if not text:
            logger.warning(f"Tender {tender.id} has no text for embedding")
            return [0.0] * cls.EMBEDDING_DIMENSIONS

        # Call OpenAI API
        try:
            client = cls.get_client()
            response = client.embeddings.create(
                model=cls.MODEL_NAME,
                input=text
            )
            embedding = response.data[0].embedding
            return embedding

        except Exception as e:
            logger.error(f"Error generating OpenAI embedding for tender {tender.id}: {e}")
            raise

    @classmethod
    def generate_profile_embedding(cls, profile: CompanyTenderProfile) -> List[float]:
        """
        Generate embedding for a company profile using OpenAI API.

        Args:
            profile: CompanyTenderProfile model instance

        Returns:
            List of floats (embedding vector, 1536 dimensions)
        """
        text_parts = []

        if profile.primary_sector:
            text_parts.append(f"Primary sector: {profile.primary_sector}")

        if profile.active_sectors:
            text_parts.append(f"Active in: {', '.join(profile.active_sectors)}")

        if profile.sub_sectors:
            text_parts.append(f"Specializes in: {', '.join(profile.sub_sectors)}")

        if profile.keywords:
            text_parts.append(f"Capabilities: {', '.join(profile.keywords)}")

        if profile.preferred_regions:
            text_parts.append(f"Operates in: {', '.join(profile.preferred_regions)}")

        text = " ".join(text_parts).strip()

        if not text:
            logger.warning(f"Profile {profile.id} has no text for embedding")
            return [0.0] * cls.EMBEDDING_DIMENSIONS

        # Call OpenAI API
        try:
            client = cls.get_client()
            response = client.embeddings.create(
                model=cls.MODEL_NAME,
                input=text
            )
            embedding = response.data[0].embedding
            return embedding

        except Exception as e:
            logger.error(f"Error generating OpenAI embedding for profile {profile.id}: {e}")
            raise


# Create singleton instance
openai_embedding_service = OpenAIEmbeddingService()
