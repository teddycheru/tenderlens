"""
CSV Parser Module
Handles reading and parsing the tender CSV file with multi-line fields
"""

import pandas as pd
from typing import List, Dict, Any


class TenderCSVParser:
    """Parse tender CSV files with proper multi-line field handling"""

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.df = None
        self.tenders = []

    def load_csv(self) -> List[Dict[str, Any]]:
        """
        Load CSV file with proper quoting to handle multi-line HTML content

        Returns:
            List of tender dictionaries
        """
        try:
            # Read CSV with proper handling of quoted multi-line fields
            self.df = pd.read_csv(
                self.csv_path,
                quoting=1,  # QUOTE_ALL equivalent
                escapechar=None,
                doublequote=True,
                dtype=str
            )

            print(f"✓ Successfully loaded CSV with {len(self.df)} records")
            print(f"✓ Columns: {list(self.df.columns)}")

            # Convert to list of dictionaries
            self.tenders = self.df.fillna('').to_dict('records')

            return self.tenders

        except Exception as e:
            print(f"✗ Error loading CSV: {str(e)}")
            raise

    def validate_tenders(self) -> Dict[str, Any]:
        """
        Validate loaded tenders and check for missing fields

        Returns:
            Validation statistics dictionary
        """
        stats = {
            'total_records': len(self.tenders),
            'complete_records': 0,
            'missing_by_field': {}
        }

        if not self.tenders:
            print("✗ No tenders loaded")
            return stats

        required_fields = ['URL', 'Title', 'Description', 'Closing Date', 'Published On']

        for field in required_fields:
            missing_count = sum(1 for t in self.tenders if not t.get(field))
            stats['missing_by_field'][field] = missing_count

        # Count complete records (all required fields present)
        complete = sum(
            1 for t in self.tenders
            if all(t.get(field) for field in required_fields)
        )
        stats['complete_records'] = complete

        # Print validation results
        print(f"\n--- CSV Validation Results ---")
        print(f"Total records: {stats['total_records']}")
        print(f"Complete records: {stats['complete_records']}")
        print(f"\nMissing fields:")
        for field, count in stats['missing_by_field'].items():
            status = "✓" if count == 0 else "✗"
            print(f"  {status} {field}: {count} missing")

        return stats

    def get_batch(self, start_idx: int, batch_size: int = 20) -> List[Dict[str, Any]]:
        """
        Get a batch of tenders for processing

        Args:
            start_idx: Starting index
            batch_size: Number of tenders per batch

        Returns:
            List of tender dictionaries for the batch
        """
        end_idx = min(start_idx + batch_size, len(self.tenders))
        return self.tenders[start_idx:end_idx]

    def get_tender(self, idx: int) -> Dict[str, Any]:
        """Get a single tender by index"""
        if 0 <= idx < len(self.tenders):
            return self.tenders[idx]
        return None

    def get_total_count(self) -> int:
        """Get total number of tenders"""
        return len(self.tenders)


if __name__ == "__main__":
    # Test the parser
    parser = TenderCSVParser('/home/tewodros-cheru/Documents/Pros/content-generator/output_merged_bottom_200.csv')
    tenders = parser.load_csv()
    stats = parser.validate_tenders()

    # Show first tender structure
    if tenders:
        print(f"\n--- Sample Tender Structure ---")
        first = tenders[0]
        for key in first.keys():
            value = first[key][:100] if isinstance(first[key], str) else first[key]
            print(f"{key}: {value}...")
