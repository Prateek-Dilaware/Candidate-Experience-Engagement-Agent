v# 🧪 TalentFlow API Testing Guide

## 📋 Table of Contents

- [Overview](#overview)
- [Important Concepts](#important-concepts)
- [Test Data Setup](#test-data-setup)
- [Testing Tools](#testing-tools)
- [API Testing Scenarios](#api-testing-scenarios)
- [Multi-Job Application Testing](#multi-job-application-testing)
- [Advanced Testing Scenarios](#advanced-testing-scenarios)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This guide provides step-by-step instructions for testing the TalentFlow API. It includes real test data, example requests, and expected responses.

### Base URL
```
http://127.0.0.1:8080/hr/engagement
```

### Authentication
Currently, no authentication is required for testing.

---

## 💡 Important Concepts

### 🔑 Key Principle: One Candidate, Many Jobs

**A single candidate can apply for multiple jobs simultaneously.**

Each unique combination of `(candidate_id, job_id)` represents a separate application with its own:
- Recruitment stage
- Communication history (touchpoints)
- Risk score
- Interview slots
- Offer letters

#### Example Scenario:
```
Candidate: CAND001 (John Doe)
├── Application 1: JOB001 (Senior Backend Engineer) → Stage: INTERVIEWED
├── Application 2: JOB002 (DevOps Engineer)        → Stage: SCREENED
└── Application 3: JOB003 (Tech Lead)              → Stage: OFFERED
```

Each application is tracked independently in the `candidate_pipeline` table.

---

## 🗄️ Test Data Setup

### Pre-Seeded Test Data

For your convenience, the following test data has been added to the database:

#### Candidates

| candidate_id | full_name | email |
|--------------|-----------|-------|
| `CAND001` | John Doe | john.doe@example.com | - for job (JOB001)
| `CAND002` | Sarah Smith | sarah.smith@example.com | - For job (JOBOO3)
| `CAND003` | Michael Chen | michael.chen@example.com | - For job (JOB001)

#### Jobs

| job_id | title | interviewer_email |
|--------|-------|-------------------|
| `JOB001` | Senior Backend Engineer | recruiter1@company.com |
| `JOB002` | DevOps Engineer | recruiter2@company.com |
| `JOB003` | Tech Lead | recruiter3@company.com |
| `JOB004` | Frontend Developer | recruiter1@company.com |

### Pipeline Initialization

**Initial State**: All candidates start with `APPLIED` stage when first created in pipeline.

You can test with any combination:
- `CAND001` + `JOB001`
- `CAND001` + `JOB002`
- `CAND002` + `JOB003`
- etc.

---

## 🛠️ Testing Tools

### Option 1: Postman (Recommended)

1. **Import Collection**
   ```bash
   # Import postman_collection.json from project root
   ```

2. **Set Base URL**
   ```
   {{base_url}} = http://127.0.0.1:8080/hr/engagement
   ```

3. **Test Each Endpoint**
   - All endpoints are pre-configured
   - Just update candidate_id and job_id in request bodies

### Option 2: VS Code REST Client

1. **Install Extension**
   - Search "REST Client" in VS Code extensions
   - Install by Huachao Mao

2. **Open Test File**
   ```bash
   # Open api_tests.http in project root
   ```

3. **Send Requests**
   - Click "Send Request" above each endpoint

### Option 3: API Visualizer (Interactive UI)

```
http://127.0.0.1:8080/static/visualizer.html
```

- Web-based interface
- Test all endpoints with forms
- See real-time responses

### Option 4: cURL (Command Line)

```bash
# Example: Get metadata
curl http://127.0.0.1:8080/hr/engagement/metadata
```

---

## 📡 API Testing Scenarios

### Scenario 1: Complete Recruitment Flow (Single Job)

Test the full lifecycle for one candidate applying to one job.

#### Step 1: Get Metadata
**Purpose**: Verify available candidates, jobs, and stages

```http
GET http://127.0.0.1:8080/hr/engagement/metadata
```

**Expected Response**:
```json
{
  "candidates": [
    {
      "candidate_id": "CAND001",
      "full_name": "John Doe",
      "email": "john.doe@example.com"
    }
  ],
  "jobs": [
    {
      "job_id": "JOB001",
      "title": "Senior Backend Engineer"
    }
  ],
  "stages": [
    "APPLIED",
    "SCREENED",
    "INTERVIEW_SCHEDULED",
    "INTERVIEWED",
    "OFFERED"
  ],
  "message_types": [
    "stage_update",
    "reminder_24h"
  ]
}
```

---

#### Step 2: Check Pipeline Status
**Purpose**: See current stage and preferences

```http
GET http://127.0.0.1:8080/hr/engagement/candidate/CAND001/job/JOB001/pipeline
```

**Expected Response (First Time)**:
```json
{
  "candidate_id": "CAND001",
  "job_id": "JOB001",
  "stage": "APPLIED",
  "stage_updated_at": "2026-01-27T10:00:00Z",
  "preferred_channel": "email",
  "timezone": "Asia/Kolkata"
}
```

**Note**: If no pipeline record exists, you'll get an error. Create one using Stage Update API.

---

#### Step 3: Update Stage to SCREENED
**Purpose**: Move candidate to next stage + send notification

```http
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "newStage": "SCREENED"
}
```

**Expected Response**:
```json
{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "stage": "SCREENED",
  "stageUpdatedAt": "2026-01-27T10:15:00Z"
}
```

**What Happens**:
1. ✅ Database updated: stage = "SCREENED"
2. ✅ AI generates personalized message
3. ✅ Email sent to john.doe@example.com
4. ✅ Touchpoint recorded in audit log

---

#### Step 4: Send Custom Status Update
**Purpose**: Send additional message (reminder, update, etc.)

```http
POST http://127.0.0.1:8080/hr/engagement/status/send
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "messageType": "REMINDER_24H",
  "channelOverride": "sms"
}
```

**Expected Response**:
```json
{
  "sent": true,
  "channel": "sms",
  "message": "Hi John! Reminder: Your interview for Senior Backend Engineer is tomorrow at 10 AM. See you then! - TalentFlow"
}
```

**Check Mock Log**:
```bash
cat mock_sms.txt
```

---

#### Step 5: Update Stage to INTERVIEW_SCHEDULED
**Purpose**: Move to next stage

```http
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "newStage": "INTERVIEW_SCHEDULED"
}
```

---

#### Step 6: Propose Interview Slots
**Purpose**: Generate available time slots

```http
POST http://127.0.0.1:8080/hr/engagement/interview/propose-slots
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "date": "2026-02-05"
}
```

**Expected Response**:
```json
{
  "status": "proposed",
  "slots": [
    "2026-02-05T10:00:00Z",
    "2026-02-05T14:00:00Z",
    "2026-02-05T16:00:00Z"
  ]
}
```

---

#### Step 7: Confirm Interview Slot
**Purpose**: Book the interview

```http
POST http://127.0.0.1:8080/hr/engagement/interview/confirm
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "chosenSlot": "2026-02-05T10:00:00Z"
}
```

**Expected Response**:
```json
{
  "status": "confirmed",
  "meetingLink": "https://meet.google.com/abc-defg-hij",
  "remindersScheduled": ["24h", "1h"]
}
```

---

#### Step 8: Update Stage to INTERVIEWED
**Purpose**: Mark interview as completed

```http
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "newStage": "INTERVIEWED"
}
```

**Expected Email Message**:
```
Subject: Interview Feedback - Senior Backend Engineer

Dear John Doe,

Thank you for taking the time to interview with us for the 
Senior Backend Engineer position. We were impressed by your 
technical skills and experience. Our team is currently 
reviewing your interview performance, and we will share 
feedback within the next 2-3 business days.

Best regards,
TalentFlow Recruiting Team
```

---

#### Step 9: Evaluate Risk Score
**Purpose**: Check if candidate might drop out

```http
POST http://127.0.0.1:8080/hr/engagement/risk/evaluate
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB001"
}
```

**Expected Response**:
```json
{
  "riskScore": 15,
  "reasons": [
    "No response for 24 hours"
  ],
  "alertTriggered": false
}
```

**Risk Score Breakdown**:
- 0-30: Low risk ✅
- 31-69: Medium risk ⚠️
- 70+: High risk 🚨 (Alert triggered)

---

#### Step 10: Update Stage to OFFERED
**Purpose**: Make offer to candidate

```http
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "newStage": "OFFERED"
}
```

---

#### Step 11: Generate Offer Letter
**Purpose**: Create formal offer document

```http
POST http://127.0.0.1:8080/hr/engagement/offer/generate
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "joiningDate": "2026-03-01"
}
```

**Expected Response**:
```json
{
  "offerId": "OFF_CAND001_JOB001",
  "status": "draft",
  "offerPreview": "Dear John Doe,\n\nWe are pleased to offer you the position of Senior Backend Engineer...\n\nJoining Date: March 1, 2026\n\nBest regards,\nTalentFlow"
}
```

---

#### Step 12: View Complete Timeline
**Purpose**: See all interactions with candidate

```http
GET http://127.0.0.1:8080/hr/engagement/candidate/CAND001/job/JOB001/timeline
```

**Expected Response**:
```json
{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "events": [
    {
      "id": "uuid-1",
      "type": "status_update",
      "timestamp": "2026-01-27T10:15:00Z",
      "stage": "SCREENED",
      "channel": "email",
      "message": "Hi John, your application has been screened..."
    },
    {
      "id": "uuid-2",
      "type": "notification",
      "timestamp": "2026-01-27T10:20:00Z",
      "stage": "SCREENED",
      "channel": "sms",
      "message": "Hi John! Reminder: Your interview..."
    },
    {
      "id": "uuid-3",
      "type": "status_update",
      "timestamp": "2026-01-27T10:45:00Z",
      "stage": "INTERVIEWED",
      "channel": "email",
      "message": "Dear John Doe, thank you for interviewing..."
    }
  ]
}
```

---

## 🎯 Multi-Job Application Testing

### Scenario 2: One Candidate, Multiple Jobs

**Test Case**: CAND001 (John Doe) applies for 3 different positions

#### Job Applications Overview

| Application | Job | Initial Stage | Target Stage |
|-------------|-----|---------------|--------------|
| Application #1 | JOB001 (Backend Engineer) | APPLIED | OFFERED |
| Application #2 | JOB002 (DevOps Engineer) | APPLIED | INTERVIEWED |
| Application #3 | JOB003 (Tech Lead) | APPLIED | SCREENED |

---

### Application #1: Backend Engineer (Full Journey)

#### Create Pipeline Entry
```http
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "newStage": "APPLIED"
}
```

#### Progress Through Stages
```http
# Move to SCREENED
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "newStage": "SCREENED"
}

# Move to INTERVIEW_SCHEDULED
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "newStage": "INTERVIEW_SCHEDULED"
}

# Move to INTERVIEWED
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "newStage": "INTERVIEWED"
}

# Move to OFFERED
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "newStage": "OFFERED"
}
```

#### Generate Offer
```http
POST http://127.0.0.1:8080/hr/engagement/offer/generate
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "joiningDate": "2026-03-15"
}
```

---

### Application #2: DevOps Engineer (Partial Journey)

#### Create & Progress
```http
# Initial application
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB002",
  "newStage": "APPLIED"
}

# Screen candidate
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB002",
  "newStage": "SCREENED"
}

# Schedule interview
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB002",
  "newStage": "INTERVIEW_SCHEDULED"
}

# Complete interview
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB002",
  "newStage": "INTERVIEWED"
}
```

#### Propose Interview Slots
```http
POST http://127.0.0.1:8080/hr/engagement/interview/propose-slots
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB002",
  "date": "2026-02-10"
}
```

---

### Application #3: Tech Lead (Early Stage)

#### Create & Screen Only
```http
# Initial application
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB003",
  "newStage": "APPLIED"
}

# Screen candidate
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB003",
  "newStage": "SCREENED"
}
```

#### Send Custom Message (WhatsApp)
```http
POST http://127.0.0.1:8080/hr/engagement/status/send
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB003",
  "messageType": "STAGE_UPDATE",
  "channelOverride": "whatsapp"
}
```

**Check Message**:
```bash
cat mock_whatsapp.txt
```

---

### Verify All Applications

#### Check Each Pipeline Status

**Application #1 (JOB001)**:
```http
GET http://127.0.0.1:8080/hr/engagement/candidate/CAND001/job/JOB001/pipeline
```
**Expected**: `stage: "OFFERED"`

**Application #2 (JOB002)**:
```http
GET http://127.0.0.1:8080/hr/engagement/candidate/CAND001/job/JOB002/pipeline
```
**Expected**: `stage: "INTERVIEWED"`

**Application #3 (JOB003)**:
```http
GET http://127.0.0.1:8080/hr/engagement/candidate/CAND001/job/JOB003/pipeline
```
**Expected**: `stage: "SCREENED"`

#### View Timelines

```http
# Timeline for JOB001
GET http://127.0.0.1:8080/hr/engagement/candidate/CAND001/job/JOB001/timeline

# Timeline for JOB002
GET http://127.0.0.1:8080/hr/engagement/candidate/CAND001/job/JOB002/timeline

# Timeline for JOB003
GET http://127.0.0.1:8080/hr/engagement/candidate/CAND001/job/JOB003/timeline
```

**Result**: Each timeline shows only events for that specific job application.

---

## 🧪 Advanced Testing Scenarios

### Scenario 3: Multi-Channel Messaging Test

Test the same stage update across different channels.

#### Email Channel (Default)
```http
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND002",
  "jobId": "JOB001",
  "newStage": "SCREENED"
}
```
**Result**: Formal email sent (150 words max)

#### SMS Override
```http
POST http://127.0.0.1:8080/hr/engagement/status/send
Content-Type: application/json

{
  "candidateId": "CAND002",
  "jobId": "JOB001",
  "messageType": "STAGE_UPDATE",
  "channelOverride": "sms"
}
```
**Result**: Concise SMS (40 words max) in `mock_sms.txt`

#### WhatsApp Override
```http
POST http://127.0.0.1:8080/hr/engagement/status/send
Content-Type: application/json

{
  "candidateId": "CAND002",
  "jobId": "JOB001",
  "messageType": "STAGE_UPDATE",
  "channelOverride": "whatsapp"
}
```
**Result**: Conversational message (60 words max) in `mock_whatsapp.txt`

---

### Scenario 4: Risk Score Escalation

Simulate high-risk candidate behavior.

#### Setup: Create Application
```http
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND003",
  "jobId": "JOB002",
  "newStage": "INTERVIEWED"
}
```

#### Evaluate Risk (Initial)
```http
POST http://127.0.0.1:8080/hr/engagement/risk/evaluate
Content-Type: application/json

{
  "candidateId": "CAND003",
  "jobId": "JOB002"
}
```
**Expected**: `riskScore: 0` (no issues yet)

#### Simulate Response Gap
**Manually in Database** (or wait 72 hours):
- Update `stage_updated_at` to be 72 hours ago
- Add negative sentiment touchpoint

#### Re-evaluate Risk
```http
POST http://127.0.0.1:8080/hr/engagement/risk/evaluate
Content-Type: application/json

{
  "candidateId": "CAND003",
  "jobId": "JOB002"
}
```
**Expected**:
```json
{
  "riskScore": 75,
  "reasons": [
    "No response for 72 hours",
    "Negative sentiment detected",
    "Rescheduled interview twice"
  ],
  "alertTriggered": true
}
```

---

### Scenario 5: Stage Validation Testing

Test invalid stage transitions.

#### Valid Transition (Sequential)
```http
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB004",
  "newStage": "APPLIED"
}

# Then immediately to SCREENED ✅
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB004",
  "newStage": "SCREENED"
}
```
**Result**: Success

#### Invalid Transition (Skip Stage)
```http
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB004",
  "newStage": "OFFERED"
}
```
**Result**: Error
```json
{
  "detail": "Cannot skip from SCREENED to OFFERED"
}
```

#### Invalid Transition (Backwards)
```http
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB004",
  "newStage": "APPLIED"
}
```
**Result**: Error
```json
{
  "detail": "Cannot move backwards from SCREENED to APPLIED"
}
```

---

## 📊 Testing Checklist

### Basic Flow ✅
- [ ] Get metadata (candidates, jobs, stages)
- [ ] Check pipeline status
- [ ] Update stage (APPLIED → SCREENED)
- [ ] Send custom message
- [ ] View timeline

### Interview Flow ✅
- [ ] Propose interview slots
- [ ] Confirm interview slot
- [ ] Update to INTERVIEWED stage

### Offer Flow ✅
- [ ] Update to OFFERED stage
- [ ] Generate offer letter

### Risk Management ✅
- [ ] Evaluate risk score (low risk)
- [ ] Test high-risk scenario
- [ ] Verify alert triggered

### Multi-Job Testing ✅
- [ ] Create 3+ applications for same candidate
- [ ] Progress each to different stages
- [ ] Verify independent tracking
- [ ] Check separate timelines

### Channel Testing ✅
- [ ] Send email (default)
- [ ] Send SMS (override)
- [ ] Send WhatsApp (override)
- [ ] Verify mock logs

### Validation Testing ✅
- [ ] Test valid sequential stage progression
- [ ] Test invalid stage skip
- [ ] Test invalid backward transition
- [ ] Test closed stage restrictions

---

## 🐛 Troubleshooting

### Error: "Candidate profile not found"

**Cause**: candidate_id doesn't exist in `candidate_profiles` table


### Error: "Candidate pipeline record not found"

**Cause**: No entry in `candidate_pipeline` for this (candidate_id, job_id) pair

**Solution**: Create pipeline entry first:
```http
POST http://127.0.0.1:8080/hr/engagement/stage/update
Content-Type: application/json

{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "newStage": "APPLIED"
}
```

### Email Not Sending

**Cause**: SMTP configuration issue

**Check**:
1. Verify `.env` file:
   ```env
   SMTP_EMAIL=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   ```
2. Ensure Gmail app password is correct (not your regular password)
3. Check server logs for SMTP errors

### Mock Files Not Created

**Cause**: File system permissions

**Solution**:
```bash
# Check if files exist
ls -la mock_*.txt

# Create manually if needed
touch mock_sms.txt mock_whatsapp.txt
chmod 644 mock_*.txt
```

### AI Message Generation Slow

**Cause**: Gemini API latency

**Expected**: 1-3 seconds for message generation

**Fallback**: System uses hardcoded message if AI fails

---

## 📝 Quick Reference Card

### Test Data Quick Copy-Paste

```json
// Candidate IDs
"CAND001"  // John Doe
"CAND002"  // Sarah Smith
"CAND003"  // Michael Chen

// Job IDs
"JOB001"   // Senior Backend Engineer
"JOB002"   // DevOps Engineer
"JOB003"   // Tech Lead
"JOB004"   // Frontend Developer

// Valid Stages (in order)
"APPLIED"
"SCREENED"
"INTERVIEW_SCHEDULED"
"INTERVIEWED"
"OFFERED"
"OFFER_ACCEPTED"
"ONBOARDING"

// Closed Stages
"CLOSED_REJECTED"
"CLOSED_WITHDRAWN"

// Channels
"email"
"sms"
"whatsapp"

// Message Types
"STAGE_UPDATE"
"REMINDER_24H"
"REMINDER_1H"
"OFFER_SENT"
"FEEDBACK_SURVEY"
```



## 📧 Test Credentials

**For Email Testing** (modify in `.env`):
```env
SMTP_EMAIL=your_test_email@gmail.com
SMTP_PASSWORD=your_app_password
```

**Recommendation**: Create a dedicated Gmail account for testing to avoid mixing with personal emails.

---

## 🚀 Quick Start Testing Script

```bash
# 1. Start server
uv run uvicorn main:app --reload

# 2. Open new terminal and test
curl http://127.0.0.1:8080/health

# 3. Get metadata
curl http://127.0.0.1:8080/hr/engagement/metadata

# 4. Create first application
curl -X POST http://127.0.0.1:8080/hr/engagement/stage/update \
  -H "Content-Type: application/json" \
  -d '{"candidateId":"CAND001","jobId":"JOB001","newStage":"APPLIED"}'

# 5. Progress to SCREENED
curl -X POST http://127.0.0.1:8080/hr/engagement/stage/update \
  -H "Content-Type: application/json" \
  -d '{"candidateId":"CAND001","jobId":"JOB001","newStage":"SCREENED"}'

# 6. Check timeline
curl http://127.0.0.1:8080/hr/engagement/candidate/CAND001/job/JOB001/timeline
```

---

