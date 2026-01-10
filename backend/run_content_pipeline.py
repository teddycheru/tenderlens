#!/usr/bin/env python3
"""
Convenience wrapper to run the content processing pipeline from the backend directory.

Usage:
    python run_content_pipeline.py /path/to/tenders.csv [options]
    python run_content_pipeline.py --help
"""

import sys
import os
import subprocess

# Get the content_pipeline directory
CONTENT_PIPELINE_DIR = os.path.join(os.path.dirname(__file__), 'content_pipeline')
PROCESS_SCRIPT = os.path.join(CONTENT_PIPELINE_DIR, 'process_tenders.py')

def main():
    """Run the content pipeline processor."""
    # Ensure we have at least one argument
    if len(sys.argv) < 2:
        print("Usage: python run_content_pipeline.py /path/to/tenders.csv [options]")
        print("       python run_content_pipeline.py --help")
        print("\nExample:")
        print("  python run_content_pipeline.py data/tenders.csv")
        print("  python run_content_pipeline.py data/tenders.csv --sample-size 10")
        print("  python run_content_pipeline.py data/tenders.csv --no-llm --batch-size 50")
        sys.exit(1)

    # Build the command
    cmd = [sys.executable, PROCESS_SCRIPT] + sys.argv[1:]

    print(f"Running content pipeline from: {CONTENT_PIPELINE_DIR}")
    print(f"Command: {' '.join(cmd)}\n")

    # Change to content_pipeline directory to ensure relative paths work correctly
    old_cwd = os.getcwd()
    try:
        os.chdir(CONTENT_PIPELINE_DIR)
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    finally:
        os.chdir(old_cwd)

if __name__ == '__main__':
    main()
