#!/usr/bin/env python3
"""
Simple test script to verify Phase 4 implementation.
Run this after starting the backend server.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def test_analytics_endpoints():
    """Test analytics API endpoints."""
    print("\n=== Testing Analytics Endpoints ===\n")

    # Test summary stats
    print("1. Testing GET /analytics/summary...")
    response = requests.get(f"{BASE_URL}/analytics/summary")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Data: {json.dumps(response.json(), indent=2)}")

    # Test volume trends
    print("\n2. Testing GET /analytics/volume-trends...")
    response = requests.get(f"{BASE_URL}/analytics/volume-trends?days=7")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Period: {data.get('period_days')} days")
        print(f"   Data points: {len(data.get('data', []))}")

    # Test category distribution
    print("\n3. Testing GET /analytics/category-distribution...")
    response = requests.get(f"{BASE_URL}/analytics/category-distribution?days=30")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Categories found: {len(data.get('data', []))}")


def test_pipeline_endpoints():
    """Test pipeline API endpoints."""
    print("\n=== Testing Pipeline Endpoints ===\n")

    # Test scrape logs
    print("1. Testing GET /pipeline/scrape-logs...")
    response = requests.get(f"{BASE_URL}/pipeline/scrape-logs?limit=5")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        logs = response.json()
        print(f"   Logs found: {len(logs)}")

    # Test staging status
    print("\n2. Testing GET /pipeline/staging-status...")
    response = requests.get(f"{BASE_URL}/pipeline/staging-status")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Data: {json.dumps(response.json(), indent=2)}")


def test_existing_endpoints():
    """Test that existing endpoints still work."""
    print("\n=== Testing Existing Endpoints ===\n")

    # Test tenders endpoint
    print("1. Testing GET /tenders...")
    response = requests.get(f"{BASE_URL}/tenders")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Tenders found: {data.get('total', 0)}")


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 4 Implementation Test")
    print("=" * 60)

    try:
        test_analytics_endpoints()
        test_pipeline_endpoints()
        test_existing_endpoints()

        print("\n" + "=" * 60)
        print("✓ All tests completed!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to backend server.")
        print("  Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
