"""
Main Processing Script
Orchestrates CSV parsing, information extraction, and content generation
Saves output to JSON with memory-efficient batching
"""

import json
import sys
import os
import gc
import logging
from typing import Dict, List, Any
from tqdm import tqdm
from datetime import datetime

# Local imports (modules are in this directory)
from csv_parser import TenderCSVParser
from hybrid_extractor import HybridExtractor, ContentGeneratorWrapper  # Hybrid extractor (regex + LLM)

# Setup logging
def setup_logging(output_dir: str = './output'):
    """Setup logging to both file and console"""
    os.makedirs(output_dir, exist_ok=True)
    log_file = os.path.join(output_dir, f'processing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return log_file


class TenderProcessor:
    """Main processor that coordinates all operations"""

    def __init__(
        self,
        csv_path: str,
        output_dir: str = './output',
        batch_size: int = 20,
        use_llm: bool = True,
        model: str = 'llama3.2:3b',
        sample_size: int = None
    ):
        self.csv_path = csv_path
        self.output_dir = output_dir
        self.batch_size = batch_size
        self.use_llm = use_llm
        self.model = model
        self.sample_size = sample_size

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Initialize components
        self.parser = TenderCSVParser(csv_path)
        self.extractor = HybridExtractor(model=model, use_llm=use_llm)  # Hybrid extraction (regex + LLM)
        self.generator = ContentGeneratorWrapper(model=model) if use_llm else None

        self.stats = {
            'total_tenders': 0,
            'successfully_extracted': 0,
            'extraction_errors': 0,
            'successfully_generated': 0,
            'generation_errors': 0,
            'start_time': None,
            'end_time': None,
            'processing_duration': None
        }

    def process_all(self) -> Dict[str, Any]:
        """
        Process all tenders in the CSV file

        Returns:
            Final output dictionary
        """
        self.stats['start_time'] = datetime.now().isoformat()
        print(f"\n{'='*60}")
        print(f"TENDER PROCESSING PIPELINE")
        print(f"{'='*60}")
        logging.info("Starting tender processing pipeline")

        # Step 1: Load CSV
        print(f"\n[Step 1/4] Loading CSV file...")
        tenders = self.parser.load_csv()

        if not tenders:
            print("✗ No tenders loaded. Aborting.")
            return None

        # Validate
        print(f"\n[Step 2/4] Validating data...")
        self.parser.validate_tenders()

        # Limit to sample size if specified
        if self.sample_size and self.sample_size < len(tenders):
            tenders = tenders[:self.sample_size]
            print(f"⚠ Limited to first {self.sample_size} tenders for testing")

        self.stats['total_tenders'] = len(tenders)

        # Step 3: Check for existing checkpoint and resume
        print(f"\n[Step 3/4] Processing {len(tenders)} tenders in batches of {self.batch_size}...")
        all_results = []
        start_index = 0

        # Check if output file exists (checkpoint)
        output_file = os.path.join(self.output_dir, 'processed_tenders.json')
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    all_results = existing_data.get('tenders', [])
                    start_index = len(all_results)

                    if start_index > 0:
                        print(f"\n✓ Resuming from checkpoint: {start_index}/{len(tenders)} tenders already processed")
                        logging.info(f"Resuming from tender {start_index}")
            except Exception as e:
                logging.warning(f"Could not load checkpoint: {e}. Starting fresh.")
                all_results = []
                start_index = 0

        # Process remaining tenders
        for batch_start in tqdm(
            range(start_index, len(tenders), self.batch_size),
            desc="Processing batches",
            unit="batch",
            initial=start_index // self.batch_size,
            total=(len(tenders) + self.batch_size - 1) // self.batch_size
        ):
            batch_end = min(batch_start + self.batch_size, len(tenders))
            batch_tenders = tenders[batch_start:batch_end]

            batch_results = self._process_batch(batch_tenders, batch_start)
            all_results.extend(batch_results)

            # Save checkpoint after each batch
            self._save_results(all_results)
            logging.info(f"Checkpoint saved: {len(all_results)} tenders processed")

            # Memory cleanup
            gc.collect()

        # Step 4: Final save
        print(f"\n[Step 4/4] Finalizing results...")
        output_file = self._save_results(all_results)

        self.stats['end_time'] = datetime.now().isoformat()

        # Print statistics
        self._print_statistics(output_file)

        return {
            'output_file': output_file,
            'stats': self.stats,
            'results': all_results
        }

    def _process_batch(self, batch_tenders: List[Dict], batch_start_idx: int) -> List[Dict]:
        """
        Process a single batch of tenders

        Args:
            batch_tenders: List of tender dictionaries
            batch_start_idx: Starting index of the batch

        Returns:
            List of processed results
        """
        batch_results = []
        logging.info(f"Starting batch processing with {len(batch_tenders)} tenders")

        for local_idx, tender in enumerate(batch_tenders):
            global_idx = batch_start_idx + local_idx
            tender_title = tender.get('Title', 'Unknown')[:50]
            logging.info(f"Processing tender {global_idx}: {tender_title}...")

            result = {
                'id': f"tender_{global_idx:06d}",
                'index': global_idx,
                'original': {
                    'url': tender.get('URL', ''),
                    'title': tender.get('Title', ''),
                    'category': tender.get('Predicted_Category', ''),
                    'status': tender.get('Bidding Status', ''),
                    'region': tender.get('Region', ''),
                    'closing_date_raw': tender.get('Closing Date', ''),
                    'published_on': tender.get('Published On', ''),
                    'language': tender.get('Language', '')
                },
                'extracted': {},
                'generated': {},
                'processing_status': 'success',
                'errors': []
            }

            try:
                # Extract structured information using Hybrid Extractor
                logging.debug(f"Extracting data for tender {global_idx}")
                extracted = self.extractor.extract_all(tender)
                result['extracted'] = extracted
                self.stats['successfully_extracted'] += 1
                logging.debug(f"Extraction completed for tender {global_idx}")

                # Log extraction quality
                confidence = extracted.get('extraction_confidence', {})
                extraction_method = extracted.get('extraction_method', 'unknown')
                needs_review = extracted.get('needs_manual_review', False)

                logging.info(f"Tender {global_idx}: method={extraction_method}, "
                           f"confidence={confidence.get('overall', 0):.2f}, "
                           f"needs_review={needs_review}")

            except Exception as e:
                error_msg = f"Extraction error: {str(e)}"
                result['errors'].append(error_msg)
                result['processing_status'] = 'extraction_failed'
                self.stats['extraction_errors'] += 1
                logging.error(f"Extraction failed for tender {global_idx}: {str(e)}")
                batch_results.append(result)
                continue

            # Generate content if LLM is enabled
            if self.use_llm and self.generator:
                # Check if we should skip content generation
                skip_generation = False
                skip_reason = None

                # Skip if non-English language detected
                if extracted.get('language_flag') != 'english':
                    skip_generation = True
                    skip_reason = f"Non-English content ({extracted.get('language_flag')})"

                # Skip if award notification
                if extracted.get('is_award_notification'):
                    skip_generation = True
                    skip_reason = "Award notification (not a bid invitation)"

                if skip_generation:
                    logging.info(f"Skipping content generation for tender {global_idx}: {skip_reason}")
                    result['generated'] = {
                        'summary': None,
                        'clean_description': None,
                        'highlights': None,
                        'skip_reason': skip_reason
                    }
                    result['processing_status'] = 'skipped'
                    self.stats['successfully_generated'] += 1
                else:
                    try:
                        # Generate all content in a single LLM call (more efficient)
                        logging.debug(f"Generating content for tender {global_idx}")
                        generated = self.generator.generate_content(tender, extracted)
                        result['generated'] = generated
                        self.stats['successfully_generated'] += 1
                        logging.info(f"Content generation completed for tender {global_idx}")

                        # Validate dates in generated content
                        self._validate_dates(result, extracted)

                    except Exception as e:
                        error_msg = f"Generation error: {str(e)}"
                        result['errors'].append(error_msg)
                        result['processing_status'] = 'generation_failed'
                        self.stats['generation_errors'] += 1
                        logging.error(f"Content generation failed for tender {global_idx}: {str(e)}")

            batch_results.append(result)

        logging.info(f"Batch processing completed. Extracted: {len([r for r in batch_results if r['processing_status']=='success'])}")
        return batch_results

    def _save_results(self, all_results: List[Dict]) -> str:
        """
        Save all results to JSON file

        Args:
            all_results: List of all processed results

        Returns:
            Path to output file
        """
        output_data = {
            'metadata': {
                'total_tenders': self.stats['total_tenders'],
                'successfully_processed': self.stats['successfully_extracted'],
                'extraction_errors': self.stats['extraction_errors'],
                'model_used': self.model if self.use_llm else 'none',
                'generated_content': self.stats['successfully_generated'],
                'generation_errors': self.stats['generation_errors'],
                'processing_start': self.stats['start_time'],
                'processing_end': self.stats['end_time'],
                'batch_size': self.batch_size,
                'timestamp': datetime.now().isoformat()
            },
            'tenders': all_results
        }

        output_file = os.path.join(self.output_dir, 'processed_tenders.json')

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"✓ Results saved to: {output_file}")
        return output_file

    def _validate_dates(self, result: Dict[str, Any], extracted: Dict[str, Any]):
        """
        Validate that generated content matches extracted dates

        Args:
            result: Processing result with generated content
            extracted: Extracted structured data
        """
        closing_date = extracted.get('dates', {}).get('closing_date', '')
        if not closing_date:
            return

        # Extract year from closing date for flexible matching
        closing_year = closing_date.split('-')[0] if closing_date else ''
        summary = result.get('generated', {}).get('summary', '').lower()

        # Check if summary contains wrong month references (simple heuristic)
        # Flag if it mentions dates that might be document availability dates
        date_warning = None
        if summary and closing_year:
            # Extract month from closing date (e.g., "2025-04-24" -> "04")
            closing_month_num = closing_date.split('-')[1] if '-' in closing_date else ''

            # Common date patterns to check
            if 'april 7' in summary or 'apr 7' in summary or '7 april' in summary:
                if closing_date.startswith(f"{closing_year}-04"):  # Both in April but different days
                    date_warning = f"⚠ Summary mentions April 7 (document availability) instead of actual deadline {closing_date}"

        if date_warning:
            result['errors'].append(date_warning)
            if 'date_validation_warning' not in self.stats:
                self.stats['date_validation_warning'] = 0
            self.stats['date_validation_warning'] += 1

    def _print_statistics(self, output_file: str):
        """Print processing statistics"""
        print(f"\n{'='*60}")
        print(f"PROCESSING STATISTICS")
        print(f"{'='*60}")
        print(f"Total tenders: {self.stats['total_tenders']}")
        print(f"Successfully extracted: {self.stats['successfully_extracted']}")
        print(f"Extraction errors: {self.stats['extraction_errors']}")

        if self.use_llm:
            success_rate = (self.stats['successfully_generated'] / max(self.stats['successfully_extracted'], 1)) * 100
            print(f"Successfully generated content: {self.stats['successfully_generated']}")
            print(f"Generation errors: {self.stats['generation_errors']}")
            print(f"Content generation success rate: {success_rate:.1f}%")

            if self.stats.get('date_validation_warning', 0) > 0:
                print(f"\n⚠ Date validation warnings: {self.stats['date_validation_warning']}")
                print(f"  (Generated content may have confused document availability dates with submission deadlines)")

        print(f"\nOutput file: {output_file}")
        print(f"File size: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")
        print(f"{'='*60}\n")


def main():
    """Main entry point"""
    import argparse

    # Setup logging
    log_file = setup_logging()
    logging.info("="*60)
    logging.info("TENDER PROCESSING PIPELINE STARTED")
    logging.info("="*60)

    parser = argparse.ArgumentParser(description='Process tender data and generate content')
    parser.add_argument(
        'csv_file',
        help='Path to input CSV file'
    )
    parser.add_argument(
        '--output-dir',
        default='./output',
        help='Output directory for results (default: ./output)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=20,
        help='Batch size for processing (default: 20)'
    )
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Skip LLM-based content generation'
    )
    parser.add_argument(
        '--model',
        default='llama3.2:3b',
        help='Ollama model to use (default: llama3.2:3b)'
    )
    parser.add_argument(
        '--sample-size',
        type=int,
        default=None,
        help='Process only first N tenders (for testing)'
    )

    args = parser.parse_args()

    # Validate CSV file exists
    if not os.path.exists(args.csv_file):
        print(f"✗ Error: CSV file not found: {args.csv_file}")
        sys.exit(1)

    # Create processor
    processor = TenderProcessor(
        csv_path=args.csv_file,
        output_dir=args.output_dir,
        batch_size=args.batch_size,
        use_llm=not args.no_llm,
        model=args.model,
        sample_size=args.sample_size
    )

    # Process
    try:
        logging.info("Starting processing...")
        result = processor.process_all()
        if result:
            print("✓ Processing completed successfully!")
            logging.info("Processing completed successfully!")
            logging.info(f"Log file: {log_file}")
        else:
            print("✗ Processing failed")
            logging.error("Processing failed - no results returned")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n✗ Processing interrupted by user")
        logging.warning("Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        logging.error(f"Unexpected error: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
