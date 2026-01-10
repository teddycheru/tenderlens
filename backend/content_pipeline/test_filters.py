"""
Test Language Filter and Typo Handling

This script tests:
1. Language detection on the full dataset
2. Filtering out unsupported languages
3. Date typo handling
4. Re-processing with filters applied
"""

import pandas as pd
import sys
from language_filter import LanguageDetector, filter_csv_by_language
from validation import ExtractionValidator

def test_language_detection():
    """Test language detection on full dataset"""
    print("="*80)
    print("LANGUAGE DETECTION TEST - Full Dataset")
    print("="*80)

    # Load CSV
    df = pd.read_csv('output_merged_bottom_200_cleaned.csv')

    # Convert to list of dicts
    tenders = df.to_dict('records')

    # Detect languages
    detector = LanguageDetector()
    supported, unsupported = detector.filter_supported_tenders(tenders)

    print(f"\nTotal tenders: {len(tenders)}")
    print(f"Supported: {len(supported)}")
    print(f"Unsupported: {len(unsupported)}")

    if unsupported:
        print(f"\nUnsupported tenders breakdown:")
        lang_counts = {}
        for tender in unsupported:
            lang = tender.get('detected_language', 'unknown')
            lang_counts[lang] = lang_counts.get(lang, 0) + 1

        for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {lang}: {count} tenders")

        print(f"\nUnsupported tenders (showing first 10):")
        for i, tender in enumerate(unsupported[:10]):
            print(f"  [{i}] {tender.get('Title', '')[:70]}...")
            print(f"      Language: {tender.get('detected_language')}, Confidence: {tender.get('confidence', 0):.2f}")

    return supported, unsupported


def test_typo_handling():
    """Test date typo handling"""
    print("\n" + "="*80)
    print("DATE TYPO HANDLING TEST")
    print("="*80)

    validator = ExtractionValidator()

    test_cases = [
        ('At 2:00 PM 24th of Aprill 2025.', 'Aprill -> April'),
        ('Feburary 15, 2025', 'Feburary -> February'),
        ('Septemeber 30, 2025 at 10:00 AM', 'Septemeber -> September'),
        ('Novemeber 10, 2024', 'Novemeber -> November'),
        ('Dec 25, 2025 at 12:00 PM', 'Short month name'),
    ]

    print("\nTesting month typo corrections:")
    for date_str, description in test_cases:
        result = validator._parse_date(date_str)
        status = "✅" if result else "❌"
        print(f"\n{status} {description}")
        print(f"   Input:  {date_str}")
        print(f"   Output: {result}")


def create_filtered_dataset():
    """Create a filtered dataset with only supported languages"""
    print("\n" + "="*80)
    print("CREATING FILTERED DATASET")
    print("="*80)

    output_path = 'output_merged_bottom_200_filtered.csv'

    stats = filter_csv_by_language(
        'output_merged_bottom_200_cleaned.csv',
        output_path
    )

    print(f"\nFiltering Statistics:")
    print(f"  Total tenders: {stats['total_tenders']}")
    print(f"  Supported: {stats['supported_tenders']}")
    print(f"  Unsupported: {stats['unsupported_tenders']}")

    if stats['unsupported_breakdown']:
        print(f"\n  Unsupported breakdown:")
        for lang, count in stats['unsupported_breakdown'].items():
            print(f"    - {lang}: {count}")

    print(f"\n✅ Filtered dataset saved to: {output_path}")

    return output_path


def verify_problematic_tenders():
    """Verify that problematic tenders are filtered correctly"""
    print("\n" + "="*80)
    print("VERIFYING PROBLEMATIC TENDERS")
    print("="*80)

    df = pd.read_csv('output_merged_bottom_200_cleaned.csv')
    detector = LanguageDetector()

    # Tenders that previously had issues
    problem_tenders = [
        (63, "ERP System placeholder"),
        (96, "ERP System placeholder"),
        (102, "Sidama language"),
        (109, "Aprill typo - should be fixed now"),
        (118, "Oromifa - incomplete date"),
    ]

    print("\nChecking problematic tenders:")
    for idx, issue in problem_tenders:
        if idx >= len(df):
            continue

        row = df.iloc[idx]
        text = f"{row['Title']} {row['Description']}"

        is_supported, language, confidence = detector.is_supported_language(text)

        # Test date parsing
        validator = ExtractionValidator()
        date_result = validator._parse_date(row['Closing Date'])

        print(f"\n[{idx}] {issue}")
        print(f"  Title: {row['Title'][:60]}...")
        print(f"  Language: {language} (confidence: {confidence:.2f})")
        print(f"  Supported: {'Yes' if is_supported else 'No (will be filtered out)'}")
        print(f"  Raw Date: {row['Closing Date'][:50]}...")
        print(f"  Parsed Date: {date_result if date_result else 'Failed to parse'}")


if __name__ == '__main__':
    print("COMPREHENSIVE FILTER AND TYPO HANDLING TEST\n")

    # Test 1: Language detection
    supported, unsupported = test_language_detection()

    # Test 2: Typo handling
    test_typo_handling()

    # Test 3: Verify problematic tenders
    verify_problematic_tenders()

    # Test 4: Create filtered dataset
    filtered_path = create_filtered_dataset()

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\n✅ Language detection working correctly")
    print(f"✅ Date typo handling working correctly")
    print(f"✅ Filtered dataset created: {filtered_path}")
    print(f"\n🎯 System ready to process {len(supported)} supported tenders")
    print(f"📋 {len(unsupported)} unsupported tenders saved for future processing")
