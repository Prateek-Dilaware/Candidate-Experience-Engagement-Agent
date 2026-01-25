# 🚀 Quick Reference Card - All APIs

## Server Info
- **URL:** http://localhost:8000
- **Swagger:** http://localhost:8000/docs
- **Start:** `uv run uvicorn main:app --reload`

---

## 📋 All 7 APIs (Quick Copy-Paste)

### 1. Update Stage
```json
POST /hr/engagement/stage/update
{
  "candidateId": "CAND-001",
  "jobId": "JOB-101",
  "newStage": "SCREENED"
}
```

### 2. Send Status
```json
POST /hr/engagement/status/send
{
  "candidateId": "CAND-001",
  "messageType": "stage_update",
  "channelOverride": "email"
}
```

### 3. Propose Slots
```json
POST /hr/engagement/interview/propose-slots
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

### 4. Confirm Interview
```json
POST /hr/engagement/interview/confirm
{
  "candidateId": "CAND-001",
  "slot": "2026-01-27T10:00:00+05:30"
}
```

### 5. Generate Offer
```json
POST /hr/engagement/offer/generate
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

### 6. Evaluate Risk
```json
POST /hr/engagement/risk/evaluate
{
  "candidateId": "CAND-001"
}
```

### 7. Get Timeline
```
GET /hr/engagement/candidate/CAND-001/timeline
```

---

## 🎯 Valid Stage Values
- APPLIED
- SCREENED
- INTERVIEW_SCHEDULED
- INTERVIEWED
- OFFERED
- OFFER_ACCEPTED
- ONBOARDING
- CLOSED_REJECTED
- CLOSED_WITHDRAWN

---

## 📢 Message Types
- stage_update
- reminder_24h
- reminder_1h
- offer_sent
- feedback_survey
- re_engagement
- closure_rejection

---

## 📱 Channels
- email
- sms
- whatsapp

---

## ✅ Full Journey Test
```bash
# Use candidateId: CAND-FULL-TEST

1. POST /stage/update → SCREENED
2. POST /status/send → Send notification
3. POST /stage/update → INTERVIEW_SCHEDULED
4. POST /interview/propose-slots → Get slots
5. POST /interview/confirm → Confirm slot
6. POST /stage/update → INTERVIEWED
7. POST /offer/generate → Create offer
8. POST /risk/evaluate → Check risk
9. GET /candidate/CAND-FULL-TEST/timeline → View all events
```

---

## 🗄️ Database Tables
- candidate_pipeline
- candidate_touchpoints
- interview_slots
- offer_letters
- candidate_risk_signals

---

## 🔥 Quick Checks
```bash
# Health check
curl http://localhost:8000/health

# Test stage update
curl -X POST http://localhost:8000/hr/engagement/stage/update \
  -H "Content-Type: application/json" \
  -d '{"candidateId":"TEST","jobId":"JOB","newStage":"SCREENED"}'
```

---

**All systems ready!** 🎉
