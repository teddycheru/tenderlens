"""
Recommendation Service - Find and score personalized tender recommendations.

Uses vector similarity search with pgvector and multi-factor scoring.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.tender import Tender
from app.models.company_profile import CompanyTenderProfile
from app.models.user_interaction import UserInteraction
from app.models.user import User
from typing import List, Tuple, Dict, Optional
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Service for generating personalized tender recommendations.

    Combines:
    - Vector similarity (semantic matching)
    - Sector matching
    - Region matching
    - Keyword overlap
    - Budget fit
    - Urgency bonus
    """

    @staticmethod
    def get_recommendations(
        db: Session,
        profile: CompanyTenderProfile,
        limit: int = 20,
        min_score: Optional[float] = None,
        days_ahead: int = 7
    ) -> List[Tuple[Tender, float, Dict]]:
        """
        Get personalized tender recommendations for a company profile.

        Args:
            db: Database session
            profile: Company tender profile
            limit: Maximum number of recommendations
            min_score: Minimum match score (0-100), defaults to profile threshold
            days_ahead: Only show tenders with at least this many days until deadline

        Returns:
            List of (tender, score, reasons) tuples
        """
        min_score = min_score or float(profile.min_match_threshold)
        # Convert to date for comparison with tender deadlines (which are date objects)
        today = datetime.now(timezone.utc).date()
        max_deadline = today + timedelta(days=days_ahead)

        # Check if profile has embedding
        if profile.profile_embedding is None:
            logger.warning(f"Profile {profile.id} has no embedding")
            return []

        # Get previously dismissed tenders (join with User to get company_id)
        dismissed_ids_query = db.query(UserInteraction.tender_id).join(
            User, UserInteraction.user_id == User.id
        ).filter(
            User.company_id == profile.company_id,
            UserInteraction.interaction_type == 'dismiss'
        )
        dismissed_ids = [row[0] for row in dismissed_ids_query.all()]

        # Calculate similarity score
        similarity_score = (1 - func.cosine_distance(
            Tender.content_embedding,
            profile.profile_embedding
        )).label('similarity_score')

        # Vector similarity search with filters
        query = db.query(
            Tender,
            similarity_score
        ).filter(
            # Only active tenders
            Tender.recommendation_status == 'active',

            # Deadline must be in future and within the specified days_ahead window
            Tender.deadline >= today,
            Tender.deadline <= max_deadline,

            # Must have embedding
            Tender.content_embedding.isnot(None),

            # Exclude dismissed tenders
            ~Tender.id.in_(dismissed_ids) if dismissed_ids else True
        )

        # Apply sector filter (must match at least one active sector)
        if profile.active_sectors:
            query = query.filter(
                Tender.category.in_(profile.active_sectors)
            )

        # Apply region filter (if specified)
        if profile.preferred_regions:
            query = query.filter(
                Tender.region.in_(profile.preferred_regions)
            )

        # Get more results than needed for filtering, ordered by similarity
        results = query.order_by(similarity_score.desc()).limit(limit * 3).all()

        # Score, filter, and rank
        recommendations = []
        for tender, similarity in results:
            score, reasons = RecommendationService.calculate_score_with_reasons(
                profile, tender, similarity
            )

            if score >= min_score:
                recommendations.append((tender, score, reasons))

        # Sort by score and limit
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:limit]

    @staticmethod
    def calculate_score_with_reasons(
        profile: CompanyTenderProfile,
        tender: Tender,
        similarity: float
    ) -> Tuple[float, Dict]:
        """
        Calculate match score and return reasons for the match.

        Args:
            profile: Company profile
            tender: Tender
            similarity: Vector similarity score (0-1)

        Returns:
            Tuple of (final_score, reasons_dict)
        """
        # Updated weights to prioritize semantic similarity with improved embeddings
        # Semantic matching is now much better with rich profile text
        weights = profile.scoring_weights or {
            "semantic": 25,         # Increased from 5 to 25 (rich embeddings)
            "active_sectors": 25,   # Reduced from 30 to 25 (still important)
            "keywords": 20,         # Reduced from 25 to 20
            "sub_sectors": 15,      # Reduced from 20 to 15
            "region": 8,            # Reduced from 10 to 8
            "budget": 4,            # Reduced from 5 to 4
            "certifications": 3     # Reduced from 5 to 3
        }

        score = 0
        reasons = []

        # Semantic similarity (base score)
        # Now weighted at 25% with improved profile embeddings
        semantic_weight = weights.get('semantic', 25)
        semantic_score = similarity * 100 * (semantic_weight / 100)
        score += semantic_score

        # Lower threshold from 0.7 to 0.5 since we have richer embeddings
        # Add reason if similarity is meaningful (>50%)
        if similarity > 0.5:
            reasons.append({
                "type": "semantic_match",
                "message": f"Strong semantic match ({similarity:.0%})",
                "weight": semantic_score
            })
        elif similarity > 0.3:
            # Add reason for moderate matches too (30-50%)
            reasons.append({
                "type": "semantic_match",
                "message": f"Moderate semantic match ({similarity:.0%})",
                "weight": semantic_score
            })

        # Sector match (most important)
        if tender.category and tender.category in profile.active_sectors:
            sector_weight = weights.get('active_sectors', 30)
            score += sector_weight
            reasons.append({
                "type": "sector_match",
                "message": f"Matches your sector: {tender.category}",
                "weight": sector_weight
            })

        # Sub-sector match
        if profile.sub_sectors and tender.category in profile.sub_sectors:
            subsector_weight = weights.get('sub_sectors', 20)
            score += subsector_weight
            reasons.append({
                "type": "subsector_match",
                "message": f"Matches your specialization",
                "weight": subsector_weight
            })

        # Region match
        if tender.region and tender.region in profile.preferred_regions:
            region_weight = weights.get('region', 10)
            score += region_weight
            reasons.append({
                "type": "region_match",
                "message": f"In your preferred region: {tender.region}",
                "weight": region_weight
            })

        # Keyword overlap (if tender has tags/keywords)
        if hasattr(tender, 'tags') and tender.tags and profile.keywords:
            tender_keywords = set(tender.tags or [])
            profile_keywords = set(profile.keywords)
            overlap = tender_keywords & profile_keywords

            if overlap:
                overlap_ratio = len(overlap) / len(profile_keywords) if profile_keywords else 0
                keyword_score = overlap_ratio * weights.get('keywords', 25)
                score += keyword_score
                reasons.append({
                    "type": "keyword_match",
                    "message": f"Matches keywords: {', '.join(list(overlap)[:3])}",
                    "weight": keyword_score
                })

        # Budget fit
        if profile.budget_min and profile.budget_max and tender.budget:
            if profile.budget_min <= tender.budget <= profile.budget_max:
                budget_weight = weights.get('budget', 5)
                score += budget_weight
                reasons.append({
                    "type": "budget_match",
                    "message": f"Within your budget range",
                    "weight": budget_weight
                })

        # Urgency bonus (deadline coming soon)
        if tender.deadline:
            days_until_deadline = (tender.deadline - datetime.now(timezone.utc).date()).days
            if days_until_deadline <= 14:
                urgency_bonus = 5
                score += urgency_bonus
                reasons.append({
                    "type": "urgency",
                    "message": f"Deadline in {days_until_deadline} days",
                    "weight": urgency_bonus
                })

        # Cap score at 100
        final_score = min(score, 100)

        return final_score, {
            "score": final_score,
            "reasons": reasons,
            "similarity": similarity
        }

    @staticmethod
    def get_similar_tenders(
        db: Session,
        tender_id: str,
        limit: int = 5
    ) -> List[Tuple[Tender, float]]:
        """
        Get tenders similar to a specific tender.
        Useful for "You might also like" features.

        Args:
            db: Database session
            tender_id: ID of the reference tender
            limit: Maximum number of similar tenders

        Returns:
            List of (tender, similarity) tuples
        """
        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        if not tender or not tender.content_embedding:
            return []

        min_deadline = datetime.now(timezone.utc) + timedelta(days=7)

        results = db.query(
            Tender,
            (1 - func.cosine_distance(
                Tender.content_embedding,
                tender.content_embedding
            )).label('similarity_score')
        ).filter(
            Tender.id != tender_id,  # Exclude the original tender
            Tender.recommendation_status == 'active',
            Tender.deadline >= min_deadline,
            Tender.content_embedding.isnot(None)
        ).order_by('similarity_score DESC').limit(limit).all()

        return results


# Create singleton instance
recommendation_service = RecommendationService()
