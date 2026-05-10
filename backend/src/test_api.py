import requests
import json

BASE_URL = "http://127.0.0.1:8080"

def test_app():
    print("--- 1. Setup Admin ---")
    resp = requests.post(f"{BASE_URL}/auth/setup-first-user")
    print(resp.json())

    print("\n--- 2. Login ---")
    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin@acme.com", "password": "admin123"})
    token_data = resp.json()
    if "access_token" not in token_data:
        print("Login failed!")
        return
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Token OK")

    print("\n--- 3. Public ML Endpoints ---")
    resp = requests.get(f"{BASE_URL}/ml/segments")
    print(f"Segments: {len(resp.json())} items found")
    
    resp = requests.get(f"{BASE_URL}/ml/metrics")
    print(f"Metrics: {resp.json()}")

    print("\n--- 4. Protected Analytics Endpoints ---")
    resp = requests.get(f"{BASE_URL}/analytics/summary", headers=headers)
    print(f"Summary: {resp.json()}")

    resp = requests.get(f"{BASE_URL}/analytics/revenue-trend?granularity=month", headers=headers)
    print(f"Trend: {len(resp.json())} data points")

    print("\n--- 5. Test AI Suggest (if API key present) ---")
    resp = requests.post(f"{BASE_URL}/analytics/suggest-rules?lang=fr", headers=headers)
    print(f"Suggest Rules: {resp.json()}")

    print("\n--- 6. Get Rules ---")
    resp = requests.get(f"{BASE_URL}/analytics/rules?lang=fr", headers=headers)
    rules = resp.json()
    print(f"Rules: {len(rules)} found")
    for r in rules[:2]:
        print(f" - {r['name']}: {r['description'][:50]}...")

    print("\n--- 7. Health Check ---")
    resp = requests.get(f"{BASE_URL}/health")
    print(f"Health: {resp.json()}")

if __name__ == "__main__":
    test_app()
