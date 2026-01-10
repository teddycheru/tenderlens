"""
Category-specific templates for tender summaries.

Provides structured summary templates based on tender type/category
to ensure consistent, useful information presentation.
"""

from typing import Dict, List, Optional
from enum import Enum


class TenderCategory(Enum):
    """Tender category classifications."""
    GOODS = "Goods and Supplies"
    SERVICES = "Services"
    CONSULTANCY = "Consultancy"
    TRAINING = "Training and Education"
    CONSTRUCTION = "Construction and Infrastructure"
    HEALTHCARE = "Health and Nutrition"
    IT = "IT and Infrastructure"
    TRANSPORTATION = "Transportation"
    OTHER = "Other"


class SummaryTemplate:
    """Template-based summary builder for different tender types."""

    # Keywords to identify tender categories
    CATEGORY_KEYWORDS = {
        TenderCategory.GOODS: [
            "procurement", "supply", "purchase", "goods", "materials", "equipment",
            "provision of", "delivery of", "stock", "inventory"
        ],
        TenderCategory.SERVICES: [
            "service", "services", "maintenance", "repair", "cleaning", "operation",
            "support", "management", "facility", "operational"
        ],
        TenderCategory.CONSULTANCY: [
            "consultancy", "consultant", "consulting", "advisory", "feasibility study",
            "design", "supervision", "study", "technical assistance", "expertise"
        ],
        TenderCategory.TRAINING: [
            "training", "education", "skill development", "capacity building", "workshop",
            "course", "development program", "mentoring", "coaching"
        ],
        TenderCategory.CONSTRUCTION: [
            "construction", "infrastructure", "building", "renovation", "road", "bridge",
            "project", "civil works", "engineering", "installation"
        ],
        TenderCategory.HEALTHCARE: [
            "medical", "health", "medicine", "pharmaceutical", "healthcare", "hospital",
            "clinic", "treatment", "vaccine", "health service"
        ],
        TenderCategory.IT: [
            "software", "system", "technology", "IT", "computer", "digital", "network",
            "server", "database", "security", "implementation"
        ],
        TenderCategory.TRANSPORTATION: [
            "vehicle", "transport", "logistics", "shipping", "delivery", "freight",
            "courier", "equipment rental"
        ],
    }

    @staticmethod
    def identify_category(text: str, title: str = "") -> TenderCategory:
        """
        Identify tender category based on text content.

        Args:
            text: Tender document text
            title: Tender title

        Returns:
            Identified TenderCategory
        """
        combined_text = (title + " " + text).lower()

        # Score each category
        scores = {}
        for category, keywords in SummaryTemplate.CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            scores[category] = score

        # Return category with highest score
        best_category = max(scores, key=scores.get)
        return best_category if scores[best_category] > 0 else TenderCategory.OTHER

    @staticmethod
    def build_summary_from_entities(
        category: TenderCategory,
        entities: Dict[str, str],
        important_sentences: List[str]
    ) -> str:
        """
        Build a summary using category-specific template.

        Args:
            category: Tender category
            entities: Extracted entities dictionary
            important_sentences: List of important sentences from document

        Returns:
            Formatted summary
        """
        summary_parts = []

        # Start with important sentences for context
        if important_sentences:
            summary_parts.extend(important_sentences[:2])

        # Add category-specific information
        if category == TenderCategory.GOODS:
            summary_parts.extend(
                SummaryTemplate._build_goods_summary(entities)
            )
        elif category == TenderCategory.SERVICES:
            summary_parts.extend(
                SummaryTemplate._build_services_summary(entities)
            )
        elif category == TenderCategory.CONSULTANCY:
            summary_parts.extend(
                SummaryTemplate._build_consultancy_summary(entities)
            )
        elif category == TenderCategory.TRAINING:
            summary_parts.extend(
                SummaryTemplate._build_training_summary(entities)
            )
        elif category == TenderCategory.CONSTRUCTION:
            summary_parts.extend(
                SummaryTemplate._build_construction_summary(entities)
            )
        elif category == TenderCategory.HEALTHCARE:
            summary_parts.extend(
                SummaryTemplate._build_healthcare_summary(entities)
            )
        elif category == TenderCategory.IT:
            summary_parts.extend(
                SummaryTemplate._build_it_summary(entities)
            )
        elif category == TenderCategory.TRANSPORTATION:
            summary_parts.extend(
                SummaryTemplate._build_transportation_summary(entities)
            )
        else:
            summary_parts.extend(
                SummaryTemplate._build_generic_summary(entities)
            )

        # Combine and clean up
        summary = " ".join(filter(None, summary_parts))
        summary = summary.strip()

        if summary and not summary.endswith(('.', '!', '?')):
            summary += '.'

        return summary

    @staticmethod
    def _build_goods_summary(entities: Dict[str, str]) -> List[str]:
        """Build summary for goods procurement."""
        parts = []

        scope = entities.get("scope", "").strip()
        if scope:
            parts.append(f"Procurement of: {scope}")

        organization = entities.get("organization", "").strip()
        if organization:
            parts.append(f"Issuer: {organization}")

        requirements = entities.get("requirements", "").strip()
        if requirements:
            parts.append(f"Requirements: {requirements}")

        deadline = entities.get("deadline", "").strip()
        if deadline:
            parts.append(f"Deadline: {deadline}")

        bid_security = entities.get("bid_security", "").strip()
        if bid_security:
            parts.append(f"Bid Security: {bid_security}")

        submission = entities.get("submission_method", "").strip()
        if submission:
            parts.append(f"Submission: {submission}")

        return parts

    @staticmethod
    def _build_services_summary(entities: Dict[str, str]) -> List[str]:
        """Build summary for service procurement."""
        parts = []

        scope = entities.get("scope", "").strip()
        if scope:
            parts.append(f"Service Required: {scope}")

        duration = entities.get("duration", "").strip()
        if duration:
            parts.append(f"Duration: {duration}")

        location = entities.get("location", "").strip()
        if location:
            parts.append(f"Location: {location}")

        requirements = entities.get("requirements", "").strip()
        if requirements:
            parts.append(f"Qualifications Needed: {requirements}")

        deadline = entities.get("deadline", "").strip()
        if deadline:
            parts.append(f"Deadline: {deadline}")

        submission = entities.get("submission_method", "").strip()
        if submission:
            parts.append(f"Submit: {submission}")

        return parts

    @staticmethod
    def _build_consultancy_summary(entities: Dict[str, str]) -> List[str]:
        """Build summary for consultancy services."""
        parts = []

        scope = entities.get("scope", "").strip()
        if scope:
            parts.append(f"Consultancy: {scope}")

        duration = entities.get("duration", "").strip()
        if duration:
            parts.append(f"Duration: {duration}")

        requirements = entities.get("requirements", "").strip()
        if requirements:
            parts.append(f"Expertise Required: {requirements}")

        deadline = entities.get("deadline", "").strip()
        if deadline:
            parts.append(f"Deadline: {deadline}")

        contact = entities.get("contact", "").strip()
        if contact:
            parts.append(f"Contact: {contact}")

        return parts

    @staticmethod
    def _build_training_summary(entities: Dict[str, str]) -> List[str]:
        """Build summary for training programs."""
        parts = []

        scope = entities.get("scope", "").strip()
        if scope:
            parts.append(f"Training: {scope}")

        duration = entities.get("duration", "").strip()
        if duration:
            parts.append(f"Duration: {duration}")

        location = entities.get("location", "").strip()
        if location:
            parts.append(f"Location: {location}")

        requirements = entities.get("requirements", "").strip()
        if requirements:
            parts.append(f"Qualifications: {requirements}")

        deadline = entities.get("deadline", "").strip()
        if deadline:
            parts.append(f"Application Deadline: {deadline}")

        return parts

    @staticmethod
    def _build_construction_summary(entities: Dict[str, str]) -> List[str]:
        """Build summary for construction/infrastructure projects."""
        parts = []

        scope = entities.get("scope", "").strip()
        if scope:
            parts.append(f"Project: {scope}")

        location = entities.get("location", "").strip()
        if location:
            parts.append(f"Location: {location}")

        duration = entities.get("duration", "").strip()
        if duration:
            parts.append(f"Expected Duration: {duration}")

        requirements = entities.get("requirements", "").strip()
        if requirements:
            parts.append(f"Requirements: {requirements}")

        deadline = entities.get("deadline", "").strip()
        if deadline:
            parts.append(f"Bid Deadline: {deadline}")

        bid_security = entities.get("bid_security", "").strip()
        if bid_security:
            parts.append(f"Bid Security: {bid_security}")

        return parts

    @staticmethod
    def _build_healthcare_summary(entities: Dict[str, str]) -> List[str]:
        """Build summary for healthcare procurement."""
        parts = []

        scope = entities.get("scope", "").strip()
        if scope:
            parts.append(f"Healthcare Need: {scope}")

        organization = entities.get("organization", "").strip()
        if organization:
            parts.append(f"Institution: {organization}")

        requirements = entities.get("requirements", "").strip()
        if requirements:
            parts.append(f"Specifications: {requirements}")

        deadline = entities.get("deadline", "").strip()
        if deadline:
            parts.append(f"Deadline: {deadline}")

        submission = entities.get("submission_method", "").strip()
        if submission:
            parts.append(f"Submission Method: {submission}")

        return parts

    @staticmethod
    def _build_it_summary(entities: Dict[str, str]) -> List[str]:
        """Build summary for IT/technology procurement."""
        parts = []

        scope = entities.get("scope", "").strip()
        if scope:
            parts.append(f"IT Solution: {scope}")

        requirements = entities.get("requirements", "").strip()
        if requirements:
            parts.append(f"Technical Requirements: {requirements}")

        duration = entities.get("duration", "").strip()
        if duration:
            parts.append(f"Implementation Period: {duration}")

        deadline = entities.get("deadline", "").strip()
        if deadline:
            parts.append(f"Proposal Deadline: {deadline}")

        contact = entities.get("contact", "").strip()
        if contact:
            parts.append(f"Technical Contact: {contact}")

        return parts

    @staticmethod
    def _build_transportation_summary(entities: Dict[str, str]) -> List[str]:
        """Build summary for transportation/logistics."""
        parts = []

        scope = entities.get("scope", "").strip()
        if scope:
            parts.append(f"Service: {scope}")

        duration = entities.get("duration", "").strip()
        if duration:
            parts.append(f"Contract Period: {duration}")

        location = entities.get("location", "").strip()
        if location:
            parts.append(f"Coverage Area: {location}")

        requirements = entities.get("requirements", "").strip()
        if requirements:
            parts.append(f"Requirements: {requirements}")

        deadline = entities.get("deadline", "").strip()
        if deadline:
            parts.append(f"Deadline: {deadline}")

        return parts

    @staticmethod
    def _build_generic_summary(entities: Dict[str, str]) -> List[str]:
        """Build summary for unclassified tenders."""
        parts = []

        scope = entities.get("scope", "").strip()
        if scope:
            parts.append(f"Scope: {scope}")

        organization = entities.get("organization", "").strip()
        if organization:
            parts.append(f"Issuer: {organization}")

        requirements = entities.get("requirements", "").strip()
        if requirements:
            parts.append(f"Requirements: {requirements}")

        deadline = entities.get("deadline", "").strip()
        if deadline:
            parts.append(f"Deadline: {deadline}")

        location = entities.get("location", "").strip()
        if location:
            parts.append(f"Location: {location}")

        submission = entities.get("submission_method", "").strip()
        if submission:
            parts.append(f"Submission: {submission}")

        return parts
