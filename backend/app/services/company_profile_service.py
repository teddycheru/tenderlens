"""
Company Profile Service

Business logic for company tender profile management and onboarding.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List, Dict
from uuid import UUID
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.models.company_profile import CompanyTenderProfile
from app.models.company import Company
from app.schemas.company_profile import (
    CompanyProfileCreate,
    CompanyProfileUpdate,
    ProfileOptions
)


class CompanyProfileService:
    """Service for managing company tender profiles"""

    # Static data for profile options
    SECTORS = [
        "IT and Infrastructure",
        "Construction and Engineering",
        "Healthcare and Pharmaceuticals",
        "Agriculture and Food Processing",
        "Manufacturing",
        "Education and Training",
        "Financial Services",
        "Transportation and Logistics",
        "Energy and Utilities",
        "Telecommunications",
        "Consulting and Professional Services",
        "Hospitality and Tourism",
        "Retail and Distribution",
        "Media and Entertainment",
        "Real Estate and Property",
        "Environmental Services",
        "Mining and Natural Resources",
        "Security Services",
        "Legal Services",
        "Other Services"
    ]

    REGIONS = [
        "Addis Ababa",
        "Oromia",
        "Amhara",
        "Tigray",
        "Somali",
        "Afar",
        "SNNPR",
        "Sidama",
        "Benishangul-Gumuz",
        "Gambela",
        "Harari",
        "Dire Dawa"
    ]

    CERTIFICATIONS = [
        "ISO 9001 (Quality Management)",
        "ISO 14001 (Environmental Management)",
        "ISO 27001 (Information Security)",
        "ISO 45001 (Occupational Health & Safety)",
        "VAT Registered",
        "Trade License",
        "Professional Engineer License",
        "Construction License",
        "Tax Compliance Certificate",
        "Business Registration Certificate",
        "Industry-Specific Certification"
    ]

    KEYWORD_SUGGESTIONS = {
        "IT and Infrastructure": [
            # Core IT Services
            "software development", "software", "web development", "mobile apps", "application development",
            "cloud computing", "cloud services", "SaaS", "IT infrastructure",
            # Networking & Security
            "cybersecurity", "network", "network infrastructure", "firewall", "security systems",
            "data protection", "backup solutions", "disaster recovery",
            # Database & Systems
            "database", "database management", "SQL", "data analytics", "big data",
            "system integration", "enterprise systems", "ERP", "CRM",
            # Support & Operations
            "IT support", "technical support", "help desk", "IT consulting", "system administration",
            "DevOps", "automation", "server", "hardware", "computers",
            # Emerging Tech
            "blockchain", "AI", "ML", "machine learning", "artificial intelligence",
            # Equipment
            "ICT equipment", "computers", "servers", "networking equipment", "procurement"
        ],
        "Construction and Engineering": [
            "building construction", "construction", "road construction", "infrastructure",
            "civil engineering", "electrical engineering", "electrical", "power systems",
            "mechanical engineering", "structural design", "structural engineering",
            "project management", "construction management", "site supervision",
            "HVAC systems", "heating", "ventilation", "air conditioning",
            "plumbing", "water systems", "sanitation",
            "architecture", "architectural design", "building design",
            "surveying", "land surveying", "geospatial",
            "construction materials", "cement", "steel", "building materials",
            "renovation", "maintenance", "repair works"
        ],
        "Healthcare and Pharmaceuticals": [
            "medical equipment", "medical devices", "diagnostic equipment",
            "pharmaceuticals", "medicines", "drugs", "pharmaceutical supply",
            "healthcare services", "medical services", "hospital services",
            "laboratory", "laboratory services", "lab equipment", "testing",
            "medical supplies", "surgical supplies", "PPE", "medical consumables",
            "hospital management", "healthcare management",
            "telemedicine", "digital health", "health IT",
            "clinical trials", "research", "medical research",
            "pharmaceutical distribution", "medical logistics",
            "nursing", "patient care", "medical training"
        ],
        "Agriculture and Food Processing": [
            "crop production", "agriculture", "farming", "agronomy",
            "livestock", "animal husbandry", "veterinary",
            "irrigation", "water management", "drip irrigation",
            "agricultural equipment", "farm machinery", "tractors", "harvesters",
            "food processing", "food production", "food manufacturing",
            "packaging", "food packaging", "preservation",
            "cold chain", "refrigeration", "storage",
            "organic farming", "sustainable agriculture",
            "agricultural consulting", "agribusiness", "farm management",
            "fertilizers", "soil management", "nutrients",
            "pesticides", "crop protection", "pest control",
            "food safety", "quality control", "food standards"
        ],
        "Manufacturing": [
            "production", "manufacturing", "industrial production",
            "assembly", "fabrication", "machining",
            "quality control", "quality assurance", "inspection",
            "supply chain", "procurement", "logistics",
            "industrial equipment", "machinery", "production equipment",
            "automation", "robotics", "automated systems",
            "metal fabrication", "metalworking", "welding",
            "plastic manufacturing", "injection molding", "extrusion",
            "packaging materials", "packaging production",
            "lean manufacturing", "process improvement", "efficiency",
            "raw materials", "material sourcing"
        ],
        "Education and Training": [
            "training", "education", "skill development", "capacity building",
            "teaching", "instruction", "curriculum development",
            "vocational training", "technical training", "professional development",
            "e-learning", "online training", "digital education",
            "educational materials", "textbooks", "learning materials",
            "training programs", "workshops", "seminars",
            "educational technology", "learning management systems",
            "educational consulting", "training needs assessment",
            "certification programs", "accreditation"
        ],
        "Financial Services": [
            "accounting", "bookkeeping", "financial reporting",
            "audit", "auditing", "internal audit", "external audit",
            "tax", "taxation", "tax consulting", "tax compliance",
            "financial consulting", "financial advisory",
            "banking services", "insurance", "investment",
            "payroll", "payroll services", "HR services",
            "financial software", "accounting software", "ERP systems",
            "financial analysis", "budgeting", "financial planning",
            "compliance", "regulatory compliance", "financial controls"
        ],
        "Telecommunications": [
            "telecommunications", "telecom", "communication systems",
            "mobile networks", "cellular", "5G", "4G", "LTE",
            "fiber optics", "optical fiber", "cable installation",
            "network infrastructure", "telecom equipment",
            "VoIP", "voice services", "call centers",
            "data services", "internet services", "broadband",
            "network maintenance", "network support",
            "telecom consulting", "network design"
        ],
        "Energy and Utilities": [
            "energy", "power", "electricity", "electrical systems",
            "renewable energy", "solar", "solar power", "wind power",
            "power generation", "generators", "power systems",
            "energy efficiency", "energy management", "energy audit",
            "utilities", "water supply", "water treatment",
            "power distribution", "transmission", "substations",
            "electrical engineering", "power engineering",
            "energy consulting", "energy solutions"
        ],
        "Transportation and Logistics": [
            "transportation", "logistics", "supply chain",
            "freight", "cargo", "shipping", "delivery",
            "fleet management", "vehicle management",
            "warehousing", "storage", "distribution",
            "transport services", "courier services",
            "logistics consulting", "supply chain management",
            "customs", "import", "export", "freight forwarding"
        ],
        "Consulting and Professional Services": [
            "consulting", "business consulting", "management consulting",
            "strategy", "strategic planning", "business development",
            "project management", "program management",
            "organizational development", "change management",
            "research", "market research", "feasibility studies",
            "advisory services", "expert services", "professional services",
            "monitoring and evaluation", "M&E", "impact assessment"
        ],
        "Environmental Services": [
            "environmental", "environmental management", "environmental consulting",
            "waste management", "waste disposal", "recycling",
            "environmental assessment", "EIA", "environmental impact",
            "pollution control", "air quality", "water quality",
            "sustainability", "sustainable development", "green solutions",
            "environmental monitoring", "environmental compliance",
            "conservation", "natural resource management"
        ],
        "Security Services": [
            "security", "security services", "security systems",
            "physical security", "guarding", "surveillance",
            "access control", "CCTV", "security cameras",
            "security consulting", "risk assessment", "security audit",
            "alarm systems", "fire safety", "safety systems",
            "security personnel", "security training"
        ]
    }

    @staticmethod
    def create_profile(
        db: Session,
        company_id: UUID,
        profile_data: CompanyProfileCreate
    ) -> CompanyTenderProfile:
        """
        Create a new company tender profile.

        Args:
            db: Database session
            company_id: UUID of the company
            profile_data: Profile data from onboarding

        Returns:
            Created CompanyTenderProfile

        Raises:
            HTTPException: If company not found or profile already exists
        """
        # Verify company exists
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )

        # Check if profile already exists
        existing_profile = db.query(CompanyTenderProfile).filter(
            CompanyTenderProfile.company_id == company_id
        ).first()

        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Company profile already exists. Use update endpoint."
            )

        # Create new profile
        profile = CompanyTenderProfile(
            company_id=company_id,
            **profile_data.model_dump()
        )

        # Determine profile completion
        profile.profile_completed = bool(
            profile.company_size and
            profile.years_in_operation and
            profile.certifications
        )

        # Set onboarding step
        profile.onboarding_step = 2 if profile.profile_completed else 1

        db.add(profile)
        db.commit()
        db.refresh(profile)

        return profile

    @staticmethod
    def get_profile_by_company(
        db: Session,
        company_id: UUID
    ) -> Optional[CompanyTenderProfile]:
        """Get company profile by company ID"""
        return db.query(CompanyTenderProfile).filter(
            CompanyTenderProfile.company_id == company_id
        ).first()

    @staticmethod
    def get_profile_by_id(
        db: Session,
        profile_id: UUID
    ) -> Optional[CompanyTenderProfile]:
        """Get company profile by profile ID"""
        return db.query(CompanyTenderProfile).filter(
            CompanyTenderProfile.id == profile_id
        ).first()

    @staticmethod
    def update_profile(
        db: Session,
        company_id: UUID,
        profile_update: CompanyProfileUpdate
    ) -> CompanyTenderProfile:
        """
        Update an existing company profile.

        Args:
            db: Database session
            company_id: UUID of the company
            profile_update: Update data

        Returns:
            Updated CompanyTenderProfile

        Raises:
            HTTPException: If profile not found
        """
        profile = db.query(CompanyTenderProfile).filter(
            CompanyTenderProfile.company_id == company_id
        ).first()

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company profile not found"
            )

        # Update fields
        update_data = profile_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)

        # Update profile completion status
        profile.profile_completed = bool(
            profile.company_size and
            profile.years_in_operation and
            profile.certifications
        )

        # Update onboarding step
        if profile.profile_completed and profile.onboarding_step < 2:
            profile.onboarding_step = 2

        db.commit()
        db.refresh(profile)

        return profile

    @staticmethod
    def delete_profile(
        db: Session,
        company_id: UUID
    ) -> bool:
        """
        Delete a company profile (soft delete by marking inactive).

        Args:
            db: Database session
            company_id: UUID of the company

        Returns:
            True if deleted

        Raises:
            HTTPException: If profile not found
        """
        profile = db.query(CompanyTenderProfile).filter(
            CompanyTenderProfile.company_id == company_id
        ).first()

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company profile not found"
            )

        # For now, hard delete. Later implement soft delete with is_active field
        db.delete(profile)
        db.commit()

        return True

    @staticmethod
    def get_profile_options() -> ProfileOptions:
        """
        Get available options for profile dropdowns.

        Returns:
            ProfileOptions with all available options
        """
        return ProfileOptions(
            sectors=CompanyProfileService.SECTORS,
            regions=CompanyProfileService.REGIONS,
            certifications=CompanyProfileService.CERTIFICATIONS,
            company_sizes=['startup', 'small', 'medium', 'large'],
            years_options=['<1', '1-3', '3-5', '5-10', '10+'],
            keyword_suggestions=CompanyProfileService.KEYWORD_SUGGESTIONS
        )

    @staticmethod
    def get_keyword_suggestions(sector: str) -> List[str]:
        """Get keyword suggestions for a specific sector"""
        return CompanyProfileService.KEYWORD_SUGGESTIONS.get(sector, [])

    @staticmethod
    def get_profiles_by_sector(
        db: Session,
        sector: str,
        limit: int = 100
    ) -> List[CompanyTenderProfile]:
        """Get all profiles in a specific sector"""
        return db.query(CompanyTenderProfile).filter(
            CompanyTenderProfile.active_sectors.contains([sector])
        ).limit(limit).all()

    @staticmethod
    def get_profiles_by_region(
        db: Session,
        region: str,
        limit: int = 100
    ) -> List[CompanyTenderProfile]:
        """Get all profiles interested in a specific region"""
        return db.query(CompanyTenderProfile).filter(
            CompanyTenderProfile.preferred_regions.contains([region])
        ).limit(limit).all()

    @staticmethod
    def search_profiles_by_keyword(
        db: Session,
        keyword: str,
        limit: int = 100
    ) -> List[CompanyTenderProfile]:
        """Search profiles by keyword"""
        return db.query(CompanyTenderProfile).filter(
            func.lower(keyword).in_(
                func.lower(func.unnest(CompanyTenderProfile.keywords))
            )
        ).limit(limit).all()

    @staticmethod
    def get_incomplete_profiles(
        db: Session,
        limit: int = 100
    ) -> List[CompanyTenderProfile]:
        """Get profiles that are incomplete (for follow-up prompts)"""
        return db.query(CompanyTenderProfile).filter(
            CompanyTenderProfile.profile_completed == False
        ).order_by(CompanyTenderProfile.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_profile_stats(db: Session, company_id: UUID) -> Dict:
        """Get statistics about a company profile"""
        profile = db.query(CompanyTenderProfile).filter(
            CompanyTenderProfile.company_id == company_id
        ).first()

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company profile not found"
            )

        return {
            "completion_percentage": profile.completion_percentage,
            "is_tier1_complete": profile.is_tier1_complete,
            "is_tier2_complete": profile.is_tier2_complete,
            "profile_completed": profile.profile_completed,
            "onboarding_step": profile.onboarding_step,
            "interaction_count": profile.interaction_count,
            "active_sectors_count": len(profile.active_sectors) if profile.active_sectors else 0,
            "sub_sectors_count": len(profile.sub_sectors) if profile.sub_sectors else 0,
            "keywords_count": len(profile.keywords) if profile.keywords else 0,
            "certifications_count": len(profile.certifications) if profile.certifications else 0,
            "has_budget_range": bool(profile.budget_min and profile.budget_max),
            "days_since_creation": (datetime.now(timezone.utc) - profile.created_at).days if profile.created_at else 0,
        }
