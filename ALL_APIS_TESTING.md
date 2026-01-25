# 🧪 Complete API Testing Guide

All 7 APIs are now implemented! Here's how to test each one.

## 🚀 Quick Start

1. **Start Server:**
   ```bash
   cd D:\code\Task4
   uv run uvicorn main:app --reload
   ```

2. **Server should be running on:** `http://localhost:8000`

3. **Open Swagger UI:** http://localhost:8000/docs

---

## 📋 API Testing Sequence

Test in this order for best results:

### ✅ API 1: Update Stage
### ✅ API 2: Send Status Update
### ✅ API 3: Propose Interview Slots
### ✅ API 4: Confirm Interview
### ✅ API 5: Generate Offer Letter
### ✅ API 6: Evaluate Risk
### ✅ API 7: Get Timeline

---

## 1️⃣ API 1: Update Candidate Stage

**Endpoint:** `POST /hr/engagement/stage/update`

**Purpose:** Update candidate to new stage

**Request:**
```json
{
  "candidateId": "CAND-001",
  "jobId": "JOB-101",
  "newStage": "SCREENED"
}
```

**Response (200):**
```json
{
  "candidateId": "CAND-001",
  "stage": "SCREENED",
  "stageUpdatedAt": "2026-01-25T15:30:00..."
}
```

**Test Sequence:**
```json
// 1. Create and screen
{"candidateId": "CAND-001", "jobId": "JOB-101", "newStage": "SCREENED"}

// 2. Schedule interview
{"candidateId": "CAND-001", "jobId": "JOB-101", "newStage": "INTERVIEW_SCHEDULED"}

// 3. Mark interviewed
{"candidateId": "CAND-001", "jobId": "JOB-101", "newStage": "INTERVIEWED"}

// 4. Make offer
{"candidateId": "CAND-001", "jobId": "JOB-101", "newStage": "OFFERED"}
```

---

## 2️⃣ API 2: Send Status Update

**Endpoint:** `POST /hr/engagement/status/send`

**Purpose:** Send personalized message to candidate

**Request:**
```json
{
  "candidateId": "CAND-001",
  "messageType": "stage_update",
  "channelOverride": "whatsapp"
}
```

**Response (200):**
```json
{
  "sent": true,
  "channel": "whatsapp",
  "message": "Hi Candidate, great news! Your application..."
}
```

**Message Types:**
- `stage_update`
- `reminder_24h`
- `reminder_1h`
- `offer_sent`
- `feedback_survey`
- `re_engagement`
- `closure_rejection`

**Channels:**
- `email` (default)
- `sms`
- `whatsapp`

---

## 3️⃣ API 3: Propose Interview Slots

**Endpoint:** `POST /hr/engagement/interview/propose-slots`

**Purpose:** Generate and propose interview time slots

**Request:**
```json
{
  "candidateId": "CAND-001",
  "jobId": "JOB-101",
  "interviewerEmail": "manager@company.com",
  "durationMinutes": 30,
  "window": {
    "startDate": "2026-01-27",
    "endDate": "2026-01-29"
  }
}
```

**Response (200):**
```json
{
  "status": "proposed",
  "slots": [
    "2026-01-27T10:00:00+05:30",
    "2026-01-27T11:00:00+05:30",
    "2026-01-27T15:00:00+05:30",
    "2026-01-28T10:00:00+05:30",
    "2026-01-28T11:00:00+05:30"
  ]
}
```

**Notes:**
- Automatically skips weekends
- Avoids lunch hours (13:00-14:00)
- Generates up to 10 slots
- Uses Asia/Kolkata timezone

---

## 4️⃣ API 4: Confirm Interview Slot

**Endpoint:** `POST /hr/engagement/interview/confirm`

**Purpose:** Confirm candidate's chosen slot

**Request:**
```json
{
  "candidateId": "CAND-001",
  "slot": "2026-01-27T10:00:00+05:30"
}
```

**Response (200):**
```json
{
  "status": "confirmed",
  "meetingLink": "https://meet.example.com/INT-abc12345",
  "remindersScheduled": ["24h", "1h"]
}
```

**Prerequisites:**
- Must have proposed slots first (API 3)
- Slot must be from proposed slots list

---

## 5️⃣ API 5: Generate Offer Letter

**Endpoint:** `POST /hr/engagement/offer/generate`

**Purpose:** Generate personalized offer letter

**Request:**
```json
{
  "candidateId": "CAND-001",
  "jobId": "JOB-101",
  "compensation": {
    "ctc": 1200000,
    "joiningBonus": 50000,
    "joiningDate": "2026-02-10"
  },
  "templateId": "OFFER_STD_V1"
}
```

**Response (200):**
```json
{
  "offerId": "uuid-here",
  "status": "draft",
  "offerPreview": "Dear Candidate,\n\nWe are pleased to extend an offer..."
}
```

**Business Rules:**
- Candidate must be at least INTERVIEWED stage
- Cannot generate offer for APPLIED/SCREENED candidates

**Error (400) if too early:**
```json
{
  "detail": "Offer can only be generated for candidates who have been interviewed"
}
```

---

## 6️⃣ API 6: Evaluate Candidate Risk

**Endpoint:** `POST /hr/engagement/risk/evaluate`

**Purpose:** Calculate drop-off risk score

**Request:**
```json
{
  "candidateId": "CAND-001"
}
```

**Response (200):**
```json
{
  "riskScore": 25,
  "reasons": [
    "No response in last 48 hours"
  ],
  "alertTriggered": false
}
```

**Risk Factors:**
- No response for 24h: +15 points
- No response for 48h: +25 points
- No response for 72h: +40 points
- Negative sentiment: +25 points
- Rescheduled twice: +20 points
- Missed interview: +35 points

**Alert Threshold:** Score ≥ 70

---

## 7️⃣ API 7: Get Candidate Timeline

**Endpoint:** `GET /hr/engagement/candidate/{candidateId}/timeline`

**Purpose:** Get all interactions and events

**Request:**
```
GET /hr/engagement/candidate/CAND-001/timeline
```

**Response (200):**
```json
{
  "candidateId": "CAND-001",
  "events": [
    {
      "id": "uuid",
      "type": "status_update",
      "timestamp": "2026-01-25T15:30:00...",
      "channel": "email",
      "message": "Hi Candidate, great news!...",
      "metadata": {}
    },
    {
      "id": "uuid",
      "type": "status_update",
      "timestamp": "2026-01-25T14:20:00...",
      "channel": "whatsapp",
      "message": "Your interview is scheduled...",
      "metadata": {}
    }
  ]
}
```

**Events ordered by:** Most recent first

---

## 🎯 Complete Test Flow

Test a full candidate journey:

```bash
# 1. Screen candidate
POST /hr/engagement/stage/update
{"candidateId": "CAND-TEST", "jobId": "JOB-TEST", "newStage": "SCREENED"}

# 2. Send update
POST /hr/engagement/status/send
{"candidateId": "CAND-TEST", "messageType": "stage_update"}

# 3. Move to interview stage
POST /hr/engagement/stage/update
{"candidateId": "CAND-TEST", "jobId": "JOB-TEST", "newStage": "INTERVIEW_SCHEDULED"}

# 4. Propose slots
POST /hr/engagement/interview/propose-slots
{
  "candidateId": "CAND-TEST",
  "jobId": "JOB-TEST",
  "interviewerEmail": "manager@company.com",
  "durationMinutes": 30,
  "window": {"startDate": "2026-01-27", "endDate": "2026-01-29"}
}

# 5. Confirm slot (use one from response)
POST /hr/engagement/interview/confirm
{"candidateId": "CAND-TEST", "slot": "2026-01-27T10:00:00+05:30"}

# 6. Mark as interviewed
POST /hr/engagement/stage/update
{"candidateId": "CAND-TEST", "jobId": "JOB-TEST", "newStage": "INTERVIEWED"}

# 7. Generate offer
POST /hr/engagement/offer/generate
{
  "candidateId": "CAND-TEST",
  "jobId": "JOB-TEST",
  "compensation": {"ctc": 1200000, "joiningBonus": 50000, "joiningDate": "2026-02-10"},
  "templateId": "OFFER_STD_V1"
}

# 8. Check risk
POST /hr/engagement/risk/evaluate
{"candidateId": "CAND-TEST"}

# 9. Get timeline
GET /hr/engagement/candidate/CAND-TEST/timeline
```

---

## 🗄️ Verify in Supabase

After testing, check these tables:

**candidate_pipeline:**
- See candidate's current stage

**candidate_touchpoints:**
- See all messages sent

**interview_slots:**
- See proposed and confirmed slots

**offer_letters:**
- See generated offers

**candidate_risk_signals:**
- See risk evaluations

---

## 🐛 Common Errors

### Error: "Candidate not found"
**Solution:** Create candidate first with API 1

### Error: "Cannot skip stages"
**Solution:** Progress sequentially through stages

### Error: "Offer can only be generated for interviewed candidates"
**Solution:** Update stage to INTERVIEWED first

### Error: "No proposed interview found"
**Solution:** Call propose-slots API before confirm

### Error: "Chosen slot not in proposed slots"
**Solution:** Use exact slot string from propose-slots response

---

## ✅ Success Checklist

- [ ] All 7 APIs return 200 OK
- [ ] Data appears in Supabase tables
- [ ] Console shows message sending logs
- [ ] Timeline shows all events
- [ ] Risk scores calculate correctly
- [ ] Stage validation works

---

## 📊 API Summary

| # | Endpoint | Method | Purpose |
|---|----------|--------|---------|
| 1 | `/stage/update` | POST | Update candidate stage |
| 2 | `/status/send` | POST | Send message to candidate |
| 3 | `/interview/propose-slots` | POST | Propose interview times |
| 4 | `/interview/confirm` | POST | Confirm interview slot |
| 5 | `/offer/generate` | POST | Generate offer letter |
| 6 | `/risk/evaluate` | POST | Calculate drop-off risk |
| 7 | `/candidate/{id}/timeline` | GET | Get all interactions |

---

**All APIs are ready for testing!** 🎉
