# 📄 CURRENT PROJECT STATE & PROGRESS

## 1. Project Name

**Candidate Experience & Engagement Agent (Python Version)**

---

## 2. Original Task Summary

The goal of this project is to build a **Candidate Engagement & Workflow System** that manages a candidate’s journey after they are already in the hiring pipeline.

The system:

* Tracks candidate stages
* Sends personalized messages
* Schedules interviews
* Generates offer letters
* Detects drop-off risk
* Alerts recruiters

This is a **post-selection workflow system**, not a resume screening or skill-matching system.

---

## 3. Technology Stack (Converted to Python)

Original task suggested:

* Node.js + Express
* LangGraph JS

We have converted it to:

* **Python**
* **FastAPI** (for APIs)
* **Supabase (PostgreSQL)** (for database)
* **LangGraph (Python)** (for workflow orchestration)
* **LLM (OpenAI / Gemini / Claude)** for:

  * Message personalization
  * Offer letter generation
  * (Optional) sentiment classification

Messaging (Email/SMS/WhatsApp) and Calendar are **mocked**.

---

## 4. Project Purpose (Important Clarification)

This system does **NOT**:

* Parse resumes
* Match skills to jobs
* Decide candidate-job fit

It assumes:

> A candidate is already created in the system with a `candidate_id` and `job_id`.

The system only manages:

* Communication
* Scheduling
* Offers
* Risk detection

---

## 5. Database Schema (Already Created)

The following tables have been created in Supabase:

### 1. `candidate_pipeline`

Stores the **current state** of the candidate.

Columns:

* candidate_id (PK)
* job_id
* stage
* stage_updated_at
* preferred_channel (email/sms/whatsapp)
* timezone (default Asia/Kolkata)
* created_at

Meaning:
One row = one candidate in one job pipeline.

---

### 2. `candidate_touchpoints`

Stores **all communications and events**.

Columns:

* id (UUID)
* candidate_id (FK)
* type (status_update / reminder / schedule / offer / survey / alert)
* channel (email / sms / whatsapp / system)
* message
* sentiment (positive / neutral / negative)
* delivery_status (queued / sent / failed)
* metadata (JSON)
* created_at

Meaning:
Each row = one interaction or system event.

---

### 3. `interview_slots`

Stores interview scheduling data.

Columns:

* id (UUID)
* candidate_id (FK)
* job_id
* interviewer_email
* proposed_slots (JSON list of timestamps)
* chosen_slot
* meeting_link
* status (proposed / confirmed / rescheduled / cancelled)
* created_at

Meaning:
Tracks proposed and confirmed interview slots.

---

### 4. `offer_letters`

Stores generated offer letters.

Columns:

* id (UUID)
* candidate_id (FK)
* job_id
* offer_text
* offer_pdf_path
* compensation_json
* status (draft / sent / signed / expired / withdrawn)
* created_at

Meaning:
Stores LLM-generated offer content and compensation data.

---

### 5. `candidate_risk_signals`

Stores disengagement risk information.

Columns:

* id (UUID)
* candidate_id (FK)
* risk_score (0–100)
* reasons (array of text)
* last_response_at
* response_gap_hours
* created_at

Meaning:
Tracks likelihood of candidate dropping out.

---

## 6. Candidate Journey Model

Stages:

* APPLIED
* SCREENED
* INTERVIEW_SCHEDULED
* INTERVIEWED
* OFFERED
* OFFER_ACCEPTED
* ONBOARDING
* CLOSED_REJECTED
* CLOSED_WITHDRAWN

Rules:

* Candidate cannot skip stages
* Offer can only be generated if stage ≥ INTERVIEWED
* If stage is CLOSED_*, no communication should be sent (except closure message)

---

## 7. APIs To Be Implemented

1. POST `/hr/engagement/stage/update`
2. POST `/hr/engagement/status/send`
3. POST `/hr/engagement/interview/propose-slots`
4. POST `/hr/engagement/interview/confirm`
5. POST `/hr/engagement/offer/generate`
6. POST `/hr/engagement/risk/evaluate`
7. GET  `/hr/engagement/candidate/{candidateId}/timeline`

Each API:

* Validates rules
* Writes to DB
* Runs workflow logic (LangGraph)
* Optionally calls LLM
* Returns JSON

---

## 8. AI (LLM) Usage

LLM is used only for:

* Message personalization
* Offer letter generation
* Optional sentiment classification

No ML model training is required.

---

## 9. Current Progress

✅ Database tables created in Supabase
✅ Project scope clarified
✅ Task converted from Node.js to Python + FastAPI
✅ Database schema understood and finalized
✅ **FastAPI project structure setup**
✅ **Supabase connection enabled**
✅ **All 7 Core APIs implemented**
✅ **Service layer verification (Pipeline, Risk, Offer, Messaging)**
✅ **Postman collection created**

---

## 10. Pending Work

⏳ **LangGraph Workflow Orchestration** (Folder `src/agents/` is empty)
⏳ **Gemini LLM Integration** (Currently using templates/mocks)
⏳ **Advanced Message Personalization** (Currently using templates)
⏳ **Comprehensive Testing** (Tests exist but need execution)


---

## 11. Execution Model

All workflows are triggered via API calls:

```
Postman / HR Tool
      ↓
   FastAPI
      ↓
   Service Layer
      ↓
   LangGraph
      ↓
   DB + LLM + Mocked Services
```

No background or automatic execution without an API call.
