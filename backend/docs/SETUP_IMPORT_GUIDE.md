# Setup & Import Guide: Content Pipeline Integration

## Overview

You now have everything needed to:
1. Drop the old tenders table
2. Create new schema with content generation fields
3. Import 190+ pre-processed tenders with generated content

## What You'll Get

After setup, your database will have:
- **199 tender records**
- **190 with complete generated content** (summaries, clean descriptions, highlights)
- **Structured extracted data** (financial, contact, dates, requirements, specs, organization, addresses)
- **All fields indexed** for fast filtering and searching

## Prerequisites

Before running the setup, ensure:

1. **PostgreSQL is running** (or Docker container)
   ```bash
   # If using Docker
   docker-compose up -d
   ```

2. **Python dependencies installed**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment variables configured** (.env file)
   ```
   DATABASE_URL=postgresql://user:password@localhost/tender_lens
   ```

## Setup Methods

### Method 1: Automated Setup (Recommended)

Run the complete setup script:

```bash
cd backend
python setup_content_pipeline.py
```

**This will:**
1. ✓ Ask for confirmation before dropping tables
2. ✓ Drop the existing tenders table
3. ✓ Run Alembic migrations
4. ✓ Import all 190+ tenders
5. ✓ Verify the import and show sample data

### Method 2: Manual Setup (Step-by-Step)

If you prefer to do it manually:

#### Step 1: Drop Existing Table

```bash
cd backend
python << 'EOF'
from sqlalchemy import text
from app.database import engine

print("Dropping tenders table...")
with engine.connect() as connection:
    connection.execute(text("DROP TABLE IF EXISTS tenders CASCADE"))
    connection.commit()
print("✅ Done")
EOF
```

#### Step 2: Run Migrations

```bash
cd backend
alembic upgrade head
```

This creates the tenders table with all new fields:
- `clean_description`
- `highlights`
- `extracted_data`
- `content_generated_at`
- `content_generation_errors`

#### Step 3: Import the Data

```bash
cd backend
python << 'EOF'
from app.services.pipeline.json_content_importer import JSONContentImporter
from app.database import SessionLocal
from pathlib import Path

db = SessionLocal()
importer = JSONContentImporter(db)
stats = importer.import_from_json(Path('content_pipeline/output/processed_tenders.json'))

print("Import Results:")
print(f"  Total: {stats['total']}")
print(f"  Updated: {stats['updated']}")
print(f"  Skipped: {stats['skipped']}")
print(f"  Errors: {stats['errors']}")

db.close()
EOF
```

#### Step 4: Verify

```bash
cd backend
python << 'EOF'
from app.database import SessionLocal
from app.models.tender import Tender

db = SessionLocal()
count = db.query(Tender).count()
tender = db.query(Tender).first()

print(f"Total records: {count}")
if tender:
    print(f"Sample tender: {tender.title[:60]}...")
    print(f"Has generated content: {bool(tender.clean_description)}")
db.close()
EOF
```

---

## What Data Gets Imported

### For Each Tender Record:

#### Original Fields (from CSV)
- ✓ Title
- ✓ Description (raw HTML)
- ✓ Category
- ✓ Region
- ✓ Language
- ✓ Status
- ✓ Published date
- ✓ Original URL
- ✓ Source

#### Generated Content (from LLM)
- ✓ `clean_description` - Formatted, readable description
- ✓ `highlights` - Key bullet points
- ✓ `ai_summary` - 2-3 sentence summary

#### Structured Extracted Data (JSON)
```json
{
  "financial": {
    "bid_security_amount": 50000,
    "bid_security_currency": "ETB",
    "document_fee": 300,
    "fee_currency": "ETB",
    "other_amounts": []
  },
  "contact": {
    "emails": ["..."],
    "phones": ["..."]
  },
  "dates": {
    "closing_date": "2025-04-24T10:00:00",
    "published_date": "2025-04-13T00:00:00"
  },
  "requirements": ["requirement1", "requirement2", ...],
  "specifications": [{"Description": "...", "Quantity": "..."}, ...],
  "organization": {"name": "..."},
  "addresses": {"regions": ["Addis Ababa"]},
  "language_flag": "english",
  "tender_type": "bid_invitation",
  "is_award_notification": false
}
```

#### Processing Metadata
- ✓ `content_generated_at` - When content was generated
- ✓ `content_generation_errors` - Any errors (if any)

---

## Database Schema After Setup

### Tender Table Columns (35 total)

```
id                          UUID (pk)
title                       String (required)
description                 Text (required)
category                    String
region                      String
language                    String
source                      String
source_url                  String (unique)
tor_url                     String
budget                      Float
budget_currency             String
published_date              Date
deadline                    Date
status                      Enum

external_id                 String (unique)
content_hash                String
data_quality_score          Float
scraped_at                  DateTime
last_verified_at            DateTime
scrape_run_id               FK

ai_summary                  Text
ai_processed                Boolean
ai_processed_at             DateTime
extracted_entities          JSON

raw_text                    Text
word_count                  Integer

clean_description           Text          ← NEW
highlights                  Text          ← NEW
extracted_data              JSON          ← NEW
content_generated_at        DateTime      ← NEW
content_generation_errors   JSON          ← NEW

created_at                  DateTime
updated_at                  DateTime
```

---

## API Endpoints After Setup

All tender data is now accessible via REST API:

### Get All Tenders
```bash
GET /api/v1/tenders/
```

**Response includes:**
- Title, description, clean_description, highlights
- Category, region, deadline
- All extracted_data (financial, contact, dates, requirements, etc.)
- Generated content timestamps

### Get Single Tender
```bash
GET /api/v1/tenders/{tender_id}
```

**Returns complete tender object with:**
- Original data
- Generated content
- Structured extracted data

### Filter by Category
```bash
GET /api/v1/tenders/?category=Facilities%20Management
```

### Filter by Region
```bash
GET /api/v1/tenders/?region=Addis%20Ababa
```

---

## Frontend Integration

Once setup is complete, your frontend can:

### Get Clean Content
```javascript
const tender = await fetch(`/api/v1/tenders/${id}`);
// tender.clean_description - ready to display
// tender.highlights - display as bullet points
// tender.ai_summary - show as summary card
```

### Get Structured Data
```javascript
const tender = await fetch(`/api/v1/tenders/${id}`);
const financial = tender.extracted_data.financial;
// financial.bid_security_amount
// financial.document_fee
// financial.bid_security_currency

const contact = tender.extracted_data.contact;
// contact.emails
// contact.phones

const requirements = tender.extracted_data.requirements;
// List of requirement strings
```

### Display Organization
```javascript
const org = tender.extracted_data.organization.name;
// e.g., "Ministry of Health"
```

---

## Sample Data After Import

### Tender 1 Example
```
Title: "The Automotive Manufacturing Company of Ethiopia..."
Category: "Facilities Management"
Region: "Addis Ababa"
Deadline: 2025-04-24

Clean Description:
  **Janitorial and Cleaning Services**

  The Automotive Manufacturing Company of Ethiopia (AMCE) is inviting qualified...
  [Well-formatted, readable content]

Highlights:
  - Bid Security: ETB 50,000
  - Document Fee: ETB 300
  - Submission Deadline: April 24, 2025 at 10:00 AM
  - Required Documents: Trade License, Tax Certificate, VAT Registration...

Extracted Data:
  Financial:
    - Bid Security: 50,000 ETB
    - Document Fee: 300 ETB

  Contact:
    - Emails: eskinder.wsenbel@ivecogroup.com

  Requirements:
    - Trade License required
    - Tax Clearance Certificate
    - VAT Registration Certificate
    - TIN Certificate

  Organization: AMCE (Automotive Manufacturing Company of Ethiopia)
  Location: Addis Ababa
```

---

## Verification Checklist

After setup, verify everything is working:

- [ ] Script runs without errors
- [ ] Table dropped successfully
- [ ] Migrations applied
- [ ] 190+ tenders imported
- [ ] No import errors
- [ ] Database has tender records
- [ ] Tenders have generated content
- [ ] API endpoints return data
- [ ] Extracted data is in JSON format

---

## Troubleshooting

### "Connection refused" Error
**Problem:** PostgreSQL not running
**Solution:**
```bash
# If using Docker
docker-compose up -d

# If using local PostgreSQL
sudo service postgresql start
```

### "Table already exists" Error
**Problem:** Migrations conflict
**Solution:**
```bash
# Check migration status
alembic current

# Downgrade to previous version
alembic downgrade -1

# Then run setup again
python setup_content_pipeline.py
```

### "Import shows 0 tenders"
**Problem:** JSON file not found
**Solution:**
```bash
# Verify file exists
ls -la content_pipeline/output/processed_tenders.json

# Check file is valid JSON
python -c "import json; json.load(open('content_pipeline/output/processed_tenders.json'))"
```

### "Module not found" Error
**Problem:** Dependencies not installed
**Solution:**
```bash
pip install -r requirements.txt
```

---

## Next Steps After Setup

1. **Start Backend**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

2. **Access API Documentation**
   ```
   http://localhost:8000/docs
   ```

3. **Fetch Tender Data**
   ```bash
   curl http://localhost:8000/api/v1/tenders/
   ```

4. **Update Frontend**
   - Display `clean_description` instead of raw HTML
   - Show `highlights` as bullet points
   - Use `extracted_data` for structured information display
   - Display `ai_summary` as a preview card

---

## Important Notes

- ⚠️ **Dropping the table will delete all existing records** - This is intentional to show the new schema
- ✓ The pre-processed JSON contains 199 tenders, 190 with complete generated content
- ✓ No API costs - all content was generated locally using Ollama
- ✓ All data is structured and optimized for frontend consumption
- ✓ JSON fields are queryable - frontend can filter by any extracted field

---

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review `JSON_TO_DB_MAPPING.md` for field details
3. Check `content_pipeline/README.md` for content generation info
4. Review `CONTENT_GENERATOR_INTEGRATION.md` for system overview
