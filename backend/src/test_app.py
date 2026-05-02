import requests
import json

BASE_URL = "http://localhost:8082"

def test_health():
    print("Testing /health...")
    r = requests.get(f"{BASE_URL}/health")
    print(f"Status: {r.status_code}, Body: {r.json()}")

def test_recommendations():
    print("\nTesting /ml/recommendations/user_1...")
    # user_1 might not exist, but recommender has a fallback
    r = requests.get(f"{BASE_URL}/ml/recommendations/user_1")
    print(f"Status: {r.status_code}, Body: {r.json()}")

def test_conversions():
    print("\nTesting /analytics/conversions...")
    # This requires an API Key because of get_current_user dependency?
    # Let's check analytics.py again.
    r = requests.get(f"{BASE_URL}/analytics/conversions")
    print(f"Status: {r.status_code}, Body: {r.text[:200]}...")

def test_trigger():
    print("\nTesting /ml/recommendations/trigger...")
    payload = {"user_id": "user_1", "feature": "dashboard"}
    r = requests.post(f"{BASE_URL}/ml/recommendations/trigger", json=payload)
    print(f"Status: {r.status_code}, Body: {r.json()}")

if __name__ == "__main__":
    test_health()
    test_recommendations()
    test_trigger()
    # test_conversions() # Might fail without auth
