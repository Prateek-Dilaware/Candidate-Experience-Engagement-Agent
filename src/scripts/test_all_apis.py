import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://127.0.0.1:8000"
CANDIDATE_ID = f"test_cand_{int(time.time())}@example.com"
print(f"USING CANDIDATE ID: {CANDIDATE_ID}")
JOB_ID = "JOB-2025-001"
INTERVIEWER_EMAIL = "manager@example.com"

# Helpers
def print_step(title):
    print(f"\n{'-'*50}")
    print(f"| {title}")
    print(f"{'-'*50}")

def print_response(res):
    if res.status_code in [200, 201]:
        print(f"SUCCESS ({res.status_code})")
        try:
            print(json.dumps(res.json(), indent=2))
        except:
            print(res.text)
    else:
        print(f"FAILED ({res.status_code})")
        print(res.text)
        # Exit on critical failures to avoid cascading errors
        if res.status_code >= 400:
             # We might want to continue for some tests, but generally block is better for sequentially dependent steps
             pass 

def pause():
    time.sleep(1)

def main():
    print(f"Starting Comprehensive API Test for {CANDIDATE_ID}...")
    
    # 1. Update Candidate Stage -> SCREENED
    print_step("1. API: Update Stage (SCREENED)")
    payload = {
        "candidateId": CANDIDATE_ID,
        "jobId": JOB_ID,
        "newStage": "SCREENED"
    }
    res = requests.post(f"{BASE_URL}/hr/engagement/stage/update", json=payload, timeout=120)
    print_response(res)
    pause()

    # 2. Send Status Update
    print_step("2. API: Send Status Update")
    payload = {
        "candidateId": CANDIDATE_ID,
        "messageType": "stage_update",
        "channelOverride": "email"
    }
    res = requests.post(f"{BASE_URL}/hr/engagement/status/send", json=payload, timeout=120)
    print_response(res)
    pause()

    # 3. Update Stage -> INTERVIEW_SCHEDULED
    print_step("3a. Prerequisite: Update Stage (INTERVIEW_SCHEDULED)")
    payload = {
        "candidateId": CANDIDATE_ID,
        "jobId": JOB_ID,
        "newStage": "INTERVIEW_SCHEDULED"
    }
    res = requests.post(f"{BASE_URL}/hr/engagement/stage/update", json=payload, timeout=120)
    print_response(res)
    pause()

    # 4. Propose Interview Slots
    print_step("3. API: Propose Interview Slots")
    start_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
    
    payload = {
        "candidateId": CANDIDATE_ID,
        "jobId": JOB_ID,
        "interviewerEmail": INTERVIEWER_EMAIL,
        "durationMinutes": 30,
        "window": {
            "startDate": start_date,
            "endDate": end_date
        }
    }
    res = requests.post(f"{BASE_URL}/hr/engagement/interview/propose-slots", json=payload, timeout=120)
    print_response(res)
    
    # Capture a slot for confirmation
    chosen_slot = None
    if res.status_code == 200:
        data = res.json()
        if "slots" in data and len(data["slots"]) > 0:
            chosen_slot = data["slots"][0]
            print(f"Selected slot for confirmation: {chosen_slot}")
    pause()

    # 5. Confirm Interview Slot
    print_step("4. API: Confirm Interview")
    if chosen_slot:
        payload = {
            "candidateId": CANDIDATE_ID,
            "slot": chosen_slot
        }
        res = requests.post(f"{BASE_URL}/hr/engagement/interview/confirm", json=payload, timeout=120)
        print_response(res)
    else:
        print("Skipping confirmation (no slot obtained)")
    pause()

    # 6. Update Stage -> INTERVIEWED
    print_step("5a. Prerequisite: Update Stage (INTERVIEWED)")
    payload = {
        "candidateId": CANDIDATE_ID,
        "jobId": JOB_ID,
        "newStage": "INTERVIEWED"
    }
    res = requests.post(f"{BASE_URL}/hr/engagement/stage/update", json=payload, timeout=120)
    print_response(res)
    pause()

    # 7. Generate Offer Letter
    print_step("5. API: Generate Offer Letter")
    payload = {
        "candidateId": CANDIDATE_ID,
        "jobId": JOB_ID,
        "compensation": {
            "ctc": 1500000,
            "joiningBonus": 100000,
            "joiningDate": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        },
        "templateId": "OFFER_STD_V1"
    }
    res = requests.post(f"{BASE_URL}/hr/engagement/offer/generate", json=payload, timeout=120)
    print_response(res)
    pause()

    # 8. Evaluate Risk
    print_step("6. API: Evaluate Risk")
    payload = {
        "candidateId": CANDIDATE_ID
    }
    res = requests.post(f"{BASE_URL}/hr/engagement/risk/evaluate", json=payload, timeout=120)
    print_response(res)
    pause()

    # 9. Get Timeline
    print_step("7. API: Get Timeline")
    res = requests.get(f"{BASE_URL}/hr/engagement/candidate/{CANDIDATE_ID}/timeline", timeout=120)
    print_response(res)
    pause()

    print("\nTest Sequence Complete!")

if __name__ == "__main__":
    main()
