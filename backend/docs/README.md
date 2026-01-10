# Documentation

Central documentation hub for the Tender-Lens MVP content pipeline integration.

## 📚 Documentation Files

### Start Here
- **[DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md)** - Navigation guide to all documentation
  - Quick reference for finding information
  - Common questions and answers
  - File locations reference

### Setup & Integration
- **[INTEGRATION_COMPLETE.md](INTEGRATION_COMPLETE.md)** - Complete overview of integration
  - What you have now
  - Data ready to import
  - Database schema changes
  - Setup process and next steps

- **[SETUP_IMPORT_GUIDE.md](SETUP_IMPORT_GUIDE.md)** - Step-by-step setup instructions
  - Prerequisites
  - Automated setup (recommended)
  - Manual setup steps
  - Verification checklist
  - Troubleshooting guide

### Reference & Details
- **[JSON_TO_DB_MAPPING.md](JSON_TO_DB_MAPPING.md)** - Detailed field mapping reference
  - How JSON fields map to database columns
  - SQL query examples
  - Frontend data structure
  - Complete field checklist

- **[QUICK_START_CONTENT_PIPELINE.md](QUICK_START_CONTENT_PIPELINE.md)** - Quick reference guide
  - Quick start examples
  - Common commands
  - Import methods
  - Tips and tricks

- **[CONTENT_GENERATOR_INTEGRATION.md](CONTENT_GENERATOR_INTEGRATION.md)** - System architecture
  - System overview
  - Workflow diagrams
  - API endpoints
  - Performance details

### Additional Documentation
- **[CSV_IMPORT_GUIDE.md](CSV_IMPORT_GUIDE.md)** - CSV import details (existing)

---

## 🚀 Quick Start

### 1. Understand Your Workflow
```bash
cat ../WORKFLOW_GUIDE.md
# Read this first to understand Phase 1 (initial) vs Phase 2 (ongoing)
```

### 2. Understand the Integration
```bash
cat DOCUMENTATION_MAP.md
cat INTEGRATION_COMPLETE.md
```

### 3. Review Data Structure
```bash
cat JSON_TO_DB_MAPPING.md
```

### 4. Set Up Database (Phase 1 - Initial Only)
```bash
cd ../
python setup_content_pipeline.py
# Drops table, runs migrations, imports 190 pre-processed tenders
```

### 5. Deploy
```bash
python -m uvicorn app.main:app --reload
```

### 6. For New Tenders (Phase 2 - Ongoing)
```bash
# Process new CSV file
python run_content_pipeline.py /path/to/new_tenders.csv

# Import to database
python import_json_to_db.py
```

---

## 📖 How to Use This Documentation

### If you're...

**New to this integration:**
1. Read `DOCUMENTATION_MAP.md` (5 min)
2. Read `INTEGRATION_COMPLETE.md` (10 min)
3. Read `SETUP_IMPORT_GUIDE.md` (10 min)
4. Run `setup_content_pipeline.py`

**Implementing the API:**
1. Read `JSON_TO_DB_MAPPING.md`
2. Check SQL query examples
3. Reference field mappings

**Building frontend features:**
1. Read `JSON_TO_DB_MAPPING.md` → Complete Frontend Data Structure
2. Check API response examples
3. Use SQL query examples for reference

**Processing new CSV files:**
1. Go to `../content_pipeline/`
2. Read `README.md` there
3. Use `process_tenders.py` script

**Troubleshooting issues:**
1. Check relevant troubleshooting section in:
   - `SETUP_IMPORT_GUIDE.md` (setup issues)
   - `../content_pipeline/README.md` (processing issues)

---

## 📁 File Structure

```
backend/
├── docs/                          ← You are here
│   ├── README.md                  (this file)
│   ├── DOCUMENTATION_MAP.md       (navigation guide)
│   ├── INTEGRATION_COMPLETE.md    (overview)
│   ├── SETUP_IMPORT_GUIDE.md      (setup)
│   ├── JSON_TO_DB_MAPPING.md      (field reference)
│   ├── QUICK_START_CONTENT_PIPELINE.md
│   ├── CONTENT_GENERATOR_INTEGRATION.md
│   └── CSV_IMPORT_GUIDE.md
│
├── content_pipeline/
│   ├── README.md                  (processing guide)
│   ├── process_tenders.py
│   ├── test_pipeline.py
│   ├── output/
│   │   └── processed_tenders.json (1.2MB DATA)
│   └── ...
│
├── setup_content_pipeline.py      ← RUN THIS
├── run_content_pipeline.py
└── ...
```

---

## 🎯 Key Information

### Data Ready
- **190 processed tenders** in `content_pipeline/output/processed_tenders.json`
- **Generated content:** Summaries, clean descriptions, highlights
- **Structured data:** Financial, contact, dates, requirements, specs, organization
- **Size:** 1.2MB

### Database Schema
- **5 new columns** for generated content
- **35 total columns** (30 existing + 5 new)
- **Migration ready** to apply

### Setup Time
- **Automated setup:** 2-5 minutes
- **Full integration:** ~30 minutes including API testing

### Documentation Size
- **6 main files**
- **2,279 lines** of comprehensive documentation
- **All questions covered**

---

## 📋 Documentation Checklist

- [x] Architecture overview
- [x] Setup instructions (automated + manual)
- [x] Data structure documentation
- [x] Field mapping reference
- [x] SQL query examples
- [x] Frontend integration guide
- [x] API endpoint documentation
- [x] Troubleshooting guides
- [x] Quick start guides
- [x] Navigation map

---

## 🔗 Quick Links

| Need to... | See... |
|-----------|--------|
| Find a topic | DOCUMENTATION_MAP.md |
| Set up database | SETUP_IMPORT_GUIDE.md |
| Understand data | JSON_TO_DB_MAPPING.md |
| Quick reference | QUICK_START_CONTENT_PIPELINE.md |
| Learn architecture | CONTENT_GENERATOR_INTEGRATION.md |
| Process CSV | ../content_pipeline/README.md |

---

## ✅ Pre-Setup Checklist

Before running `python setup_content_pipeline.py`:

- [ ] PostgreSQL running (or Docker)
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Read `SETUP_IMPORT_GUIDE.md`
- [ ] Understand the data structure from `JSON_TO_DB_MAPPING.md`

---

## 🚀 After Setup

Once setup is complete:

1. **API is ready:** `GET /api/v1/tenders/`
2. **Data is loaded:** 190 tender records with generated content
3. **Frontend can access:** All structured data via API
4. **Next:** Update frontend to display clean content

---

## 💡 Tips

- **Start with `DOCUMENTATION_MAP.md`** - It's your navigation guide
- **Use as reference** - Bookmark frequently accessed docs
- **Share with team** - All information is here for new developers
- **Keep updated** - As new features are added, documentation grows

---

## Support

All questions answered in the documentation:

- Setup issues? → `SETUP_IMPORT_GUIDE.md` Troubleshooting
- Data structure? → `JSON_TO_DB_MAPPING.md`
- Processing? → `../content_pipeline/README.md`
- Quick answer? → `DOCUMENTATION_MAP.md` Common Questions

---

**Last Updated:** 2025-11-19
**Status:** Complete & Ready for Production
