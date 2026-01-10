"""
Test Hybrid Extractor on Real Tender Data
"""

import sys
import json
from hybrid_extractor import HybridExtractor

# Test tenders with known issues
test_tenders = [
    {
        'name': 'Test 1: Organization extraction error (Unconditional Bank)',
        'tender': {
            'Title': 'Action for Development (AFD), a local organization, invites interested bidders for the Supply of Veterinary Equipment',
            'Description': '''
            <p><strong>Invitation for Bid</strong></p>
            <p>Bid Reference Number: AFDA-09/2025</p>
            <p>Eligible bidders are expected to submit copies of renewed trade license.</p>
            <p>The bid document can be purchased against payment of non-refundable fee of Birr 300.00.</p>
            <p>All bids must be accompanied by a bid bond amounting 1% of the total bid amount in the form of C.P.O. or Unconditional Bank Guarantee.</p>
            <p>All bids must be submitted at or before 2:00 P.M local time on 28th April, 2025.</p>
            <p>Contact: Tel 011 662 5976/0939655371</p>
            ''',
            'Closing Date': 'At 2:00 P.M local time on 28th April, 2025.',
            'Published On': 'Apr 13, 2025',
            'Region': 'Addis Ababa',
            'Category': 'Corporate Services'
        },
        'expected_org': 'Action for Development (AFD)'
    },
    {
        'name': 'Test 2: Relative date parsing error',
        'tender': {
            'Title': 'RaDO (Rehabilitation and Development Organization) Invites Eligible Bidders for the Procurement of Different Item',
            'Description': '''
            <p>RaDO invites eligible bidders</p>
            <p>Deadline for submission: 7 consecutive days starting from the date of the Announcement</p>
            <p>Contact: info@rado.org</p>
            ''',
            'Closing Date': '7 consecutive days starting from the date of the Announcement',
            'Published On': 'Apr 13, 2025',
            'Region': 'Addis Ababa',
            'Category': 'Uncategorized'
        },
        'expected_closing': '2025-04-20'
    },
    {
        'name': 'Test 3: Not specified organization',
        'tender': {
            'Title': 'The Hailemariam & Roman Foundation has received a financing from Agence Française de Dévelopement (\"AFD\"), intends to procure consultancy service',
            'Description': '''
            <p>Consultancy service to undertake Agrarian Analysis Study (AAS)</p>
            <p>Deadline: No later than April 29/2025</p>
            <p>Contact: c.scetp@haileromanfoundation.org</p>
            ''',
            'Closing Date': 'No later than April 29/2025',
            'Published On': 'Apr 12, 2025',
            'Region': 'Addis Ababa',
            'Category': 'Consultancy'
        },
        'expected_org': 'The Hailemariam & Roman Foundation'
    }
]

def test_without_llm():
    """Test with regex only (no LLM)"""
    print("=" * 70)
    print("TEST MODE: Regex Only (No LLM)")
    print("=" * 70)

    extractor = HybridExtractor(use_llm=False)

    for test_case in test_tenders:
        print(f"\n{test_case['name']}")
        print("-" * 70)

        result = extractor.extract_all(test_case['tender'])

        org_name = result.get('organization', {}).get('name', '')
        closing_date = result.get('dates', {}).get('closing_date', '')
        extraction_method = result.get('extraction_method', '')
        confidence = result.get('extraction_confidence', {})

        print(f"Organization: {org_name}")
        if 'expected_org' in test_case:
            status = "✓" if test_case['expected_org'] in org_name else "✗"
            print(f"Expected: {test_case['expected_org']} {status}")

        print(f"Closing Date: {closing_date}")
        if 'expected_closing' in test_case:
            status = "✓" if closing_date and test_case['expected_closing'] in closing_date else "✗"
            print(f"Expected: {test_case['expected_closing']} {status}")

        print(f"Extraction Method: {extraction_method}")
        print(f"Confidence: Overall={confidence.get('overall', 0):.2f}, "
              f"Org={confidence.get('organization', 0):.2f}, "
              f"Dates={confidence.get('dates', 0):.2f}")
        print(f"Needs Review: {result.get('needs_manual_review', False)}")


def test_with_llm():
    """Test with LLM (hybrid mode)"""
    print("\n" + "=" * 70)
    print("TEST MODE: Hybrid (Regex + LLM)")
    print("=" * 70)

    try:
        extractor = HybridExtractor(model="llama3.2:3b", use_llm=True)

        for test_case in test_tenders[:1]:  # Test just first one with LLM
            print(f"\n{test_case['name']}")
            print("-" * 70)

            result = extractor.extract_all(test_case['tender'])

            org_name = result.get('organization', {}).get('name', '')
            closing_date = result.get('dates', {}).get('closing_date', '')
            extraction_method = result.get('extraction_method', '')
            confidence = result.get('extraction_confidence', {})

            print(f"Organization: {org_name}")
            if 'expected_org' in test_case:
                status = "✓" if test_case['expected_org'] in org_name else "✗"
                print(f"Expected: {test_case['expected_org']} {status}")

            print(f"Financial: {result.get('financial', {})}")
            print(f"Contact: {result.get('contact', {})}")
            print(f"Requirements (count): {len(result.get('requirements', []))}")

            print(f"\nExtraction Method: {extraction_method}")
            print(f"Confidence: Overall={confidence.get('overall', 0):.2f}, "
                  f"Org={confidence.get('organization', 0):.2f}, "
                  f"Financial={confidence.get('financial', 0):.2f}, "
                  f"Dates={confidence.get('dates', 0):.2f}")
            print(f"Needs Review: {result.get('needs_manual_review', False)}")

    except Exception as e:
        print(f"⚠ LLM test skipped (Ollama may not be running): {e}")


if __name__ == "__main__":
    # Test without LLM first (faster)
    test_without_llm()

    # Test with LLM if available
    if '--skip-llm' not in sys.argv:
        test_with_llm()
    else:
        print("\n⚠ Skipped LLM tests (--skip-llm flag)")

    print("\n" + "=" * 70)
    print("Tests Complete!")
    print("=" * 70)
