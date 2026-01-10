# Documentation Map

Quick reference guide to all integration documentation.

## Main Documentation Files

### 1. **INTEGRATION_COMPLETE.md**
**What:** Complete overview of the integration
**When to read:** Start here for the big picture
**Contains:**
- Summary of what you have now
- Data ready to import
- Database schema changes
- Setup process options
- After setup details
- Next steps

**Use when:** You need a comprehensive overview before starting

---

### 2. **JSON_TO_DB_MAPPING.md**
**What:** Detailed field mapping reference
**When to read:** Before/during import to understand data flow
**Contains:**
- Original data mapping (JSON → DB)
- Extracted data mapping
- Generated content mapping
- Metadata mapping
- SQL query examples
- Frontend data structure
- Complete field checklist

**Use when:** You need to understand how JSON fields map to database columns

---

### 3. **SETUP_IMPORT_GUIDE.md**
**What:** Step-by-step setup instructions
**When to read:** Before setting up the database
**Contains:**
- Prerequisites
- Automated setup method
- Manual setup steps
- Data import details
- Database schema reference
- API endpoints
- Frontend integration guide
- Verification checklist
- Troubleshooting

**Use when:** You're ready to set up the database

---

### 4. **QUICK_START_CONTENT_PIPELINE.md**
**What:** Quick reference for content pipeline
**When to read:** When you want to quickly understand the pipeline
**Contains:**
- Quick overview
- File structure
- Usage examples
- Import methods
- Performance tips
- Troubleshooting

**Use when:** You need a quick reference without full details

---

### 5. **CONTENT_GENERATOR_INTEGRATION.md**
**What:** System architecture and integration details
**When to read:** When you want to understand the system architecture
**Contains:**
- New workflow diagram
- Quick start guide
- Database schema
- API endpoints
- File structure
- Migration guide
- Removed components
- Performance details
- Troubleshooting

**Use when:** You want to understand the overall system design

---

### 6. **backend/content_pipeline/README.md**
**What:** Content pipeline processing details
**When to read:** When processing new CSV files
**Contains:**
- Quick start guide
- Command-line options
- Output structure
- Import instructions
- Performance expectations
- Troubleshooting
- Directory structure

**Use when:** You're processing new tender CSV files

---

## Documentation Flowchart

```
NEW TO THIS INTEGRATION?
        ↓
   Read this order:
   1. INTEGRATION_COMPLETE.md ← Overview
   2. JSON_TO_DB_MAPPING.md ← Understand data
   3. SETUP_IMPORT_GUIDE.md ← Set it up
        ↓
READY TO PROCESS NEW CSVS?
        ↓
   Use: QUICK_START_CONTENT_PIPELINE.md
   Reference: backend/content_pipeline/README.md

WANT TO UNDERSTAND THE SYSTEM?
        ↓
   Read: CONTENT_GENERATOR_INTEGRATION.md

NEED QUICK ANSWERS?
        ↓
   Try: QUICK_START_CONTENT_PIPELINE.md
   Or: DOCUMENTATION_MAP.md (this file)

STUCK ON A PROBLEM?
        ↓
   Check troubleshooting in:
   - SETUP_IMPORT_GUIDE.md
   - QUICK_START_CONTENT_PIPELINE.md
   - backend/content_pipeline/README.md
```

---

## Common Questions & Where to Find Answers

### Setup & Installation

**Q: How do I set up the database?**
→ See: SETUP_IMPORT_GUIDE.md

**Q: What are the prerequisites?**
→ See: SETUP_IMPORT_GUIDE.md → Prerequisites

**Q: How do I run the setup?**
→ See: SETUP_IMPORT_GUIDE.md → Setup Methods

---

### Data & Schema

**Q: What data will I get after import?**
→ See: INTEGRATION_COMPLETE.md → Data Ready to Import

**Q: What are the new database fields?**
→ See: JSON_TO_DB_MAPPING.md or SETUP_IMPORT_GUIDE.md → Database Schema

**Q: How does JSON data map to the database?**
→ See: JSON_TO_DB_MAPPING.md

**Q: What will the frontend receive?**
→ See: JSON_TO_DB_MAPPING.md → Complete Frontend Data Structure

---

### Processing & Workflows

**Q: How do I process a new CSV file?**
→ See: QUICK_START_CONTENT_PIPELINE.md → Usage or backend/content_pipeline/README.md

**Q: What options are available for processing?**
→ See: backend/content_pipeline/README.md → Available Options

**Q: How long does processing take?**
→ See: backend/content_pipeline/README.md → Performance Expectations

---

### API & Frontend

**Q: What API endpoints are available?**
→ See: SETUP_IMPORT_GUIDE.md → API Endpoints After Setup

**Q: How do I fetch tender data from the API?**
→ See: JSON_TO_DB_MAPPING.md → SQL Query Examples

**Q: How should I update my frontend?**
→ See: SETUP_IMPORT_GUIDE.md → Frontend Integration

**Q: What should the frontend display?**
→ See: INTEGRATION_COMPLETE.md → After Setup: What Frontend Gets

---

### Troubleshooting

**Q: Database connection failed**
→ See: SETUP_IMPORT_GUIDE.md → Troubleshooting → "Connection refused"

**Q: Import shows 0 tenders**
→ See: SETUP_IMPORT_GUIDE.md → Troubleshooting → "Import shows 0"

**Q: Module not found error**
→ See: SETUP_IMPORT_GUIDE.md → Troubleshooting → "Module not found"

**Q: Migration failed**
→ See: SETUP_IMPORT_GUIDE.md → Troubleshooting → "Table already exists"

**Q: Slow performance**
→ See: backend/content_pipeline/README.md → Troubleshooting → Slow Performance

**Q: Out of memory**
→ See: backend/content_pipeline/README.md → Troubleshooting → Out of Memory

---

## File Locations Reference

### Documentation
```
/Tender-lens-mvp/
├── INTEGRATION_COMPLETE.md
├── JSON_TO_DB_MAPPING.md
├── SETUP_IMPORT_GUIDE.md
├── QUICK_START_CONTENT_PIPELINE.md
├── CONTENT_GENERATOR_INTEGRATION.md
└── DOCUMENTATION_MAP.md (this file)
```

### Setup Scripts
```
/Tender-lens-mvp/backend/
├── setup_content_pipeline.py (Automated setup)
└── run_content_pipeline.py (Run processor)
```

### Content Pipeline
```
/Tender-lens-mvp/backend/content_pipeline/
├── process_tenders.py
├── test_pipeline.py
├── csv_parser.py
├── extractor.py
├── content_generator.py
├── utils.py
├── output/
│   └── processed_tenders.json (1.2MB)
└── README.md
```

### Database/Services
```
/Tender-lens-mvp/backend/
├── app/
│   ├── models/tender.py (Updated)
│   ├── services/
│   │   ├── csv_parser.py
│   │   ├── extractor.py
│   │   ├── content_generator.py
│   │   ├── utils.py
│   │   └── pipeline/json_content_importer.py (New)
│   └── ...
├── alembic/versions/
│   └── add_content_generation_fields.py (Migration)
└── requirements.txt (Updated)
```

---

## Quick Navigation

### For Beginners (First Time)
1. Read: **INTEGRATION_COMPLETE.md**
2. Read: **JSON_TO_DB_MAPPING.md**
3. Execute: `python setup_content_pipeline.py`
4. Reference: **SETUP_IMPORT_GUIDE.md** if issues

### For Developers (Building API)
1. Read: **JSON_TO_DB_MAPPING.md**
2. Read: **SETUP_IMPORT_GUIDE.md** → API Endpoints
3. Reference: **JSON_TO_DB_MAPPING.md** → SQL Query Examples

### For Frontend Engineers
1. Read: **INTEGRATION_COMPLETE.md** → After Setup
2. Read: **JSON_TO_DB_MAPPING.md** → Complete Frontend Data Structure
3. Reference: **SETUP_IMPORT_GUIDE.md** → Frontend Integration

### For DevOps/Setup
1. Read: **SETUP_IMPORT_GUIDE.md**
2. Execute: `python setup_content_pipeline.py`
3. Reference: **SETUP_IMPORT_GUIDE.md** → Troubleshooting

---

## Document Reading Time

| Document | Reading Time | Best For |
|----------|--------------|----------|
| INTEGRATION_COMPLETE.md | 5-10 min | Overview |
| JSON_TO_DB_MAPPING.md | 10-15 min | Understanding data |
| SETUP_IMPORT_GUIDE.md | 10-15 min | Setting up |
| QUICK_START_CONTENT_PIPELINE.md | 5 min | Quick reference |
| CONTENT_GENERATOR_INTEGRATION.md | 10 min | Architecture |
| backend/content_pipeline/README.md | 5 min | Processing |
| DOCUMENTATION_MAP.md | 3-5 min | Navigation |

---

## Key Facts to Remember

✓ **190 tenders ready to import** (from processed_tenders.json)
✓ **5 new database fields** to store generated content
✓ **All data is structured** as JSON for easy frontend access
✓ **No API costs** - content generated locally with Ollama
✓ **Automatic setup available** - run one script
✓ **Complete documentation** - everything is documented
✓ **Frontend ready** - all fields available for display

---

## Setup Checklist

Before running setup, ensure:
- [ ] PostgreSQL is running
- [ ] Python dependencies installed
- [ ] You've read INTEGRATION_COMPLETE.md
- [ ] You understand the data structure (JSON_TO_DB_MAPPING.md)
- [ ] You have 5-10 minutes available

Then:
- [ ] Run: `python backend/setup_content_pipeline.py`
- [ ] Verify: Check database has records
- [ ] Test: Start backend and test API

---

## Maintenance Notes

### When Processing New Tenders
1. Reference: `backend/content_pipeline/README.md`
2. Command: `python run_content_pipeline.py /path/to/csv`
3. Import: Use `JSONContentImporter` class

### When Updating Frontend
1. Reference: `JSON_TO_DB_MAPPING.md`
2. Available fields: See "Complete Frontend Data Structure"
3. API Examples: See "SQL Query Examples"

### When Troubleshooting
1. Check: Relevant troubleshooting section
2. Files: `SETUP_IMPORT_GUIDE.md`, `backend/content_pipeline/README.md`
3. Logs: Check `content_pipeline/output/processing_*.log`

---

## Summary

This DOCUMENTATION_MAP.md file serves as your **navigation guide** for all integration documentation.

- Use it to find answers quickly
- Reference it when onboarding team members
- Keep it accessible for future reference

**Bookmark this file for quick access to the documentation you need!**

---

**Last Updated:** 2025-11-19
**Version:** 1.0
**Status:** Complete & Ready
