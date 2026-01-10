"""
Compare Regex vs LLM extraction accuracy on real tender data
"""
import json

# Load processed tenders
with open('output/processed_tenders.json', 'r') as f:
    data = json.load(f)

tenders = data['tenders']

# Analyze contact extraction accuracy
print("=" * 60)
print("CONTACT EXTRACTION ACCURACY ANALYSIS")
print("=" * 60)

email_correct = 0
email_total = 0
phone_correct = 0
phone_total = 0

for tender in tenders[:20]:  # Sample first 20
    extracted = tender.get('extracted', {})
    contact = extracted.get('contact', {})
    
    emails = contact.get('emails', [])
    phones = contact.get('phones', [])
    
    # Check email format (regex is deterministic, should be 100%)
    for email in emails:
        email_total += 1
        if '@' in email and '.' in email:
            email_correct += 1
    
    # Check phone format
    for phone in phones:
        phone_total += 1
        if phone.startswith(('+251', '0')) and len(phone) >= 10:
            phone_correct += 1

print(f"\nEmail extraction:")
print(f"  Total found: {email_total}")
print(f"  Valid format: {email_correct}")
print(f"  Accuracy: {(email_correct/email_total*100) if email_total > 0 else 0:.1f}%")

print(f"\nPhone extraction:")
print(f"  Total found: {phone_total}")
print(f"  Valid format: {phone_correct}")
print(f"  Accuracy: {(phone_correct/phone_total*100) if phone_total > 0 else 0:.1f}%")

# Analyze organization extraction issues
print("\n" + "=" * 60)
print("ORGANIZATION EXTRACTION ISSUES")
print("=" * 60)

org_issues = []
for idx, tender in enumerate(tenders[:20]):
    extracted = tender.get('extracted', {})
    org = extracted.get('organization', {})
    org_name = org.get('name', '')
    title = tender.get('original', {}).get('title', '')
    
    # Check for problematic extractions
    if org_name in ['Unconditional Bank', 'Not specified', 'Unknown', '']:
        org_issues.append({
            'index': idx,
            'extracted_org': org_name,
            'title': title[:80]
        })

print(f"\nProblematic org extractions: {len(org_issues)}/{20}")
for issue in org_issues[:5]:
    print(f"\n  [{issue['index']}] Extracted: '{issue['extracted_org']}'")
    print(f"      Title: {issue['title']}...")

