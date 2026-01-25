# Testing Guide for Candidate Engagement API

## Prerequisites

1. **Install dependencies:**
```bash
pip install -e .
```

2. **Configure environment:**
Create `.env` file with your credentials:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
GOOGLE_API_KEY=your_gemini_api_key
```

3. **Setup database:**
Run `supabase_schema.sql` in your Supabase SQL Editor

4. **Start the server:**
```bash
uv run uvicorn main:app --reload
```

Server runs at: `http://localhost:8080`

---

## API 1: Update Candidate Stage ✅ IMPLEMENTED

### Endpoint
```
POST http://localhost:8080/hr/engagement/stage/update
```

### Test Case 1: Create New Candidate (Applied → Screened)

**Request:**
```json
{
  "candidateId": "CAND-001",
  "jobId": "JOB-101",
  "newStage": "SCREENED"
}
```

**Expected Response:**
```json
{
  "candidateId": "CAND-001",
  "stage": "SCREENED",
  "stageUpdatedAt": "2026-01-24T10:30:00.000Z"
}
```

**What happens:**
- Creates candidate record with APPLIED stage
- Updates to SCREENED stage
- Sends notification via preferred channel (email by default)
- Records touchpoint in database

---

### Test Case 2: Sequential Stage Progression (Screened → Interview Scheduled)

**Request:**
```json
{
  "candidateId": "CAND-001",
  "jobId": "JOB-101",
  "newStage": "INTERVIEW_SCHEDULED"
}
```

**Expected Response:**
```json
{
  "candidateId": "CAND-001",
  "stage": "INTERVIEW_SCHEDULED",
  "stageUpdatedAt": "2026-01-24T10:35:00.000Z"
}
```

---

### Test Case 3: Invalid Transition (Should Fail)

**Request:**
```json
{
  "candidateId": "CAND-001",
  "jobId": "JOB-101",
  "newStage": "OFFERED"
}
```

**Expected Response:** ❌ Error 400
```json
{
  "detail": "Failed to update candidate stage: Cannot skip from INTERVIEW_SCHEDULED to OFFERED. Must progress sequentially."
}
```

---

### Test Case 4: Move to Closed Stage (Always Allowed)

**Request:**
```json
{
  "candidateId": "CAND-001",
  "jobId": "JOB-101",
  "newStage": "CLOSED_REJECTED"
}
```

**Expected Response:**
```json
{
  "candidateId": "CAND-001",
  "stage": "CLOSED_REJECTED",
  "stageUpdatedAt": "2026-01-24T10:40:00.000Z"
}
```

---

### Test Case 5: Cannot Move from Closed Stage (Should Fail)

**Request:**
```json
{
  "candidateId": "CAND-001",
  "jobId": "JOB-101",
  "newStage": "INTERVIEWED"
}
```

**Expected Response:** ❌ Error 400
```json
{
  "detail": "Failed to update candidate stage: Cannot transition from closed stage: CLOSED_REJECTED"
}
```

---

## Complete Test Flow

### Full Candidate Journey

```bash
# 1. Applied → Screened
POST /hr/engagement/stage/update
{"candidateId": "CAND-002", "jobId": "JOB-102", "newStage": "SCREENED"}

# 2. Screened → Interview Scheduled
POST /hr/engagement/stage/update
{"candidateId": "CAND-002", "jobId": "JOB-102", "newStage": "INTERVIEW_SCHEDULED"}

# 3. Interview Scheduled → Interviewed
POST /hr/engagement/stage/update
{"candidateId": "CAND-002", "jobId": "JOB-102", "newStage": "INTERVIEWED"}

# 4. Interviewed → Offered
POST /hr/engagement/stage/update
{"candidateId": "CAND-002", "jobId": "JOB-102", "newStage": "OFFERED"}

# 5. Offered → Offer Accepted
POST /hr/engagement/stage/update
{"candidateId": "CAND-002", "jobId": "JOB-102", "newStage": "OFFER_ACCEPTED"}

# 6. Offer Accepted → Onboarding
POST /hr/engagement/stage/update
{"candidateId": "CAND-002", "jobId": "JOB-102", "newStage": "ONBOARDING"}
```

---

## Verify in Database

### Check Candidate Pipeline
```sql
SELECT * FROM candidate_pipeline WHERE candidate_id = 'CAND-001';
```

### Check Touchpoints (All Communications)
```sql
SELECT * FROM candidate_touchpoints 
WHERE candidate_id = 'CAND-001' 
ORDER BY created_at DESC;
```

---

## Using cURL

```bash
# Update stage
curl -X POST http://localhost:8080/hr/engagement/stage/update \
  -H "Content-Type: application/json" \
  -d '{
    "candidateId": "CAND-001",
    "jobId": "JOB-101",
    "newStage": "SCREENED"
  }'

# Health check
curl http://localhost:8080/health
```

---

## Using Python Requests

```python
import requests

url = "http://localhost:8080/hr/engagement/stage/update"
payload = {
    "candidateId": "CAND-003",
    "jobId": "JOB-103",
    "newStage": "SCREENED"
}

response = requests.post(url, json=payload)
print(response.json())
```

---

## Console Output

When you run the API, you'll see console logs like:

```
📤 [EMAIL] Sending to CAND-001: Hi Candidate, great news! Your application for Sof...
INFO:     127.0.0.1:50234 - "POST /hr/engagement/stage/update HTTP/1.1" 200 OK
```

---

## Next Steps

Once API 1 is working:
- ✅ API 2: Send Status Update
- ✅ API 3: Propose Interview Slots
- ✅ API 4: Confirm Interview
- ✅ API 5: Generate Offer Letter
- ✅ API 6: Evaluate Risk
- ✅ API 7: Get Timeline
