"""
Benchmark BGE-M3 embedding generation on your infrastructure.
Tests with 100 sample tenders to validate performance assumptions.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import statistics
from datetime import datetime, timezone
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.tender import Tender
from typing import List, Dict
import json

class EmbeddingBenchmark:

    def __init__(self, model_name: str = "BAAI/bge-m3"):
        self.model = None
        self.model_name = model_name
        self.results = {
            "model_name": model_name,
            "test_date": datetime.now(timezone.utc).isoformat(),
            "model_load_time": 0,
            "embedding_times": [],
            "sample_sizes": [],
            "statistics": {}
        }

    def load_model(self):
        """Load embedding model and measure load time"""
        print(f"Loading {self.model_name} model...")
        if "bge-m3" in self.model_name.lower():
            print("This will download ~2.2GB on first run...")
        start = time.time()
        self.model = SentenceTransformer(self.model_name)
        load_time = time.time() - start
        self.results["model_load_time"] = load_time
        print(f"✅ Model loaded in {load_time:.2f} seconds")
        return load_time

    def get_sample_tenders(self, db: Session, limit: int = 100) -> List[Tender]:
        """Get sample tenders from database"""
        tenders = db.query(Tender).limit(limit).all()
        print(f"✅ Retrieved {len(tenders)} sample tenders")
        return tenders

    def prepare_tender_text(self, tender: Tender) -> str:
        """Prepare tender text for embedding (same as production)"""
        text_parts = [
            tender.title or "",
            tender.description or "",
            tender.ai_summary or ""  # Use existing AI summary if available
        ]
        text = " ".join(filter(None, text_parts))
        return text.strip()

    def benchmark_single_tender(self, tender: Tender) -> Dict:
        """Benchmark embedding generation for a single tender"""
        text = self.prepare_tender_text(tender)
        text_length = len(text)

        # Measure embedding generation time
        start = time.time()
        embedding = self.model.encode(text, normalize_embeddings=True)
        duration = time.time() - start

        return {
            "tender_id": str(tender.id),
            "text_length": text_length,
            "embedding_dimensions": len(embedding),
            "duration_seconds": duration
        }

    def run_benchmark(self, num_samples: int = 100):
        """Run full benchmark"""
        print(f"\n{'='*60}")
        print(f"Embedding Benchmark - {self.model_name}")
        print(f"{'='*60}\n")

        # Load model
        self.load_model()

        # Get sample tenders
        db = SessionLocal()
        try:
            tenders = self.get_sample_tenders(db, limit=num_samples)

            if len(tenders) == 0:
                print("❌ No tenders found in database. Please add some test data first.")
                return

            print(f"\nProcessing {len(tenders)} tenders...")
            print(f"{'='*60}\n")

            # Benchmark each tender
            for i, tender in enumerate(tenders, 1):
                result = self.benchmark_single_tender(tender)
                self.results["embedding_times"].append(result["duration_seconds"])
                self.results["sample_sizes"].append(result["text_length"])

                # Print progress every 10 tenders
                if i % 10 == 0 or i == len(tenders):
                    avg_time = statistics.mean(self.results["embedding_times"])
                    print(f"[{i}/{len(tenders)}] Avg time: {avg_time:.3f}s | "
                          f"Latest: {result['duration_seconds']:.3f}s | "
                          f"Text length: {result['text_length']} chars")

            # Calculate statistics
            self.calculate_statistics()

            # Print results
            self.print_results()

            # Save results
            self.save_results()

        finally:
            db.close()

    def calculate_statistics(self):
        """Calculate benchmark statistics"""
        times = self.results["embedding_times"]
        sizes = self.results["sample_sizes"]

        self.results["statistics"] = {
            "count": len(times),
            "mean_time": statistics.mean(times),
            "median_time": statistics.median(times),
            "min_time": min(times),
            "max_time": max(times),
            "stdev_time": statistics.stdev(times) if len(times) > 1 else 0,
            "p95_time": sorted(times)[int(len(times) * 0.95)] if times else 0,
            "mean_text_length": statistics.mean(sizes),
            "total_time": sum(times),

            # Projections
            "daily_volume_projection": {
                "tenders_per_day": 1500,
                "estimated_total_time_minutes": (statistics.mean(times) * 1500) / 60,
                "estimated_concurrent_tasks": (statistics.mean(times) * 1500) / 86400,  # Over 24h
            }
        }

    def print_results(self):
        """Print benchmark results"""
        stats = self.results["statistics"]

        print(f"\n{'='*60}")
        print(f"BENCHMARK RESULTS")
        print(f"{'='*60}\n")

        print(f"Model: {self.results['model_name']}")
        print(f"Model Load Time: {self.results['model_load_time']:.2f}s")
        print(f"Sample Size: {stats['count']} tenders\n")

        print(f"⏱️  Embedding Generation Times:")
        print(f"   Mean:     {stats['mean_time']:.3f}s")
        print(f"   Median:   {stats['median_time']:.3f}s")
        print(f"   Min:      {stats['min_time']:.3f}s")
        print(f"   Max:      {stats['max_time']:.3f}s")
        print(f"   Std Dev:  {stats['stdev_time']:.3f}s")
        print(f"   P95:      {stats['p95_time']:.3f}s\n")

        print(f"📊 Daily Volume Projections (1,500 tenders/day):")
        proj = stats['daily_volume_projection']
        print(f"   Total processing time: {proj['estimated_total_time_minutes']:.1f} minutes")
        print(f"   Avg concurrent tasks:  {proj['estimated_concurrent_tasks']:.1f} tasks\n")

        # Verdict
        print(f"{'='*60}")
        print(f"VERDICT:")
        print(f"{'='*60}\n")

        if stats['mean_time'] <= 5.0:
            print(f"✅ EXCELLENT: Mean time {stats['mean_time']:.2f}s is within target (<5s)")
            print(f"   Your CPU can easily handle 1,500 tenders/day.")
        elif stats['mean_time'] <= 10.0:
            print(f"⚠️  ACCEPTABLE: Mean time {stats['mean_time']:.2f}s is above target but workable")
            print(f"   Consider GPU for better performance, but CPU will work.")
        else:
            print(f"❌ SLOW: Mean time {stats['mean_time']:.2f}s is too high")
            print(f"   Recommendation: Use GPU or switch to lighter model (all-MiniLM-L6-v2)")

        print()

    def save_results(self, filename: str = None):
        """Save results to file"""
        if filename is None:
            # Save in backend directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            filename = os.path.join(script_dir, "..", "benchmark_results.json")
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"💾 Results saved to {filename}\n")


def main():
    """Run benchmark"""
    benchmark = EmbeddingBenchmark()
    benchmark.run_benchmark(num_samples=100)


if __name__ == "__main__":
    main()
