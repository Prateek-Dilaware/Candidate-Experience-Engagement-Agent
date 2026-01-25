import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000"
CANDIDATE_ID = "herofreefireop@gmail.com"

def check_server():
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def verify_candidate():
    print(f"🔍 Checking timeline for: {CANDIDATE_ID}")
    url = f"{BASE_URL}/hr/engagement/candidate/{CANDIDATE_ID}/timeline"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("\n✅ API Success! Data retrieved:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\n❌ API Failed. Status: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"\n❌ Request failed: {e}")

if __name__ == "__main__":
    if not check_server():
        print("⚠️  Server not running on port 8000. Please start it with: uv run uvicorn main:app --reload")
        sys.exit(1)
        
    verify_candidate()
