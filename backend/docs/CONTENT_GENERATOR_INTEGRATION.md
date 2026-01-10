# Content Generator Integration Guide

## Overview

The Tender-Lens MVP now integrates with the **offline LLM content-generator** for processing tender documents. This replaces the previously failing FLAN-T5 and GLiNER fallback services with a more robust, memory-efficient approach using **Ollama with Llama 3.2 3B**.

## New Workflow

```
CSV File (2merkato or other source)
    ↓
[1] Content-Generator Script
    (Extract & Generate Content)
    ├─ Information Extraction
    ├─ Content Generation (Ollama + Llama 3.2 3B)
    └─ Output: processed_tenders.json
    ↓
[2] JSON Content Importer
    (Load into Database)
    ├─ Read JSON output
    ├─ Find/create tenders
    └─ Store generated content in DB
    ↓
[3] Database
    (Tender records with generated content)
    ├─ clean_description
    ├─ highlights
    ├─ extracted_data
    └─ content_generated_at
    ↓
[4] Backend API
    (Serve data to frontend)
    ↓
[5] Frontend
    (Display clean, organized content)
```

## Quick Start: Processing Tenders

### Step 1: Set Up Content-Generator

```bash
# Navigate to content-generator directory
cd /path/to/content-generator

# Install dependencies
pip install -r requirements.txt

# Install Ollama (if not already installed)
# Download from: https://ollama.ai

# Start Ollama service in a separate terminal
ollama serve

# Pull the Llama 3.2 3B model (one-time setup)
ollama pull llama3.2:3b
```

### Step 2: Process CSV File

```bash
# Basic usage
python process_tenders.py /path/to/output_merged_bottom_200.csv

# With options
python process_tenders.py /path/to/tenders.csv \
    --output-dir ./output \
    --batch-size 20 \
    --sample-size 10  # Process only first 10 for testing

# Fast mode (extraction only, no content generation)
python process_tenders.py /path/to/tenders.csv --no-llm
```

**Output:** `output/processed_tenders.json`

### Step 3: Import JSON into Database

```python
from app.services.pipeline.json_content_importer import JSONContentImporter
from app.database import SessionLocal
from pathlib import Path

# Get database session
db = SessionLocal()

# Create importer
importer = JSONContentImporter(db)

# Import processed content
json_path = Path('path/to/processed_tenders.json')
stats = importer.import_from_json(json_path)

print(f"Imported: {stats['updated']} tenders")
print(f"Skipped: {stats['skipped']} (already generated)")
print(f"Errors: {stats['errors']}")

# Close session
db.close()
```

### Step 4: Frontend Reads from Database

The frontend now reads fully processed tender data from the database:
- Clean descriptions
- Extracted highlights
- Structured data (financial, contact, dates, requirements, specifications)
- All formatting handled server-side

## Database Schema

### New Tender Model Fields

```python
class Tender:
    # ... existing fields ...

    # Content Generation Fields (NEW)
    clean_description: Text          # LLM-generated clean description
    highlights: Text                 # LLM-generated key highlights
    extracted_data: JSON             # Structured extraction results
    content_generated_at: DateTime    # When content was generated
    content_generation_errors: JSON   # Any errors during generation
```

### Extracted Data Structure

The `extracted_data` field contains:

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
    "emails": ["contact@example.com"],
    "phones": ["+251911234567"]
  },
  "dates": {
    "closing_date": "2025-04-24 at 10:00:00",
    "published_date": "2025-04-13 at 00:00:00"
  },
  "requirements": ["Trade License", "Tax Certificate", ...],
  "specifications": [
    {"Description": "...", "Quantity": "...", ...},
    ...
  ],
  "organization": {"name": "Ministry of Health"},
  "addresses": {"po_boxes": [], "regions": ["Addis Ababa"]},
  "language_flag": "english",
  "tender_type": "bid_invitation",
  "is_award_notification": false
}
```

## API Endpoints

### GET /api/v1/tenders/{tender_id}

Returns tender with all generated content:

```json
{
  "id": "uuid",
  "title": "Ministry of Health - Medical Equipment",
  "description": "Raw HTML description",
  "clean_description": "Formatted clean description",
  "highlights": "Key highlights as bullet points",
  "extracted_data": { ... },
  "category": "Healthcare",
  "region": "Addis Ababa",
  "deadline": "2025-04-24",
  "status": "published",
  "content_generated_at": "2025-11-19T12:00:00Z"
}
```

### GET /api/v1/tenders

List tenders with filtering - now all have generated content available.

## Migration Guide

### For Existing Database

Run the Alembic migration to add new fields:

```bash
cd backend
alembic upgrade head
```

This creates:
- `clean_description` column
- `highlights` column
- `extracted_data` JSON column
- `content_generated_at` column
- `content_generation_errors` column
- Index on `content_generated_at`

### Migrating Existing Tenders

For tenders already in the database:

```bash
# Option 1: Re-process from original CSV with content-generator
python content-generator/process_tenders.py original_file.csv
# Then import the JSON

# Option 2: Only process tenders without content
# (content-generator will skip those with content_generated_at already set)
```

## Removed Components

The following components have been removed due to failures:

- **hybrid_summarizer.py** - FLAN-T5 based summarization
- **gliner_service.py** - GLiNER entity extraction fallback

### Why?

Both services had reliability issues and required significant memory overhead. The offline LLM approach (Ollama + Llama 3.2 3B) is:
- ✅ More reliable
- ✅ Memory efficient (4GB during inference)
- ✅ No API costs
- ✅ Full data privacy
- ✅ Offline-first design

## API Key Configuration

### If Using OpenAI/Anthropic APIs

The backend still supports OpenAI and Anthropic APIs for real-time summarization of new documents. Set in `.env`:

```
OPENAI_API_KEY=your-key-here
# or
ANTHROPIC_API_KEY=your-key-here
```

However, the recommended approach is to use the content-generator offline pipeline.

## Performance

### Processing Times (on 8GB RAM system)

| Stage | Per Tender | Total for 200 |
|-------|-----------|---------------|
| CSV Parsing | <1ms | <1 sec |
| Information Extraction | ~20ms | ~4 sec |
| Content Generation (Llama 3.2 3B) | 15-30s | 50-100 min |
| **Total with LLM** | **~20-30s** | **~1-2 hours** |
| **Total without LLM** | **~20ms** | **~4 seconds** |

### Optimization Tips

- Run overnight or in background for large datasets
- Use `--sample-size 10` to test first
- Use `--no-llm` flag for quick validation
- Increase `--batch-size 50` for faster processing
- Close other applications to free RAM

## Troubleshooting

### Ollama Not Found

```
Error: Ollama not found. Please install Ollama and run: ollama serve
```

**Solution:**
1. Download from https://ollama.ai
2. Run `ollama serve` in a separate terminal
3. Retry

### Out of Memory

```
MemoryError: Unable to allocate ... MB
```

**Solutions:**
1. Use smaller batch size: `--batch-size 10`
2. Close other applications
3. Use `--no-llm` to skip content generation
4. Process in smaller chunks

### Model Not Found

```
Error: model 'llama3.2:3b' not found
```

**Solution:**
```bash
ollama pull llama3.2:3b
ollama list  # Verify
```

## File Structure

```
backend/
├── app/
│   ├── models/
│   │   └── tender.py                    # Updated with new fields
│   ├── services/
│   │   ├── pipeline/
│   │   │   ├── csv_importer.py         # Existing CSV import
│   │   │   └── json_content_importer.py # NEW: JSON import
│   │   ├── csv_parser.py               # NEW: From content-generator
│   │   ├── extractor.py                # NEW: From content-generator
│   │   ├── content_generator.py        # NEW: From content-generator
│   │   └── utils.py                    # NEW: From content-generator
│   └── api/
│       └── v1/
│           └── tenders.py              # Updated to serve generated content
└── alembic/
    └── versions/
        └── add_content_generation_fields.py  # NEW: Migration
```

## Example: Complete Workflow

```bash
# 1. Process CSV with content-generator
cd content-generator
python process_tenders.py /path/to/output_merged_bottom_200.csv
# Output: output/processed_tenders.json

# 2. Import into database (from backend directory)
cd ../backend
python << 'EOF'
from app.services.pipeline.json_content_importer import JSONContentImporter
from app.database import SessionLocal
from pathlib import Path

db = SessionLocal()
importer = JSONContentImporter(db)
stats = importer.import_from_json(Path('../content-generator/output/processed_tenders.json'))
print(f"✅ Imported {stats['updated']} tenders")
db.close()
EOF

# 3. Start backend
python -m uvicorn app.main:app --reload

# 4. Access API
curl http://localhost:8000/api/v1/tenders/tender_000000

# 5. Frontend displays the clean content
```

## Support

- Content-Generator Docs: See `content-generator/README.md`
- API Docs: http://localhost:8000/docs
- Database Schema: `backend/app/models/tender.py`

## References

- Ollama: https://ollama.ai
- Llama 3.2: https://llama.meta.com
- FastAPI: https://fastapi.tiangolo.com
- SQLAlchemy: https://sqlalchemy.org
