# JSON to Database Column Mapping

## Complete Data Flow: processed_tenders.json → Database

This document shows exactly how data from the processed_tenders.json file maps to the tender database table columns.

---

## 1. ORIGINAL TENDER DATA MAPPING

### JSON Source: `tender["original"]`

```json
"original": {
  "url": "https://tender.2merkato.com/tenders/...",
  "title": "The Automotive Manufacturing Company...",
  "category": "Facilities Management",
  "status": "Open",
  "region": "Addis Ababa",
  "closing_date_raw": "April 24,2025 at 10:00 A.M.",
  "published_on": "Apr 13, 2025",
  "language": "english"
}
```

### Database Columns:

| JSON Key | DB Column | DB Type | Frontend Use |
|----------|-----------|---------|--------------|
| `url` | `source_url` | String(unique) | Link to original tender |
| `title` | `title` | String(required) | Tender title display |
| `category` | `category` | String(indexed) | Filter by category |
| `status` | `status` | Enum(PUBLISHED/CLOSED/etc) | Filter by status |
| `region` | `region` | String(indexed) | Filter by region/location |
| `published_on` | `published_date` | Date | Show publication date |
| `language` | `language` | String | Language detection |
| `description` | `description` | Text(required) | Raw HTML content |

---

## 2. EXTRACTED DATA MAPPING

### JSON Source: `tender["extracted"]`

This is stored as **one large JSON object** in the `extracted_data` column.

```json
"extracted": {
  "financial": {...},
  "contact": {...},
  "dates": {...},
  "requirements": [...],
  "specifications": [...],
  "organization": {...},
  "addresses": {...},
  "language_flag": "english",
  "tender_type": "bid_invitation",
  "is_award_notification": false
}
```

### Database Column:

| JSON Key | DB Column | DB Type | Frontend Use |
|----------|-----------|---------|--------------|
| `extracted` (entire) | `extracted_data` | JSON | All structured data access |

### Detailed Extraction Map (inside extracted_data JSON):

#### Financial Information
```json
extracted_data.financial = {
  "bid_security_amount": 50000.0,
  "bid_security_currency": "ETB",
  "document_fee": 300.0,
  "fee_currency": "ETB",
  "other_amounts": []
}
```

**Frontend can fetch:**
```sql
SELECT
  (extracted_data->'financial'->>'bid_security_amount')::numeric as bid_security,
  (extracted_data->'financial'->>'bid_security_currency') as currency,
  (extracted_data->'financial'->>'document_fee')::numeric as fee
FROM tenders
WHERE id = 'tender_id'
```

#### Contact Information
```json
extracted_data.contact = {
  "emails": ["contact@example.com", "...@ivecogroup.com"],
  "phones": ["+251911234567"]
}
```

**Frontend can fetch:**
```sql
SELECT
  extracted_data->'contact'->'emails' as contact_emails,
  extracted_data->'contact'->'phones' as contact_phones
FROM tenders
WHERE id = 'tender_id'
```

#### Dates
```json
extracted_data.dates = {
  "closing_date": "2025-04-24T10:00:00",
  "published_date": "2025-04-13T00:00:00",
  "closing_date_original": "April 24,2025 at 10:00 A.M."
}
```

**Frontend can also use:** `deadline` column (parsed date)
**Frontend can fetch parsed dates from:**
- `deadline` column (Date type)
- `published_date` column (Date type)

#### Requirements
```json
extracted_data.requirements = [
  "Bid Documents: Interested bidders may obtain...",
  "Eligibility Requirements: Bidders must include...",
  "Submission of Bids: Both technical and financial...",
  "Bid Security: A bid security of Birr 50,000..."
]
```

**Frontend can fetch:**
```sql
SELECT jsonb_array_length(extracted_data->'requirements') as requirement_count,
       extracted_data->'requirements' as all_requirements
FROM tenders
WHERE id = 'tender_id'
```

#### Specifications (Tables)
```json
extracted_data.specifications = [
  {"Description": "Load Balancing System", "Quantity": "1", "Unit": "EA"},
  {"Description": "Support Services", "Quantity": "3", "Unit": "Years"}
]
```

**Frontend can fetch:**
```sql
SELECT extracted_data->'specifications' as specifications_table
FROM tenders
WHERE id = 'tender_id'
```

#### Organization
```json
extracted_data.organization = {
  "name": "Ministry of Health",
  "type": ""
}
```

**Frontend can fetch:**
```sql
SELECT (extracted_data->'organization'->>'name') as issuing_organization
FROM tenders
WHERE id = 'tender_id'
```

#### Addresses
```json
extracted_data.addresses = {
  "po_boxes": [],
  "regions": ["Addis Ababa"]
}
```

#### Metadata
```json
extracted_data.language_flag = "english",
extracted_data.tender_type = "bid_invitation",
extracted_data.is_award_notification = false
```

---

## 3. GENERATED CONTENT MAPPING

### JSON Source: `tender["generated"]`

```json
"generated": {
  "summary": "2-3 sentence executive summary...",
  "clean_description": "Well-formatted description with markdown...",
  "highlights": "- Key highlight 1\n- Key highlight 2\n..."
}
```

### Database Columns:

| JSON Key | DB Column | DB Type | Frontend Use |
|----------|-----------|---------|--------------|
| `summary` | `ai_summary` | Text | Quick preview/summary display |
| `clean_description` | `clean_description` | Text | Main tender description (formatted) |
| `highlights` | `highlights` | Text | Key points/features display |

**Frontend display example:**
```python
# Fetch all needed data in one query
tender = db.query(Tender).filter(Tender.id == tender_id).first()

# Display summary
print(tender.ai_summary)  # "Oromia Bank is seeking a supplier..."

# Display clean description (formatted)
print(tender.clean_description)  # "**Bid Extension Notification**\n\n..."

# Display highlights
print(tender.highlights)  # "- Bid Closing: April 22, 2025\n- Extension applies to OT/05/2024-25\n..."

# Display extracted data
financial = tender.extracted_data['financial']
print(f"Bid Security: {financial['bid_security_amount']} {financial['bid_security_currency']}")

contact = tender.extracted_data['contact']
print(f"Contact Emails: {', '.join(contact['emails'])}")
```

---

## 4. METADATA MAPPING

### JSON Source: `tender["original"]` + Processing

| JSON Key | DB Column | DB Type | Frontend Use |
|----------|-----------|---------|--------------|
| `id` | `id` | UUID | Unique record identifier |
| `index` | (not stored) | - | Not needed in DB |
| Processing timestamp | `content_generated_at` | DateTime | Show when content was generated |
| Processing errors | `content_generation_errors` | JSON | Show error messages if any |

---

## 5. AUTO-GENERATED COLUMNS (From Importer)

These are created by the JSON importer when processing:

| Column | Value | Type | Frontend Use |
|--------|-------|------|--------------|
| `external_id` | SHA256(url) | String | Deduplication |
| `content_hash` | MD5(description) | String | Duplicate detection |
| `source` | "content-generator" | String | Data source tracking |
| `status` | PUBLISHED | Enum | Show tender status |
| `created_at` | Now | DateTime | Record creation timestamp |
| `updated_at` | Now | DateTime | Last modification |

---

## COMPLETE FRONTEND DATA STRUCTURE

Here's what the frontend gets when fetching a tender:

```typescript
interface Tender {
  // Basic Info
  id: string;
  title: string;
  description: string; // raw HTML

  // Metadata
  category: string;
  region: string;
  language: string;
  source: string;
  source_url: string;
  status: "published" | "closed" | "draft" | "cancelled";

  // Dates
  published_date: Date;
  deadline: Date;

  // Generated Content (FROM JSON)
  clean_description: string; // Formatted, ready to display
  highlights: string; // Bullet points
  ai_summary: string; // Quick summary

  // Structured Data (FROM JSON)
  extracted_data: {
    financial: {
      bid_security_amount: number;
      bid_security_currency: string;
      document_fee: number;
      fee_currency: string;
      other_amounts: number[];
    };
    contact: {
      emails: string[];
      phones: string[];
    };
    dates: {
      closing_date: string; // ISO format
      published_date: string;
      closing_date_original: string;
    };
    requirements: string[];
    specifications: Array<Record<string, string>>;
    organization: {
      name: string;
      type: string;
    };
    addresses: {
      po_boxes: string[];
      regions: string[];
    };
    language_flag: string;
    tender_type: string;
    is_award_notification: boolean;
  };

  // Processing Info
  content_generated_at: DateTime;
  content_generation_errors?: any[];
}
```

---

## SQL QUERY EXAMPLES FOR FRONTEND

### Get all tender info in one query:
```sql
SELECT
  id, title, clean_description, highlights, ai_summary,
  category, region, deadline, published_date,
  extracted_data,
  source_url, status
FROM tenders
WHERE id = $1
```

### Get all fields for list view:
```sql
SELECT
  id, title, ai_summary, category, region, deadline,
  (extracted_data->'financial'->>'bid_security_amount')::numeric as bid_security,
  (extracted_data->'contact'->'emails'->>0) as first_email,
  source_url
FROM tenders
WHERE status = 'published'
ORDER BY deadline DESC
```

### Filter by extracted data:
```sql
SELECT *
FROM tenders
WHERE
  (extracted_data->'organization'->>'name' ILIKE '%Ministry%')
  AND (extracted_data->'financial'->>'bid_security_amount')::numeric > 100000
  AND region = 'Addis Ababa'
```

---

## DATABASE COLUMN CHECKLIST

✓ All financial information available (bid_security_amount, document_fee, currency)
✓ All contact information available (emails, phones)
✓ All dates available (formatted and original)
✓ All requirements in list format
✓ All specifications in table format
✓ Organization information
✓ Geographic information
✓ Language detection
✓ Tender type classification
✓ LLM-generated summaries
✓ LLM-generated clean descriptions
✓ LLM-generated highlights
✓ Processing timestamps
✓ Original tender URL
✓ Status tracking

**Everything needed for frontend display is available!**

