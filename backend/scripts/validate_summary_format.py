#!/usr/bin/env python3
"""
Validate tender summaries against user-defined evaluation metrics.

Metrics:
1. Paragraph Organization:
   - Paragraph 1: Company name, company description, tender title
   - Paragraph 2: Description of the tender
   - Paragraph 3: Key requirements
   - Paragraph 4+: Other details (contact, submission, deadline, etc.)

2. Content Coverage:
   - Must extract all necessary information from Description_clean column
   - Should include all critical tender information
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.database import SessionLocal
from app.models.tender import Tender
from app.services.ai.gliner_service import GlinerService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SummaryValidator:
    """Validate summary format against evaluation metrics."""

    REQUIRED_FIELDS = {
        "organization": "🏢 Organization/Company Name",
        "scope": "📦 Tender Scope/Description",
        "requirements": "✓ Key Requirements",
        "deadline": "📅 Submission Deadline",
        "location": "📍 Location",
        "submission_method": "📤 How to Submit"
    }

    def __init__(self):
        self.gliner = GlinerService()
        self.db = SessionLocal()

    def validate_summary_format(self, tender: Tender) -> dict:
        """
        Validate if summary adheres to evaluation metrics.

        Returns:
            Dictionary with validation results
        """
        result = {
            "tender_id": tender.id,
            "title": tender.title,
            "summary": tender.ai_summary,
            "description_clean": tender.description_clean[:500] + "..." if tender.description_clean else None,
            "validation_results": {},
            "paragraph_structure": {},
            "missing_fields": [],
            "score": 0,
            "max_score": 100,
        }

        if not tender.ai_summary:
            result["status"] = "❌ NO SUMMARY"
            return result

        summary = tender.ai_summary

        # ========== CHECK 1: PARAGRAPH ORGANIZATION ==========
        paragraphs = [p.strip() for p in summary.split("\n\n") if p.strip()]

        result["paragraph_structure"]["total_paragraphs"] = len(paragraphs)
        result["paragraph_structure"]["paragraphs"] = paragraphs

        # Expected structure: At least 3-4 logical sections
        structure_check = {
            "has_overview": any("OVERVIEW" in p.upper() or "📋" in p for p in paragraphs),
            "has_quick_facts": any("QUICK FACTS" in p.upper() or "⚡" in p for p in paragraphs),
            "has_key_details": any("KEY DETAILS" in p.upper() or "📦" in p or "REQUIREMENTS" in p.upper() for p in paragraphs),
            "has_deadline": any("deadline" in p.lower() or "📅" in p for p in paragraphs),
            "has_submission": any("submit" in p.lower() or "📤" in p for p in paragraphs),
        }

        result["paragraph_structure"]["structure_check"] = structure_check

        # ========== CHECK 2: REQUIRED FIELD EXTRACTION ==========
        extracted_entities = self.gliner._extract_key_entities(tender.description_clean or "")

        for field, label in self.REQUIRED_FIELDS.items():
            present = field in extracted_entities and bool(extracted_entities[field])
            in_summary = field.replace("_", " ").lower() in summary.lower() or extracted_entities.get(field, "").lower() in summary.lower()

            result["validation_results"][label] = {
                "extracted": present,
                "in_summary": in_summary,
                "value": extracted_entities.get(field, "NOT FOUND")
            }

            if not present:
                result["missing_fields"].append(label)

        # ========== CHECK 3: CONTENT COVERAGE ==========
        description_clean = tender.description_clean or ""
        key_coverage_metrics = {
            "mentions_scope": len(extracted_entities.get("scope", "")) > 0,
            "mentions_requirements": len(extracted_entities.get("requirements", "")) > 0,
            "mentions_deadline": len(extracted_entities.get("deadline", "")) > 0,
            "mentions_organization": len(extracted_entities.get("organization", "")) > 0,
            "has_substantial_length": len(summary) > 150,
            "has_multiple_sections": len(paragraphs) >= 3,
        }

        result["validation_results"]["content_coverage"] = key_coverage_metrics

        # ========== SCORING ==========
        score = 0
        max_score = 100

        # 20 points: Structure
        structure_score = sum(structure_check.values()) * 4
        score += structure_score

        # 40 points: Field extraction (10 per critical field)
        critical_fields = 4  # organization, scope, requirements, deadline
        fields_found = sum(1 for f in ["organization", "scope", "requirements", "deadline"]
                          if extracted_entities.get(f))
        field_score = (fields_found / critical_fields) * 40
        score += field_score

        # 20 points: Content coverage
        coverage_score = sum(key_coverage_metrics.values()) * (20 / len(key_coverage_metrics))
        score += coverage_score

        # 20 points: Length and detail
        if len(summary) > 300:
            length_score = 20
        elif len(summary) > 200:
            length_score = 15
        elif len(summary) > 100:
            length_score = 10
        else:
            length_score = 5
        score += length_score

        result["score"] = int(score)
        result["max_score"] = max_score
        result["status"] = self._get_status(score, max_score)

        return result

    @staticmethod
    def _get_status(score: int, max_score: int) -> str:
        """Determine status based on score."""
        percentage = (score / max_score) * 100
        if percentage >= 85:
            return "✅ EXCELLENT"
        elif percentage >= 70:
            return "✓ GOOD"
        elif percentage >= 50:
            return "⚠️ FAIR"
        else:
            return "❌ POOR"

    def validate_batch(self, limit: int = 10) -> list:
        """Validate a batch of tenders."""
        tenders = self.db.query(Tender).filter(
            Tender.ai_summary.isnot(None)
        ).limit(limit).all()

        results = []
        for tender in tenders:
            result = self.validate_summary_format(tender)
            results.append(result)

        return results

    def print_validation_report(self, results: list):
        """Print a formatted validation report."""
        print("\n" + "="*80)
        print("TENDER SUMMARY VALIDATION REPORT")
        print("="*80)

        for result in results:
            print(f"\n{'─'*80}")
            print(f"📄 Tender: {result['title']}")
            print(f"ID: {result['tender_id']}")
            print(f"Status: {result['status']} ({result['score']}/{result['max_score']} points)")

            # Paragraph Structure
            print(f"\n📊 PARAGRAPH STRUCTURE:")
            print(f"  Total sections: {result['paragraph_structure']['total_paragraphs']}")

            structure = result['paragraph_structure']['structure_check']
            print(f"  ✓ Has Overview: {structure.get('has_overview', False)}")
            print(f"  ✓ Has Quick Facts: {structure.get('has_quick_facts', False)}")
            print(f"  ✓ Has Key Details: {structure.get('has_key_details', False)}")
            print(f"  ✓ Has Deadline: {structure.get('has_deadline', False)}")
            print(f"  ✓ Has Submission: {structure.get('has_submission', False)}")

            # Field Extraction
            print(f"\n📋 FIELD EXTRACTION:")
            for label, details in result['validation_results'].items():
                if label == "content_coverage":
                    continue
                if isinstance(details, dict) and 'extracted' in details:
                    status = "✓" if details['extracted'] else "✗"
                    print(f"  {status} {label}: {details['value']}")

            # Content Coverage
            if result['validation_results'].get('content_coverage'):
                print(f"\n📍 CONTENT COVERAGE:")
                coverage = result['validation_results']['content_coverage']
                for metric, present in coverage.items():
                    status = "✓" if present else "✗"
                    print(f"  {status} {metric.replace('_', ' ').title()}")

            # Missing Fields
            if result['missing_fields']:
                print(f"\n⚠️  MISSING FIELDS:")
                for field in result['missing_fields']:
                    print(f"  - {field}")
            else:
                print(f"\n✅ All required fields present!")

            # Summary Preview
            print(f"\n📝 SUMMARY PREVIEW:")
            summary = result['summary']
            lines = summary.split('\n')[:10]
            for line in lines:
                print(f"  {line}")
            if len(summary.split('\n')) > 10:
                print(f"  ... ({len(summary.split(chr(10)))} total lines)")

        # Summary Statistics
        print(f"\n{'='*80}")
        print("SUMMARY STATISTICS")
        print(f"{'='*80}")

        total = len(results)
        excellent = sum(1 for r in results if "EXCELLENT" in r['status'])
        good = sum(1 for r in results if "GOOD" in r['status'])
        fair = sum(1 for r in results if "FAIR" in r['status'])
        poor = sum(1 for r in results if "POOR" in r['status'])

        print(f"\nTotal Tenders Validated: {total}")
        print(f"✅ Excellent: {excellent} ({excellent/total*100:.1f}%)")
        print(f"✓  Good: {good} ({good/total*100:.1f}%)")
        print(f"⚠️  Fair: {fair} ({fair/total*100:.1f}%)")
        print(f"❌ Poor: {poor} ({poor/total*100:.1f}%)")

        avg_score = sum(r['score'] for r in results) / total
        print(f"\nAverage Score: {avg_score:.1f}/{results[0]['max_score']}")

        # Recommendations
        print(f"\n{'='*80}")
        print("RECOMMENDATIONS")
        print(f"{'='*80}")

        if excellent + good >= total * 0.8:
            print("✅ Summary format is EXCELLENT and ready for production!")
        else:
            print("⚠️  Summary format needs improvements:")

            avg_missing_count = len([r for results in results for r in results.get('missing_fields', [])])
            if avg_missing_count > 0:
                print(f"  1. Missing fields in {avg_missing_count} results")

            low_structure = sum(1 for r in results if r['paragraph_structure']['total_paragraphs'] < 3)
            if low_structure > 0:
                print(f"  2. {low_structure} summaries lack proper section structure (need 3+ sections)")

            print("  3. Review gliner_service.py to enhance entity extraction")
            print("  4. Ensure Description_clean field contains all necessary information")


if __name__ == "__main__":
    validator = SummaryValidator()

    # Validate batch of 10 summaries
    print("🔍 Validating tender summaries against evaluation metrics...")
    results = validator.validate_batch(limit=10)

    # Print detailed report
    validator.print_validation_report(results)

    # Export JSON for further analysis
    import json
    with open("summary_validation_results.json", "w") as f:
        # Convert to JSON-serializable format
        json_results = []
        for r in results:
            r_copy = r.copy()
            r_copy['summary'] = r_copy['summary'][:200] + "..." if len(r_copy['summary']) > 200 else r_copy['summary']
            json_results.append(r_copy)
        json.dump(json_results, f, indent=2, default=str)

    print("\n📊 Detailed results saved to: summary_validation_results.json")
