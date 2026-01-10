"""
Quick test script to verify the pipeline works before processing all tenders
"""

import sys
import os

# Local imports (modules are in this directory)
from csv_parser import TenderCSVParser
from extractor import TenderExtractor
from content_generator import ContentGenerator


def test_csv_parser():
    """Test CSV parsing"""
    print("\n" + "="*60)
    print("TEST 1: CSV Parser")
    print("="*60)

    csv_path = '/home/tewodros-cheru/Documents/Pros/content-generator/output_merged_bottom_200.csv'

    if not os.path.exists(csv_path):
        print(f"✗ CSV file not found: {csv_path}")
        return False

    try:
        parser = TenderCSVParser(csv_path)
        tenders = parser.load_csv()

        if not tenders:
            print("✗ No tenders loaded")
            return False

        stats = parser.validate_tenders()

        # Test batch retrieval
        batch = parser.get_batch(0, batch_size=5)
        print(f"\n✓ Successfully loaded {len(tenders)} tenders")
        print(f"✓ Retrieved batch of {len(batch)} tenders")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_extractor():
    """Test information extraction"""
    print("\n" + "="*60)
    print("TEST 2: Information Extractor")
    print("="*60)

    csv_path = '/home/tewodros-cheru/Documents/Pros/content-generator/output_merged_bottom_200.csv'

    try:
        parser = TenderCSVParser(csv_path)
        tenders = parser.load_csv()

        if not tenders or len(tenders) == 0:
            print("✗ No tenders to test")
            return False

        extractor = TenderExtractor()

        # Test on first tender
        tender = tenders[0]
        print(f"\nTesting on tender: {tender.get('Title', 'N/A')[:80]}")

        extracted = extractor.extract_all(tender)

        print(f"\n✓ Successfully extracted data:")
        print(f"  - Financial: {extracted['financial']}")
        print(f"  - Contact emails: {len(extracted['contact']['emails'])} found")
        print(f"  - Contact phones: {len(extracted['contact']['phones'])} found")
        print(f"  - Dates: {extracted['dates']}")
        print(f"  - Requirements: {len(extracted['requirements'])} found")
        print(f"  - Specifications: {len(extracted['specifications'])} found")
        print(f"  - Organization: {extracted['organization']['name']}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_content_generator():
    """Test content generation with LLM"""
    print("\n" + "="*60)
    print("TEST 3: Content Generator (Ollama)")
    print("="*60)

    try:
        generator = ContentGenerator(model='llama3.2:3b', check_running=True)

        test_html = """
        <p><strong>Ministry of Health</strong> invites qualified bidders for medical equipment supply.</p>
        <p>Bid Security: <strong>Birr 50,000.00</strong></p>
        <p>Document Fee: <strong>Birr 300.00</strong></p>
        <ul>
            <li>Trade License required</li>
            <li>Tax clearance certificate</li>
            <li>Proof of previous experience</li>
        </ul>
        """

        test_title = "Ministry of Health - Medical Equipment Supply Tender"

        print(f"\nTesting content generation...")
        print(f"Input title: {test_title}")

        print(f"\n1. Generating summary...")
        summary = generator.generate_summary(test_html, test_title)
        if summary:
            print(f"✓ Summary generated ({len(summary)} chars):\n  {summary[:150]}...")
        else:
            print("⚠ Summary generation returned None")

        print(f"\n2. Generating clean description...")
        clean = generator.generate_clean_description(test_html)
        if clean:
            print(f"✓ Clean description generated ({len(clean)} chars):\n  {clean[:150]}...")
        else:
            print("⚠ Clean description generation returned None")

        print(f"\n3. Extracting highlights...")
        test_extracted = {
            'financial': {'bid_security_amount': 50000},
            'organization': {'name': 'Ministry of Health'},
            'region': 'Addis Ababa',
            'requirements': ['Trade License', 'Tax Certificate', 'Experience Proof']
        }
        highlights = generator.extract_key_highlights(test_extracted, test_title)
        if highlights:
            print(f"✓ Highlights extracted ({len(highlights)} chars):\n  {highlights[:150]}...")
        else:
            print("⚠ Highlights extraction returned None")

        print(f"\n✓ Content generation working!")
        return True

    except Exception as e:
        print(f"⚠ Error during content generation: {e}")
        print(f"  Note: This is OK if Ollama is not running yet")
        return False


def test_full_pipeline():
    """Test the full processing pipeline on a small sample"""
    print("\n" + "="*60)
    print("TEST 4: Full Pipeline (First 5 Tenders)")
    print("="*60)

    from process_tenders import TenderProcessor

    csv_path = '/home/tewodros-cheru/Documents/Pros/content-generator/output_merged_bottom_200.csv'

    try:
        processor = TenderProcessor(
            csv_path=csv_path,
            output_dir='./test_output',
            batch_size=5,
            use_llm=False,  # Test without LLM first
            model='llama3.2:3b'
        )

        tenders = processor.parser.load_csv()[:5]  # Get first 5
        batch_results = processor._process_batch(tenders, 0)

        print(f"\n✓ Successfully processed {len(batch_results)} tenders")

        for result in batch_results:
            status = "✓" if result['processing_status'] == 'success' else "✗"
            print(f"  {status} {result['id']}: {result['original']['title'][:50]}...")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("TENDER PROCESSING PIPELINE - TEST SUITE")
    print("="*60)

    tests = [
        ("CSV Parser", test_csv_parser),
        ("Information Extractor", test_extractor),
        ("Content Generator", test_content_generator),
        ("Full Pipeline", test_full_pipeline),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results[test_name] = False

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed! Ready for full processing.")
        print("\nNext step: Run the full processor:")
        print("  python process_tenders.py /path/to/output_merged_bottom_200.csv")
    else:
        print("\n⚠ Some tests failed. Check output above.")

    print("="*60 + "\n")


if __name__ == '__main__':
    main()
