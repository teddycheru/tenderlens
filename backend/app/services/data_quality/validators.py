# backend/app/services/data_quality/validators.py
"""
Comprehensive validation rules for scraped tender data.
Uses Pydantic for type validation and custom business rules.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, date
import re
from pydantic import BaseModel, validator, Field, ValidationError as PydanticValidationError
from urllib.parse import urlparse


class TenderValidationRule(BaseModel):
    """
    Pydantic model for validating tender data.
    Enforces data types, required fields, and basic business rules.
    """

    # Required fields
    title: str = Field(..., min_length=10, max_length=500)
    description: Optional[str] = Field(None, max_length=10000)

    # Optional but validated fields
    deadline: Optional[date] = None
    published_date: Optional[date] = None
    category: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    source_url: Optional[str] = Field(None, max_length=2000)
    budget: Optional[float] = None
    budget_currency: Optional[str] = Field("ETB", max_length=10)

    @validator('title')
    def validate_title(cls, v):
        """Title must be meaningful and not just placeholder text."""
        if not v or len(v.strip()) < 10:
            raise ValueError("Title must be at least 10 characters")

        # Check for placeholder text
        placeholders = ["test", "dummy", "placeholder", "lorem ipsum", "n/a", "tbd"]
        if any(placeholder in v.lower() for placeholder in placeholders):
            raise ValueError("Title appears to be placeholder text")

        return v.strip()

    @validator('description')
    def validate_description(cls, v):
        """Description should be meaningful if provided."""
        if v and len(v.strip()) < 20:
            raise ValueError("Description too short (minimum 20 characters)")

        if v and len(v) > 10000:
            raise ValueError("Description exceeds maximum length (10000 characters)")

        return v.strip() if v else None

    @validator('deadline')
    def validate_deadline(cls, v):
        """Deadline must be in the future (with 1-day grace period)."""
        if v:
            min_deadline = date.today()
            if v < min_deadline:
                raise ValueError(f"Deadline must be on or after {min_deadline}")
        return v

    @validator('published_date')
    def validate_published_date(cls, v):
        """Published date should not be in the future."""
        if v and v > date.today():
            raise ValueError("Published date cannot be in the future")
        return v

    @validator('source_url')
    def validate_url(cls, v):
        """Validate URL format and protocol."""
        if not v:
            return None

        try:
            result = urlparse(v)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Invalid URL format")

            if result.scheme not in ['http', 'https']:
                raise ValueError("URL must use http or https protocol")

            return v.strip()
        except Exception as e:
            raise ValueError(f"Invalid URL: {str(e)}")

    @validator('budget')
    def validate_budget(cls, v):
        """Budget must be positive and within reasonable range."""
        if v is not None:
            if v <= 0:
                raise ValueError("Budget must be positive")

            if v > 1_000_000_000_000:  # 1 trillion max
                raise ValueError("Budget exceeds reasonable maximum (1 trillion)")

        return v

    class Config:
        extra = "allow"
        validate_assignment = True


class DataValidator:
    """
    Service for validating scraped tender data.
    Combines Pydantic validation with custom business rules.
    """

    def validate_tender(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate tender data against all rules.

        Returns:
            {
                "is_valid": bool,
                "errors": List[Dict],
                "warnings": List[Dict],
                "validated_data": Dict or None,
                "quality_score": float
            }
        """
        errors = []
        warnings = []

        try:
            # Step 1: Pydantic validation
            validated = TenderValidationRule(**raw_data)

            # Step 2: Additional business rules
            business_errors, business_warnings = self._apply_business_rules(
                raw_data, validated.dict()
            )
            errors.extend(business_errors)
            warnings.extend(business_warnings)

            # Step 3: Calculate quality score
            quality_score = self._calculate_quality_score(
                validated.dict(), warnings
            )

            return {
                "is_valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "validated_data": validated.dict() if len(errors) == 0 else None,
                "quality_score": quality_score
            }

        except PydanticValidationError as e:
            # Convert Pydantic validation errors to our format
            for error in e.errors():
                errors.append({
                    "type": "validation_error",
                    "field": ".".join(str(x) for x in error['loc']),
                    "message": error['msg'],
                    "severity": "error",
                    "raw_value": error.get('input')
                })

            return {
                "is_valid": False,
                "errors": errors,
                "warnings": warnings,
                "validated_data": None,
                "quality_score": 0.0
            }
        except Exception as e:
            errors.append({
                "type": "system_error",
                "field": None,
                "message": f"Unexpected validation error: {str(e)}",
                "severity": "critical"
            })

            return {
                "is_valid": False,
                "errors": errors,
                "warnings": warnings,
                "validated_data": None,
                "quality_score": 0.0
            }

    def _apply_business_rules(self, raw_data: Dict, validated_data: Dict) -> tuple:
        """
        Apply additional business-specific validation rules.
        """
        errors = []
        warnings = []

        # Rule 1: Deadline should be reasonable (at least 7 days from published date)
        if validated_data.get('deadline') and validated_data.get('published_date'):
            deadline = validated_data['deadline']
            published = validated_data['published_date']

            if isinstance(deadline, str):
                deadline = datetime.strptime(deadline, "%Y-%m-%d").date()
            if isinstance(published, str):
                published = datetime.strptime(published, "%Y-%m-%d").date()

            days_diff = (deadline - published).days

            if days_diff < 7:
                warnings.append({
                    "type": "business_rule",
                    "field": "deadline",
                    "message": f"Short deadline: only {days_diff} days from publication",
                    "severity": "warning"
                })

        # Rule 2: Warn if category not specified
        if not validated_data.get('category'):
            warnings.append({
                "type": "missing_data",
                "field": "category",
                "message": "Category not specified",
                "severity": "warning"
            })

        # Rule 3: Warn if no source URL
        if not validated_data.get('source_url'):
            warnings.append({
                "type": "missing_data",
                "field": "source_url",
                "message": "No source URL provided",
                "severity": "warning"
            })

        return errors, warnings

    def _calculate_quality_score(self, validated_data: Dict, warnings: List[Dict]) -> float:
        """
        Calculate data quality score (0-100).
        """
        score = 100.0

        # Deduct for warnings
        score -= len(warnings) * 5

        # Deduct for missing optional fields
        important_fields = ['description', 'category', 'region', 'budget', 'deadline']
        missing_count = sum(1 for field in important_fields if not validated_data.get(field))
        score -= missing_count * 8

        # Bonus for rich description
        if validated_data.get('description') and len(validated_data['description']) > 200:
            score += 5

        # Bonus for having budget
        if validated_data.get('budget'):
            score += 5

        return max(0.0, min(100.0, score))


# Singleton instance
data_validator = DataValidator()
