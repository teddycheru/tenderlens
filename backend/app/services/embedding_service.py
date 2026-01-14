"""
Embedding Service - Generate vector embeddings for tenders and company profiles.

Uses sentence-transformers with BGE-M3 (1024 dimensions).
Multilingual support, high-quality semantic embeddings.
"""

from sentence_transformers import SentenceTransformer
from typing import List, Optional
import numpy as np
from app.models.tender import Tender
from app.models.company_profile import CompanyTenderProfile
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating embeddings using sentence-transformers.

    Model: BGE-M3 (1024 dimensions)
    - Speed: ~1.8s per tender
    - Size: 2.2GB download
    - Multilingual: 100+ languages
    - High quality semantic embeddings
    """

    # MODEL_NAME = "BAAI/bge-m3"
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2" # Smaller model for testing/demo
    EMBEDDING_DIMENSIONS = 384  # 1024 for BGE-M3, 384 for MiniLM-L6-v2

    _model: Optional[SentenceTransformer] = None

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        """
        Lazy load the embedding model (singleton pattern).
        Model is loaded once and reused across requests.
        """
        if cls._model is None:
            logger.info(f"Loading embedding model: {cls.MODEL_NAME}")
            cls._model = SentenceTransformer(cls.MODEL_NAME, device='cpu')
            logger.info(f"Model loaded successfully. Dimensions: {cls.EMBEDDING_DIMENSIONS}")
        return cls._model

    @classmethod
    def _extract_project_text(cls, title: str) -> str:
        """
        Extract actual project/procurement text by removing organization boilerplate.
        Critical: Focuses on WHAT is being procured, not WHO is procuring.

        Scalable pattern matching: Specific patterns first, general fallbacks last.
        """
        import re

        # COMPREHENSIVE PATTERNS - Ordered by specificity (most specific → most general)
        boilerplate_patterns = [
            # === FINANCING/WORLD BANK PATTERNS ===
            r"intends?\s+to\s+apply\s+part\s+of\s+the\s+proceeds.*?(?:for\s+the\s+)?(supply|procurement|contract)\s+(?:of\s+|for\s+(?:the\s+)?)",
            r"has\s+received\s+financing.*?toward.*?(?:for\s+the\s+)?(supply|procurement|contract)\s+(?:of\s+|for\s+(?:the\s+)?)",

            # === PUBLIC TENDER NOTICES ===
            r"public\s+tender\s+notice\s+for\s+(?:sale\s+of\s+)?",

            # === INVITATION PATTERNS WITH SPECIFIC ACTIONS ===
            r"invites?\s+(?:interested\s+)?(?:and\s+)?(?:eligible\s+)?(?:potential\s+)?bidders?\s+for\s+the\s+(?:procurement|supply|sales?)\s+of\s+",
            r"has\s+invites?\s+(?:interested\s+)?(?:and\s+)?(?:potential\s+)?bidders?\s+for\s+the\s+(?:procurement|supply)\s+of\s+",
            r"would\s+like\s+to\s+invite\s+(?:eligible\s+)?(?:and\s+)?(?:interested\s+)?(?:reputable\s+)?(?:bidders?|companies|firms)\s+for\s+the\s+(?:procurement|sales?|supply)\s+of\s+",
            r"(?:wants?|like)\s+to\s+invite\s+(?:competent\s+)?(?:interested\s+)?(?:eligible\s+)?(?:and\s+)?(?:qualified\s+)?(?:supplier|bidders?|firms)\s+to\s+(?:provide|supply)\s+",

            # === "INVITES BIDDERS TO" PATTERNS ===
            r"(?:now\s+)?invites?\s+(?:interested\s+)?(?:and\s+)?(?:qualified\s+)?bidders?\s+to\s+(?:submit|supply)\s+(?:scaled\s+)?bids?\s+for\s+(?:the\s+)?(?:provision\s+of\s+)?(?:services?\s+for\s+(?:the\s+)?)?",
            r"invites?\s+(?:interested\s+)?(?:&|and)\s+(?:qualified\s+)?bidders?\s+to\s+(?:supply|installation|implementation)\s*,?\s*",
            r"invites?\s+(?:interested\s+)?(?:and\s+)?(?:qualified\s+)?bidders?\s+to\s+(?:submit|participate)\s+",

            # === "INVITES BIDS FROM" PATTERNS ===
            r"invites?\s+bids?\s+from\s+(?:interested\s+)?(?:and\s+)?(?:eligible\s+)?bidders?\s+(?:\([^)]+\)\s*,?\s*)?for\s+the\s+(?:procurement|supply)\s+of\s+",
            r"here\s+by\s+invites?\s+(?:wax\s+)?sealed\s+bids?\s*,?\s*from\s+(?:qualified\s+)?(?:and\s+)?(?:eligible\s+)?",

            # === "PARTICIPATE IN THE BID" PATTERNS ===
            r"invites?\s+all\s+interested\s+and\s+eligible\s+bidders?\s+to\s+participate\s+in\s+the\s+bid\s+for\s+the\s+(?:supply|procurement)\s+of\s+",

            # === "INTENDS TO INVITE" PATTERNS ===
            r"intends?\s+to\s+invite\s+qualified\s+.*?for\s+",

            # === "INVITE YOUR/ESTEEMED" PATTERNS ===
            r"invite\s+your\s+esteemed\s+bidders?\s+(?:with.*?)?(?:to|for)\s+",

            # === EXPRESSION OF INTEREST PATTERNS ===
            r"hereby\s+seeks?\s+expressions?\s+of\s+interest\s+from\s+",
            r"(?:would\s+)?like\s+to\s+receive\s+expressions?\s+of\s+interest\s+(?:\(EOIs?\)\s+)?from\s+.*?(?:for\s+)?",
            r"seeks?\s+expressions?\s+of\s+interest\s+(?:for|in)\s+",

            # === "WANTS TO" PATTERNS ===
            r"wants?\s+to\s+conduct\s+a\s+bid\s+for\s+(?:the\s+)?(?:selection\s+of\s+)?",
            r"wants?\s+to\s+(?:construct|invite|provide)\s+(?:a\s+)?",

            # === "TO PARTICIPATE" PATTERNS ===
            r"would\s+like\s+to\s+invite\s+interested\s+.*?service\s+providers\s+to\s+participate\s+in\s+(?:an\s+)?(?:open\s+)?(?:bid|tender)\s+(?:for|on)\s+",

            # === "FOR THE [SERVICE]" PATTERNS ===
            r"invites?\s+(?:qualified\s+)?(?:and\s+)?(?:eligible\s+)?bidders?\s+for\s+the\s+(?:printing|cleaning|construction|repair|maintenance)\s+service\s+(?:of\s+)?",

            # === "INVITES...THOSE WHO" PATTERNS (medical, qualified, etc.) ===
            r"invites?\s+(?:interested\s+)?(?:and\s+)?(?:experienced\s+)?(?:medical\s+)?service\s+providers\s*,\s*those\s+who\s+.*?(?:for|to)\s+",

            # === GENERIC INVITATION PATTERNS ===
            r"(?:here\s+)?now\s+invites?\s+sealed\s+bids?\s+from\s+.*?(?:bidders?\s+)?for\s+(?:the\s+)?(?:procurement|construction|supply|installation)\s+of\s+",
            r"invites?\s+(?:interested\s+)?(?:and\s+)?(?:eligible\s+)?bidders?\s+(?:all\s+over.*?)?for\s+(?:the\s+)?(?:procurement|construction|supply|installation|purchase)\s+(?:of\s+|and\s+installation\s+of\s+)",
            r"would\s+like\s+to\s+invite\s+.*?for\s+(?:the\s+)?(?:procurement|construction|supply|implementing)\s+(?:of\s+)?",
            r"invites?\s+to\s+all\s+interested\s+(?:&|and)\s+eligible\s+.*?for\s+the\s+(?:purchase|procurement|supply)\s+of\s+",

            # === GENERAL "INVITES [ENTITY] FOR" PATTERNS ===
            r"invites?\s+(?:all\s+)?interested\s+(?:and|&)\s+(?:eligible\s+)?(?:bidders?|suppliers?|firms)\s+(?:by\s+this.*?)?for\s+(?:the\s+)?",
            r"invites?\s+(?:eligible\s+)?(?:bidders?|suppliers?)\s+(?:by\s+this.*?)?for\s+(?:the\s+)?",

            # === SEEKING/LOOKING PATTERNS ===
            r"(?:is\s+)?seeking\s+(?:a\s+)?service\s+provider\s+for\s+",
            r"looks\s+for\s+(?:consultancy\s+)?service\s+for\s+",

            # === HIRING/PREQUALIFICATION PATTERNS ===
            r"would\s+like\s+to\s+(?:hire|prequalify)\s+",
            r"we\s+invite\s+you\s+to\s+submit\s+a\s+proposal\s+for\s+",

            # === GENERIC SEALED BIDS ===
            r"invites?\s+sealed\s+bids?\s+from\s+",

            # === NOTIFICATION PATTERNS ===
            r"notify\s+tender\s+award\s+on\s+"
        ]

        # Try each pattern in order
        for pattern_str in boilerplate_patterns:
            pattern = re.compile(pattern_str, flags=re.IGNORECASE)
            match = pattern.search(title)
            if match:
                extracted = title[match.end():].strip()

                # Post-extraction cleanup
                # Remove leftover connector words at start
                extracted = re.sub(r'^(?:the\s+|a\s+|an\s+|of\s+|for\s+|to\s+|in\s+)+', '', extracted, flags=re.IGNORECASE)

                # Remove residual noise phrases
                extracted = re.sub(r'^(?:qualified\s+)?(?:eligible\s+)?(?:and\s+)?bidders?\s+(?:all\s+over.*?)?for\s+(?:the\s+)?', '', extracted, flags=re.IGNORECASE)
                extracted = re.sub(r'^(?:different\s+)?(?:various\s+)?', '', extracted, flags=re.IGNORECASE)

                return extracted.strip()

        # No pattern matched - return original
        return title

    @classmethod
    def generate_tender_embedding(cls, tender: Tender) -> List[float]:
        """
        Generate embedding for a tender.

        CRITICAL: Extracts project text to focus on procurement need, not issuer.
        Example: "ABC IT Company invites bids for Accounting" → embeds "Accounting"

        Combines:
        - Extracted project text from title
        - Description
        - AI summary (if available)
        - Category and region (as context)

        Args:
            tender: Tender model instance

        Returns:
            List of floats (embedding vector)
        """
        # Prepare text for embedding
        text_parts = []

        # Title - EXTRACT PROJECT TEXT ONLY (not issuer info)
        if tender.title:
            project_text = cls._extract_project_text(tender.title)
            text_parts.append(project_text)

        # Category and region as context
        if tender.category:
            text_parts.append(f"Category: {tender.category}")
        if tender.region:
            text_parts.append(f"Region: {tender.region}")

        # Description
        if tender.description:
            # Limit description to avoid token limits
            desc = tender.description[:2000]
            text_parts.append(desc)

        # AI summary (if available, usually better than raw description)
        if tender.ai_summary:
            text_parts.append(tender.ai_summary)

        # Combine all parts
        text = " ".join(text_parts).strip()

        if not text:
            logger.warning(f"Tender {tender.id} has no text for embedding")
            # Return zero vector if no text
            return [0.0] * cls.EMBEDDING_DIMENSIONS

        # Generate embedding
        model = cls.get_model()
        embedding = model.encode(
            text,
            normalize_embeddings=True,  # L2 normalization for cosine similarity
            show_progress_bar=False
        )

        # Convert to list for JSON serialization
        return embedding.tolist()

    @classmethod
    def generate_profile_embedding(cls, profile: CompanyTenderProfile) -> List[float]:
        """
        Generate embedding for a company profile.

        Creates a rich, query-like text that matches well with tender descriptions.
        This approach significantly improves semantic similarity matching.

        Combines:
        - Primary sector
        - Active sectors (expanded with descriptive text)
        - Sub-sectors
        - Keywords (repeated and expanded)
        - Preferred regions
        - Certifications
        - Company context

        Args:
            profile: CompanyTenderProfile model instance

        Returns:
            List of floats (embedding vector)
        """
        text_parts = []

        # Build a rich, descriptive query-like text
        # This helps the embedding model understand what tenders to match

        # Start with a natural language description
        if profile.active_sectors:
            sectors_text = ", ".join(profile.active_sectors)
            text_parts.append(
                f"Looking for tenders and procurement opportunities in {sectors_text}."
            )

        # Add keywords multiple times with context to boost their importance
        if profile.keywords:
            keywords_text = ", ".join(profile.keywords)
            text_parts.append(f"Our core capabilities include: {keywords_text}.")
            text_parts.append(f"We provide services in: {keywords_text}.")
            # Repeat keywords to increase weight
            text_parts.append(keywords_text)

        # Primary sector with context
        if profile.primary_sector:
            text_parts.append(
                f"We are a {profile.primary_sector} company seeking relevant tenders."
            )

        # Sub-sectors (specializations) with expanded text
        if profile.sub_sectors:
            subsectors_text = ", ".join(profile.sub_sectors)
            text_parts.append(
                f"We specialize in {subsectors_text} and seek related opportunities."
            )

        # Preferred regions with context
        if profile.preferred_regions:
            regions_text = ", ".join(profile.preferred_regions)
            text_parts.append(
                f"We operate in {regions_text} and interested in tenders from these regions."
            )

        # Certifications (if available)
        if profile.certifications:
            certs_text = ", ".join(profile.certifications)
            text_parts.append(f"Our certifications: {certs_text}.")

        # Budget range (if available)
        if profile.budget_min and profile.budget_max:
            currency = profile.budget_currency or 'ETB'
            text_parts.append(
                f"We handle projects ranging from {profile.budget_min:,.0f} to "
                f"{profile.budget_max:,.0f} {currency}."
            )

        # Company size context
        if profile.company_size:
            size_map = {
                'startup': 'startup company',
                'small': 'small business',
                'medium': 'medium-sized enterprise',
                'large': 'large corporation'
            }
            size_text = size_map.get(profile.company_size, profile.company_size)
            text_parts.append(f"We are a {size_text}.")

        # Experience
        if profile.years_in_operation:
            exp_map = {
                '<1': 'new company with emerging capabilities',
                '1-3': 'company with 1-3 years of experience',
                '3-5': 'company with 3-5 years of proven experience',
                '5-10': 'company with 5-10 years of industry experience',
                '10+': 'established company with over 10 years of experience'
            }
            exp_text = exp_map.get(profile.years_in_operation, '')
            if exp_text:
                text_parts.append(f"We are a {exp_text}.")

        # Combine all parts
        text = " ".join(text_parts).strip()

        if not text:
            logger.warning(f"Profile {profile.id} has no text for embedding")
            return [0.0] * cls.EMBEDDING_DIMENSIONS

        logger.info(f"Profile embedding text ({len(text)} chars): {text[:200]}...")

        # Generate embedding
        model = cls.get_model()
        embedding = model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        return embedding.tolist()

    @classmethod
    def batch_generate_embeddings(
        cls,
        texts: List[str],
        batch_size: int = 32
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.

        Args:
            texts: List of text strings
            batch_size: Number of texts to process at once

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        model = cls.get_model()
        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
            batch_size=batch_size
        )

        return [emb.tolist() for emb in embeddings]

    @classmethod
    def compute_similarity(
        cls,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score (0-1, higher is more similar)
        """
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Cosine similarity (already normalized, so just dot product)
        similarity = np.dot(vec1, vec2)

        return float(similarity)


# Create singleton instance
embedding_service = EmbeddingService()
