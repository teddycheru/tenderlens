# backend/app/services/pipeline/__init__.py
"""
ETL Pipeline services for processing scraped tender data.
"""

from app.services.pipeline.transformer import tender_transformer
from app.services.pipeline.deduplicator import tender_deduplicator
from app.services.pipeline.loader import tender_loader
from app.services.pipeline.orchestrator import pipeline_orchestrator
from app.services.pipeline.csv_importer import CSVImporter, create_importer_for_source, MERKATO_CONFIG

__all__ = [
    "tender_transformer",
    "tender_deduplicator",
    "tender_loader",
    "pipeline_orchestrator",
    "CSVImporter",
    "create_importer_for_source",
    "MERKATO_CONFIG",
]
