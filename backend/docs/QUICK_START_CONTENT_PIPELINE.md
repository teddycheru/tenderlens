# Quick Start: Content Pipeline (Local Setup)

Everything you need to process tenders is now in the `backend/content_pipeline/` directory!

## 📦 What's Included

```
backend/
├── content_pipeline/
│   ├── process_tenders.py          ← Main script
│   ├── test_pipeline.py            ← Test script
│   ├── output/
│   │   ├── processed_tenders.json   ← Your 1.2MB pre-processed output!
│   │   └── processing_*.log        ← Processing logs
│   └── README.md                   ← Detailed documentation
├── run_content_pipeline.py         ← Convenience wrapper
└── app/services/
    ├── csv_parser.py               ← CSV parsing
    ├── extractor.py                ← Information extraction
    ├── content_generator.py        ← LLM generation
    └── utils.py                    ← Utilities
```

## 🚀 Usage (From Backend Directory)

### Run with Your CSV File

```bash
cd backend

# Process your CSV file
python run_content_pipeline.py /path/to/your_tenders.csv

# Test with first 10 tenders
python run_content_pipeline.py /path/to/your_tenders.csv --sample-size 10

# Fast mode (no content generation)
python run_content_pipeline.py /path/to/your_tenders.csv --no-llm
```

### Run Tests

```bash
cd backend/content_pipeline
python test_pipeline.py
```

## 📊 Your Pre-Processed Output

You already have `processed_tenders.json` (1.2MB) with:
- 200 processed tenders
- Extracted structured data
- Generated summaries and clean descriptions
- Key highlights
- All organized and ready to import

## 📥 Import Into Database

### Method 1: Python Script

```bash
cd backend
python << 'EOF'
from app.services.pipeline.json_content_importer import JSONContentImporter
from app.database import SessionLocal
from pathlib import Path

db = SessionLocal()
importer = JSONContentImporter(db)
stats = importer.import_from_json(Path('content_pipeline/output/processed_tenders.json'))
print(f"✅ Imported {stats['updated']} tenders")
print(f"   Skipped: {stats['skipped']}")
print(f"   Errors: {stats['errors']}")
db.close()
EOF
```

### Method 2: Create an Import Script

Save this as `backend/import_processed_tenders.py`:

```python
#!/usr/bin/env python3
"""Import processed tenders from content_pipeline output"""

from app.services.pipeline.json_content_importer import JSONContentImporter
from app.database import SessionLocal
from pathlib import Path
import sys

def main():
    json_path = Path('content_pipeline/output/processed_tenders.json')

    if not json_path.exists():
        print(f"❌ File not found: {json_path}")
        sys.exit(1)

    db = SessionLocal()
    try:
        importer = JSONContentImporter(db)
        stats = importer.import_from_json(json_path)

        print("✅ Import Summary:")
        print(f"   Updated: {stats['updated']}")
        print(f"   Skipped: {stats['skipped']}")
        print(f"   Errors:  {stats['errors']}")
        print(f"   Total:   {stats['total']}")

    finally:
        db.close()

if __name__ == '__main__':
    main()
```

Then run:
```bash
cd backend
python import_processed_tenders.py
```

## ⚙️ Setup Requirements

### One-Time Setup

```bash
# 1. Install Ollama (if not already done)
# Download from https://ollama.ai

# 2. Start Ollama in another terminal
ollama serve

# 3. Pull the model (first time only)
ollama pull llama3.2:3b

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Run migrations
alembic upgrade head
```

### That's it! You're ready to go.

## 📋 Processing Your New Data

Step-by-step workflow:

1. **Process CSV** → Generates JSON
   ```bash
   python run_content_pipeline.py /path/to/new_tenders.csv
   ```

2. **Check output** → Verify in `content_pipeline/output/`
   ```bash
   ls -lah content_pipeline/output/
   ```

3. **Import to DB** → Load into database
   ```bash
   python import_processed_tenders.py
   # or use the inline Python method above
   ```

4. **Access from API** → Frontend reads clean data
   ```bash
   curl http://localhost:8000/api/v1/tenders/
   ```

## 💡 Tips & Tricks

### Process Large Files Overnight

```bash
# Run in background and capture output
nohup python run_content_pipeline.py large_file.csv > processing.log 2>&1 &

# Monitor progress
tail -f processing.log
```

### Process in Batches

```bash
# First 50 tenders (for testing)
python run_content_pipeline.py data.csv --sample-size 50

# Adjust batch size for speed
python run_content_pipeline.py data.csv --batch-size 50
```

### Extract Only (No LLM)

Fast mode without content generation:

```bash
python run_content_pipeline.py data.csv --no-llm
# Completes in ~4 seconds for 200 tenders
```

## 📦 What Gets Generated

The `processed_tenders.json` file contains everything your frontend needs:

```json
{
  "metadata": { /* Processing metadata */ },
  "tenders": [
    {
      "id": "tender_000000",
      "original": { /* Original tender data */ },
      "extracted": {
        /* Structured data:
           - financial (bid security, fees)
           - contact (emails, phones)
           - dates (formatted closing dates)
           - requirements (list of requirements)
           - specifications (tables/specs)
           - organization (entity name)
           - addresses (locations)
           - language_flag, tender_type, etc.
        */
      },
      "generated": {
        "summary": "2-3 sentence summary",
        "clean_description": "Well-formatted description",
        "highlights": "Bullet-point highlights"
      }
    }
  ]
}
```

## 🔍 Verify Setup

```bash
# Check Ollama is running
ollama list

# Check Llama 3.2 3B is available
ollama list | grep llama3.2

# Test the pipeline
cd backend/content_pipeline
python test_pipeline.py

# Check generated output
head -c 500 output/processed_tenders.json | python -m json.tool
```

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| "Ollama not found" | Make sure `ollama serve` is running in another terminal |
| "Out of memory" | Use `--sample-size` to process fewer tenders, or `--batch-size 10` |
| "Module not found" | Use `run_content_pipeline.py` wrapper from backend directory |
| Slow processing | This is normal (15-30s per tender). Let it run overnight for large datasets |

## 📚 Further Reading

- **Detailed Guide**: See `CONTENT_GENERATOR_INTEGRATION.md`
- **Pipeline Docs**: See `backend/content_pipeline/README.md`
- **API Docs**: Start the backend and visit http://localhost:8000/docs

## 🎯 You're All Set!

Everything is now integrated locally. No need to jump between directories:
- Run scripts from `backend/` directory
- Process your data
- Import results
- Frontend displays clean content

Happy processing! 🚀
