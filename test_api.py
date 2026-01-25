"""Test script for Candidate Engagement API."""
import requests
import json

# API endpoint
BASE_URL = "http://localhost:8080"

def test_update_stage():
    """Test the update stage API."""
    url = f"{BASE_URL}/hr/engagement/stage/update"
    
    payload = {
        "candidateId": "CAND-001",
        "jobId": "JOB-101",
        "newStage": "SCREENED"
    }
    
    print("🚀 Testing Stage Update API...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    response = requests.post(url, json=payload)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Success!")
    else:
        print("❌ Failed!")
    
    return response

def test_stage_progression():
    """Test complete stage progression."""
    stages = [
        "SCREENED",
        "INTERVIEW_SCHEDULED",
        "INTERVIEWED",
        "OFFERED",
        "OFFER_ACCEPTED",
        "ONBOARDING"
    ]
    
    print("\n🎯 Testing Stage Progression...")
    print("=" * 50)
    
    for stage in stages:
        print(f"\n→ Moving to: {stage}")
        
        payload = {
            "candidateId": "CAND-002",
            "jobId": "JOB-102",
            "newStage": stage
        }
        
        response = requests.post(
            f"{BASE_URL}/hr/engagement/stage/update",
            json=payload
        )
        
        if response.status_code == 200:
            print(f"  ✅ Success! Now at: {response.json()['stage']}")
        else:
            print(f"  ❌ Failed: {response.json()}")
            break

def test_invalid_transition():
    """Test invalid stage transition (should fail)."""
    print("\n⚠️  Testing Invalid Transition (Should Fail)...")
    print("=" * 50)
    
    # First, create candidate at SCREENED
    requests.post(
        f"{BASE_URL}/hr/engagement/stage/update",
        json={
            "candidateId": "CAND-003",
            "jobId": "JOB-103",
            "newStage": "SCREENED"
        }
    )
    
    # Try to skip to OFFERED (should fail)
    print("\nTrying to skip from SCREENED → OFFERED...")
    response = requests.post(
        f"{BASE_URL}/hr/engagement/stage/update",
        json={
            "candidateId": "CAND-003",
            "jobId": "JOB-103",
            "newStage": "OFFERED"
        }
    )
    
    if response.status_code == 400:
        print(f"✅ Correctly rejected! Error: {response.json()['detail']}")
    else:
        print(f"❌ Should have been rejected but wasn't!")

def test_health_check():
    """Test health check endpoints."""
    print("\n🏥 Testing Health Check...")
    print("=" * 50)
    
    # Root endpoint
    response = requests.get(f"{BASE_URL}/")
    print(f"Root: {response.json()}")
    
    # Health endpoint
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health: {response.json()}")

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 CANDIDATE ENGAGEMENT API - TEST SUITE")
    print("=" * 50)
    
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except requests.exceptions.RequestException:
        print("\n❌ ERROR: Server is not running!")
        print("Please start the server with: uv run uvicorn main:app --reload")
        exit(1)
    
    # Run tests
    test_health_check()
    test_update_stage()
    test_stage_progression()
    test_invalid_transition()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("=" * 50)
