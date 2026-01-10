# TenderLens Import Scripts

This directory contains CLI scripts for importing and managing tender data.

## Available Scripts

### import_csv.py

Import tenders from CSV files into the database.

**Quick Start:**
```bash
# From backend directory
cd /path/to/Tender-lens-mvp/backend

# Set environment variables
export POSTGRES_HOST=localhost
export POSTGRES_USER=tenderlens
export POSTGRES_PASSWORD=tenderlens123
export POSTGRES_DB=tenderlens

# Run import
python scripts/import_csv.py <csv_file> <source_name>
```

**Usage:**
```bash
python scripts/import_csv.py <csv_file_path> <source_name> [options]

Arguments:
  csv_file              Path to CSV file to import
  source_name           Data source name (e.g., "2merkato")

Options:
  --skip-duplicates     Skip records with duplicate URLs (default)
  --no-skip-duplicates  Import all records, even duplicates
  --batch-size N        Records to commit at once (default: 100)
  --verbose             Enable detailed logging
  -h, --help           Show help message
```

**Examples:**
```bash
# Basic import
python scripts/import_csv.py tenders.csv 2merkato

# Verbose output
python scripts/import_csv.py tenders.csv 2merkato --verbose

# Custom batch size
python scripts/import_csv.py large_file.csv 2merkato --batch-size 500

# Allow duplicates
python scripts/import_csv.py tenders.csv 2merkato --no-skip-duplicates
```

**Supported Sources:**
- `2merkato` - Tenders from 2merkato.com

To add more sources, edit `app/services/pipeline/csv_importer.py`

## Full Documentation

See `backend/docs/CSV_IMPORT_GUIDE.md` for complete documentation including:
- Configuration details
- Adding new data sources
- Troubleshooting
- Integration with pipeline
