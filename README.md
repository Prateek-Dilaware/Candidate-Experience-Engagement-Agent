# 🚀 TalentFlow: AI-Powered Candidate Engagement System

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

TalentFlow is an intelligent candidate engagement and recruitment automation platform that leverages AI (Google Gemini) and workflow orchestration (LangGraph) to streamline the hiring process. It provides multi-channel communication, automated messaging, risk evaluation, and comprehensive candidate tracking.

---

## 📋 Table of Contents

- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Project Architecture](#-project-architecture)
- [Getting Started](#-getting-started)
- [API Reference](#-api-reference)
- [Database Schema](#-database-schema)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Development Guide](#-development-guide)

---

## ✨ Key Features

### 🤖 AI-Powered Communication
- **Smart Message Generation**: Uses Google Gemini to craft personalized, context-aware messages
- **Channel-Adaptive Content**: Automatically adjusts tone and length for Email (formal), SMS (concise), and WhatsApp (conversational)
- **Structured Output**: Ensures consistent, professional communication with Pydantic validation

### 📊 Workflow Automation
- **LangGraph Orchestration**: Automated state machine for candidate engagement workflows
- **Stage Transition Management**: Validates and tracks candidate progress through recruitment pipeline
- **Multi-Channel Delivery**: Supports Email (SMTP), SMS, and WhatsApp (mocked for development)

### 🎯 Intelligent Features
- **Risk Evaluation**: Predictive scoring based on response gaps, sentiment, and interaction patterns
- **Interview Scheduling**: Automated slot proposal and confirmation with calendar integration
- **Offer Letter Generation**: AI-drafted professional employment offers
- **Timeline Tracking**: Complete audit log of all candidate interactions

### 💻 Modern Frontend
- **Real-time Dashboard**: Live visualization of candidate pipeline and statistics
- **Responsive Interface**: Clean, intuitive UI for HR operations
- **API Visualizer**: Interactive tool for testing and exploring all API endpoints

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (async Python web framework)
- **AI/ML**: Google Gemini (LLM), LangChain (AI orchestration), LangGraph (workflow automation)
- **Database**: Supabase (PostgreSQL)
- **Email**: SMTP (Gmail integration)
- **Validation**: Pydantic (data validation)
- **Server**: Uvicorn (ASGI server)

### Frontend
- **Core**: Vanilla JavaScript (ES6+)
- **UI**: HTML5, CSS3 (responsive design)
- **Charts**: Chart.js (data visualization)
- **Icons**: Lucide icons

### DevOps & Tools
- **Package Manager**: uv (fast Python package installer)
- **Environment**: Python 3.12+
- **API Testing**: Postman, REST Client (VS Code)

---

## 🏗️ Project Architecture

```
┌─────────────────┐
│   Frontend      │  ← User Interface (HTML/JS/CSS)
│   (Vanilla JS)  │
└────────┬────────┘
         │ HTTP Requests
         ↓
┌─────────────────┐
│   FastAPI       │  ← REST API Layer
│   Routes        │     • /metadata
└────────┬────────┘     • /stage/update
         │              • /status/send
         ↓              • /interview/*
┌─────────────────┐     • /offer/generate
│  Controllers    │  ← Business Logic Orchestration
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Services      │  ← Core Business Services
│                 │     • PipelineService
│                 │     • MessagingService
│                 │     • SchedulingService
└────────┬────────┘     • RiskService
         │              • OfferService
         ↓
┌─────────────────┐
│   AI Agents     │  ← LangGraph + Gemini Integration
│                 │     • EngagementGraph (workflow)
│                 │     • MessagePersonalizer (AI)
└────────┬────────┘     • OfferWriter (AI)
         │
         ↓
┌─────────────────┐
│   Database      │  ← Supabase (PostgreSQL)
│   (Supabase)    │     • candidate_profiles
└─────────────────┘     • candidate_pipeline
                        • candidate_touchpoints
                        • interview_slots
                        • offer_letters
```

### Data Flow Example: Stage Update

```
User clicks "Move to Interviewed" in UI
    ↓
POST /hr/engagement/stage/update
    ↓
EngagementController.update_candidate_stage()
    ↓
┌─────────────────────────────────────┐
│ 1. CandidateDataService             │ → Fetch candidate name
│ 2. CandidateDataService             │ → Fetch job title  
│ 3. PipelineService                  │ → Validate & update stage
│ 4. EngagementGraph (LangGraph)      │ → Orchestrate workflow
│    ├─ MessagePersonalizer (Gemini)  │ → Generate AI message
│    └─ MessagingService              │ → Send via SMTP/SMS/WhatsApp
└─────────────────────────────────────┘
    ↓
Response with updated stage + confirmation
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+** installed
- **uv** package manager ([Installation guide](https://github.com/astral-sh/uv))
- **Supabase account** with database setup
- **Google Gemini API key** ([Get it here](https://makersuite.google.com/app/apikey))
- **Gmail account** for SMTP (with app password enabled)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Task4_TS
   ```

2. **Create `.env` file** in the root directory:
   ```env
   # Supabase Configuration
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   
   # Google Gemini API
   GOOGLE_API_KEY=your_gemini_api_key
   
   # SMTP Configuration (Gmail)
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_EMAIL=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   
   # Application Settings
   APP_HOST=0.0.0.0
   APP_PORT=8080
   DEBUG=True
   DEFAULT_TIMEZONE=Asia/Kolkata
   ```

3. **Set up the database**
   - Create a Supabase project
   - Run the SQL schema:
     ```bash
     # Copy and execute the contents of supabase_schema.sql in your Supabase SQL editor
     ```

4. **Install dependencies**
   ```bash
   uv sync
   ```

5. **Seed the database** (optional, for testing)
   ```bash
   uv run python -m src.scripts.seed_db
   ```

6. **Run the application**
   ```bash
   uv run uvicorn main:app --reload
   ```

7. **Access the application**
   - **Main Dashboard**: http://127.0.0.1:8080/hr/engagement/
   - **API Visualizer**: http://127.0.0.1:8080/static/visualizer.html
   - **Health Check**: http://127.0.0.1:8080/health
   - **API Docs**: http://127.0.0.1:8080/docs

---

## 📡 API Reference

### Base URL
```
http://127.0.0.1:8080/hr/engagement
```

### Endpoints

#### 1. Metadata & Discovery

##### Get Metadata
```http
GET /metadata
```
**Description**: Fetches all candidates, jobs, stages, and message types for UI population

**Response**:
```json
{
  "candidates": [
    {
      "candidate_id": "CAND001",
      "full_name": "John Doe",
      "email": "john@example.com"
    }
  ],
  "jobs": [
    {
      "job_id": "JOB001",
      "title": "Senior Backend Engineer"
    }
  ],
  "stages": ["APPLIED", "SCREENED", "INTERVIEWED", ...],
  "message_types": ["stage_update", "reminder_24h", ...]
}
```

---

#### 2. Pipeline Management

##### Get Candidate Pipeline Info
```http
GET /candidate/{candidateId}/job/{jobId}/pipeline
```
**Description**: Fetches current stage and pipeline details

**Response**:
```json
{
  "candidate_id": "CAND001",
  "job_id": "JOB001",
  "stage": "INTERVIEWED",
  "preferred_channel": "email",
  "stage_updated_at": "2026-01-27T10:30:00Z"
}
```

##### Update Candidate Stage
```http
POST /stage/update
```
**Request Body**:
```json
{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "newStage": "INTERVIEWED"
}
```

**Response**:
```json
{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "stage": "INTERVIEWED",
  "stageUpdatedAt": "2026-01-27T10:30:00Z"
}
```

**What Happens**:
1. Validates stage transition
2. Updates database
3. Generates AI-personalized message
4. Sends notification via preferred channel
5. Records touchpoint in audit log

---

#### 3. Messaging

##### Send Status Update
```http
POST /status/send
```
**Request Body**:
```json
{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "messageType": "STAGE_UPDATE",
  "channelOverride": "email"
}
```

**Response**:
```json
{
  "sent": true,
  "channel": "email",
  "message": "Hi John, we're pleased to inform you..."
}
```

---

#### 4. Interview Scheduling

##### Propose Interview Slots
```http
POST /interview/propose-slots
```
**Request Body**:
```json
{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "date": "2026-02-01"
}
```

**Response**:
```json
{
  "status": "proposed",
  "slots": [
    "2026-02-01T10:00:00Z",
    "2026-02-01T14:00:00Z",
    "2026-02-01T16:00:00Z"
  ]
}
```

##### Confirm Interview
```http
POST /interview/confirm
```
**Request Body**:
```json
{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "chosenSlot": "2026-02-01T10:00:00Z"
}
```

**Response**:
```json
{
  "status": "confirmed",
  "meetingLink": "https://meet.google.com/abc-defg-hij",
  "remindersScheduled": ["24h", "1h"]
}
```

---

#### 5. Offer Management

##### Generate Offer Letter
```http
POST /offer/generate
```
**Request Body**:
```json
{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "joiningDate": "2026-03-01"
}
```

**Response**:
```json
{
  "offerId": "OFF001",
  "status": "draft",
  "offerPreview": "Dear John Doe,\n\nWe are pleased to offer you..."
}
```

---

#### 6. Risk Evaluation

##### Evaluate Candidate Risk
```http
POST /risk/evaluate
```
**Request Body**:
```json
{
  "candidateId": "CAND001",
  "jobId": "JOB001"
}
```

**Response**:
```json
{
  "riskScore": 35,
  "reasons": [
    "No response for 48 hours",
    "Rescheduled interview once"
  ],
  "alertTriggered": false
}
```

**Risk Factors**:
- Response gap (24h: +15, 48h: +25, 72h: +40 points)
- Negative sentiment: +25 points
- Rescheduled twice: +20 points
- Missed interview: +35 points
- **Alert Threshold**: 70 points

---

#### 7. Candidate Timeline

##### Get Interaction History
```http
GET /candidate/{candidateId}/job/{jobId}/timeline
```
**Response**:
```json
{
  "candidateId": "CAND001",
  "jobId": "JOB001",
  "events": [
    {
      "id": "uuid",
      "type": "status_update",
      "timestamp": "2026-01-27T10:30:00Z",
      "stage": "INTERVIEWED",
      "channel": "email",
      "message": "Congratulations on completing your interview!",
      "metadata": {}
    }
  ]
}
```

---

## 🗄️ Database Schema

TalentFlow uses **7 core tables** in Supabase (PostgreSQL):

### 1. `candidate_profiles`
**Purpose**: Core candidate identity and contact information

| Column | Type | Description |
|--------|------|-------------|
| candidate_id | TEXT (PK) | Unique identifier |
| full_name | TEXT | Candidate's full name |
| email | TEXT (UNIQUE) | Email address |
| created_at | TIMESTAMPTZ | Registration timestamp |

### 2. `jobs`
**Purpose**: Job postings and recruiter details

| Column | Type | Description |
|--------|------|-------------|
| job_id | TEXT (PK) | Unique job identifier |
| title | TEXT | Job title/position |
| interviewer_email | TEXT | Hiring manager email |
| created_at | TIMESTAMPTZ | Creation timestamp |

### 3. `candidate_pipeline`
**Purpose**: Tracks candidate progress through recruitment stages

| Column | Type | Description |
|--------|------|-------------|
| candidate_id | TEXT (PK, FK) | References candidate_profiles |
| job_id | TEXT (PK, FK) | References jobs |
| stage | TEXT | Current recruitment stage (ENUM) |
| stage_updated_at | TIMESTAMPTZ | Last stage change timestamp |
| preferred_channel | TEXT | Communication preference (email/sms/whatsapp) |
| timezone | TEXT | Candidate timezone |
| created_at | TIMESTAMPTZ | Pipeline entry timestamp |

**Stage Values**: `APPLIED`, `SCREENED`, `INTERVIEW_SCHEDULED`, `INTERVIEWED`, `OFFERED`, `OFFER_ACCEPTED`, `ONBOARDING`, `CLOSED_REJECTED`, `CLOSED_WITHDRAWN`

### 4. `candidate_touchpoints`
**Purpose**: Audit log of all candidate communications and interactions

| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Unique touchpoint ID |
| candidate_id | TEXT (FK) | References candidate_pipeline |
| job_id | TEXT (FK) | References candidate_pipeline |
| stage | TEXT | Stage at time of touchpoint |
| type | TEXT | Interaction type (status_update, reminder, etc.) |
| channel | TEXT | Communication channel used |
| message | TEXT | Message content sent |
| sentiment | TEXT | Detected sentiment (positive/neutral/negative) |
| delivery_status | TEXT | Status (queued/sent/failed) |
| metadata | JSONB | Additional context (JSON object) |
| created_at | TIMESTAMPTZ | Touchpoint timestamp |

### 5. `candidate_risk_signals`
**Purpose**: Stores AI-calculated risk assessments

| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Unique signal ID |
| candidate_id | TEXT (FK) | References candidate_pipeline |
| job_id | TEXT (FK) | References candidate_pipeline |
| risk_score | INT | Calculated risk score (0-100) |
| reasons | JSONB | Array of risk factors |
| alert_triggered | BOOLEAN | Whether score exceeded threshold (70) |
| created_at | TIMESTAMPTZ | Assessment timestamp |

### 6. `interview_slots`
**Purpose**: Manages interview scheduling and availability

| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Unique slot ID |
| candidate_id | TEXT (FK) | References candidate_pipeline |
| job_id | TEXT (FK) | References candidate_pipeline |
| proposed_slots | JSONB | Array of proposed times |
| chosen_slot | TIMESTAMPTZ | Selected interview time |
| meeting_link | TEXT | Video call URL |
| status | TEXT | Status (proposed/confirmed/cancelled) |
| created_at | TIMESTAMPTZ | Slot creation timestamp |

### 7. `offer_letters`
**Purpose**: Stores generated employment offers

| Column | Type | Description |
|--------|------|-------------|
| offer_id | TEXT (PK) | Unique offer ID |
| candidate_id | TEXT (FK) | References candidate_pipeline |
| job_id | TEXT (FK) | References candidate_pipeline |
| content | TEXT | Full offer letter text (markdown) |
| joining_date | DATE | Proposed start date |
| status | TEXT | Status (draft/sent/accepted/rejected) |
| created_at | TIMESTAMPTZ | Offer creation timestamp |

### Database Relationships

```
candidate_profiles (1) ─────< (N) candidate_pipeline (N) >───── (1) jobs
        │                              │
        │                              │
        └──────────────────────────────┴────< candidate_touchpoints
                                       │
                                       ├────< candidate_risk_signals
                                       │
                                       ├────< interview_slots
                                       │
                                       └────< offer_letters
```

### Important Constraints

1. **Cascade Deletes**: When a candidate or job is deleted, all related records are automatically removed
2. **Unique Constraints**: 
   - Email addresses must be unique in `candidate_profiles`
   - (candidate_id, job_id) pair is unique in `candidate_pipeline`
3. **Check Constraints**: Stage, channel, sentiment, status fields are validated against allowed values
4. **Foreign Keys**: Ensure referential integrity across all relationships

---

## 📁 Project Structure

```
Task4_TS/
├── 📄 main.py                          # FastAPI application entry point
├── 📄 pyproject.toml                   # Project dependencies (uv)
├── 📄 .env                             # Environment variables (not in repo)
├── 📄 supabase_schema.sql              # Database schema SQL
├── 📄 api_tests.http                   # REST Client API tests
├── 📄 postman_collection.json          # Postman API collection
├── 📄 mock_sms.txt                     # SMS delivery log (generated)
├── 📄 mock_whatsapp.txt                # WhatsApp delivery log (generated)
│
├── 📁 src/                             # Source code root
│   │
│   ├── 📁 agents/                      # 🤖 AI Agents (LangGraph + Gemini)
│   │   ├── engagement_flow.py          #    • LangGraph workflow orchestrator
│   │   ├── message_personalizer.py     #    • AI message generator (channel-aware)
│   │   ├── offer_writer.py             #    • AI offer letter generator
│   │   └── gemini_client.py            #    • Google Gemini API wrapper
│   │
│   ├── 📁 api/                         # 🌐 REST API Layer
│   │   ├── 📁 routes/                  
│   │   │   └── engagement.py           #    • FastAPI route definitions
│   │   └── 📁 controllers/             
│   │       └── engagement_controller.py #    • Business logic orchestration
│   │
│   ├── 📁 services/                    # ⚙️ Core Business Services
│   │   ├── pipeline_service.py         #    • Stage management & validation
│   │   ├── messaging_service.py        #    • Multi-channel message delivery
│   │   ├── candidate_data_service.py   #    • Candidate & job data fetching
│   │   ├── scheduling_service.py       #    • Interview slot management
│   │   ├── offer_service.py            #    • Offer letter generation
│   │   ├── risk_service.py             #    • Risk score calculation
│   │   ├── template_service.py         #    • Message template generation
│   │   └── google_calendar_service.py  #    • Calendar integration
│   │
│   ├── 📁 config/                      # ⚙️ Configuration & Constants
│   │   ├── settings.py                 #    • Environment variable management (Pydantic)
│   │   └── constants.py                #    • Enums (Stage, Channel, MessageType, etc.)
│   │
│   ├── 📁 db/                          # 🗄️ Database Layer
│   │   ├── supabase_client.py          #    • Supabase connection singleton
│   │   └── models.py                   #    • Database model definitions
│   │
│   ├── 📁 schemas/                     # 📋 API Request/Response Models
│   │   └── engagement_schema.py        #    • Pydantic schemas for validation
│   │
│   ├── 📁 scripts/                     # 🛠️ Utility Scripts
│   │   ├── seed_db.py                  #    • Database seeding script
│   │   ├── test_all_apis.py            #    • API testing script
│   │   └── verify_api_data.py          #    • Data verification script
│   │
│   ├── 📁 frontend/                    # 💻 Frontend (Static Files)
│   │   ├── index.html                  #    • Main dashboard UI
│   │   ├── script.js                   #    • Frontend JavaScript logic
│   │   ├── style.css                   #    • Styling
│   │   └── visualizer.html             #    • API testing visualizer
│   │
│   └── 📁 templates/                   # 📧 Message Templates (if needed)
│
└── 📁 .venv/                           # Python virtual environment
```

### Folder Descriptions

#### 🤖 `agents/` - AI-Powered Automation
The "brain" of the system. Contains AI agents that:
- Generate personalized messages using Google Gemini
- Orchestrate workflows using LangGraph state machines
- Adapt content based on communication channel (Email/SMS/WhatsApp)
- Create formal offer letters with AI assistance

**Key Files**:
- `engagement_flow.py`: LangGraph workflow that automates the entire engagement process
- `message_personalizer.py`: AI agent that crafts channel-optimized messages
- `offer_writer.py`: AI agent for generating professional offer letters
- `gemini_client.py`: Wrapper for Google Gemini API

#### 🌐 `api/` - HTTP Interface
The "interface" between frontend and backend. Follows MVC pattern:
- **routes/**: Defines HTTP endpoints (URL mappings)
- **controllers/**: Orchestrates business logic (coordinates services)

**Flow**: `User Request` → `Route` → `Controller` → `Services` → `Response`

#### ⚙️ `services/` - Business Logic
The "workers" of the system. Each service handles specific domain logic:
- `pipeline_service.py`: Manages candidate stage transitions with validation
- `messaging_service.py`: Handles multi-channel message delivery (Email/SMS/WhatsApp)
- `candidate_data_service.py`: CRUD operations for candidates and jobs
- `scheduling_service.py`: Interview slot management
- `offer_service.py`: Offer letter creation and tracking
- `risk_service.py`: Calculates dropout risk scores
- `template_service.py`: Generates message templates

#### ⚙️ `config/` - Configuration Management
Central configuration hub:
- `settings.py`: Loads environment variables (Supabase, Gemini API, SMTP)
- `constants.py`: Defines enums and business rules (stages, channels, risk weights)

#### 🗄️ `db/` - Database Layer
Database abstraction layer:
- `supabase_client.py`: Singleton Supabase client
- `models.py`: Database model definitions (Pydantic or SQLAlchemy-style)

#### 📋 `schemas/` - Data Validation
Pydantic models for API request/response validation:
- Ensures type safety
- Automatic OpenAPI documentation
- Input sanitization

#### 🛠️ `scripts/` - Utilities
Helper scripts for development:
- `seed_db.py`: Populates database with test data
- `test_all_apis.py`: Automated API testing
- `verify_api_data.py`: Data integrity checks

#### 💻 `frontend/` - User Interface
Static files served by FastAPI:
- `index.html`: Main HR dashboard
- `script.js`: Frontend logic (API calls, UI updates)
- `style.css`: Responsive styling
- `visualizer.html`: Interactive API testing tool

---

## 🔄 How It Works

### 1. Stage Update Flow (Complete Walkthrough)

**Scenario**: HR wants to move candidate "John Doe" from "SCREENED" to "INTERVIEWED"

#### Step-by-Step Process:

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. USER ACTION (Frontend)                                       │
└─────────────────────────────────────────────────────────────────┘
   User clicks "Update to INTERVIEWED" in dashboard
   
   ↓ HTTP POST Request
   
┌─────────────────────────────────────────────────────────────────┐
│ 2. API ROUTE (engagement.py)                                    │
└─────────────────────────────────────────────────────────────────┘
   POST /hr/engagement/stage/update
   {
     "candidateId": "CAND001",
     "jobId": "JOB001", 
     "newStage": "INTERVIEWED"
   }
   
   ↓ Route validates request schema
   
┌─────────────────────────────────────────────────────────────────┐
│ 3. CONTROLLER (engagement_controller.py)                        │
└─────────────────────────────────────────────────────────────────┘
   update_candidate_stage() method called
   
   ├─> Step 3a: Fetch candidate profile
   │   CandidateDataService.get_candidate_profile("CAND001")
   │   → Returns: { full_name: "John Doe", email: "john@example.com" }
   │
   ├─> Step 3b: Fetch job details
   │   CandidateDataService.get_job_details("JOB001")
   │   → Returns: { title: "Senior Backend Engineer" }
   │
   ├─> Step 3c: Get current pipeline status
   │   PipelineService.get_candidate("CAND001", "JOB001")
   │   → Returns: { stage: "SCREENED", preferred_channel: "email" }
   │
   ├─> Step 3d: Validate & update stage
   │   PipelineService.update_candidate_stage()
   │   └─> Validates: Can we go from SCREENED → INTERVIEWED? ✅
   │   └─> Updates database: stage = "INTERVIEWED"
   │
   └─> Step 3e: Send notification
       MessagingService.send_stage_update_notification()
       
       ↓
       
┌─────────────────────────────────────────────────────────────────┐
│ 4. AI MESSAGE GENERATION (message_personalizer.py)              │
└─────────────────────────────────────────────────────────────────┘
   MessagePersonalizer.generate_stage_update_message()
   
   Inputs:
   - candidate_name: "John Doe"
   - role_title: "Senior Backend Engineer"  
   - new_stage: "INTERVIEWED"
   - channel: "email"
   
   ├─> Selects appropriate prompt template (EMAIL)
   │   • Formal tone
   │   • Include subject line
   │   • Max 150 words
   │
   ├─> Calls Google Gemini API
   │   GeminiClient → ChatGoogleGenerativeAI
   │   Prompt: "Write a professional email to John Doe..."
   │
   └─> Returns structured output (Pydantic validated)
       {
         "subject": "Congratulations - Next Steps After Your Interview",
         "body": "Dear John,\n\nThank you for taking the time to 
                  interview for the Senior Backend Engineer position..."
       }
       
   ↓
   
┌─────────────────────────────────────────────────────────────────┐
│ 5. MESSAGE DELIVERY (messaging_service.py)                      │
└─────────────────────────────────────────────────────────────────┘
   MessagingService.send_message()
   
   ├─> Determines channel (email from candidate preference)
   │
   ├─> Sends via SMTP
   │   _send_email_smtp()
   │   ├─> Creates MIMEText message
   │   ├─> Connects to Gmail SMTP server
   │   ├─> Sends email to john@example.com
   │   └─> Returns success/failure
   │
   └─> Records touchpoint in database
       Inserts into candidate_touchpoints:
       {
         candidate_id: "CAND001",
         job_id: "JOB001",
         stage: "INTERVIEWED",
         type: "status_update",
         channel: "email",
         message: "Dear John...",
         delivery_status: "sent",
         created_at: "2026-01-27T10:30:00Z"
       }
       
   ↓
   
┌─────────────────────────────────────────────────────────────────┐
│ 6. RESPONSE TO FRONTEND                                         │
└─────────────────────────────────────────────────────────────────┘
   HTTP 200 OK
   {
     "candidateId": "CAND001",
     "jobId": "JOB001",
     "stage": "INTERVIEWED",
     "stageUpdatedAt": "2026-01-27T10:30:00Z"
   }
   
   ↓
   
┌─────────────────────────────────────────────────────────────────┐
│ 7. UI UPDATE                                                    │
└─────────────────────────────────────────────────────────────────┘
   Dashboard refreshes:
   - Pipeline view shows "INTERVIEWED" badge
   - Timeline shows new touchpoint event
   - Success notification displayed to user
```

### 2. Channel-Aware Messaging

The system automatically adapts message style based on channel:

#### Email (Formal)
```
Subject: Interview Feedback - Senior Backend Engineer Position

Dear John Doe,

Thank you for taking the time to interview with us for the Senior 
Backend Engineer position. We were impressed by your technical skills 
and experience. Our team is currently reviewing your interview 
performance, and we will share feedback within the next 2-3 business 
days.

Best regards,
TalentFlow Recruiting Team
```

#### SMS (Concise - 40 words max)
```
Hi John! Thanks for interviewing for Senior Backend Engineer. 
We're reviewing your performance and will share feedback in 2-3 days. 
Questions? Reply here. - TalentFlow
```

#### WhatsApp (Conversational - 60 words max)
```
Hi John! 👋

Thanks so much for interviewing with us today for the Senior Backend 
Engineer role. You did great! Our team is discussing next steps and 
we'll get back to you within 2-3 days with feedback. 

Feel free to reach out if you have any questions!

- TalentFlow Team
```

### 3. Risk Evaluation Logic

**Risk Score Calculation**:

```python
Base Score = 0

# Response Time Penalties
if no_response_24h:  score += 15
if no_response_48h:  score += 25  # replaces 24h penalty
if no_response_72h:  score += 40  # replaces 48h penalty

# Sentiment Analysis
if negative_sentiment:  score += 25

# Interview Behavior
if rescheduled_twice:   score += 20
if missed_interview:    score += 35

# Alert Trigger
if score >= 70:  alert_triggered = True
```

**Example Scenarios**:

| Scenario | Factors | Score | Alert |
|----------|---------|-------|-------|
| Responsive candidate | No issues | 0 | ❌ |
| Slow responder | 48h gap | 25 | ❌ |
| Concerning candidate | 48h gap + negative sentiment | 50 | ❌ |
| High risk | 72h gap + rescheduled twice | 60 | ❌ |
| Critical risk | 72h gap + missed interview | 75 | ✅ |

### 4. Interview Scheduling Flow

```
HR: Propose slots for Feb 1st
  ↓
System generates 3 available times:
  • 10:00 AM
  • 2:00 PM  
  • 4:00 PM
  ↓
Candidate selects 10:00 AM
  ↓
System:
  1. Creates Google Calendar event
  2. Generates meeting link
  3. Schedules reminders (24h & 1h before)
  4. Sends confirmation email
  ↓
Status: INTERVIEW_SCHEDULED
```

---

## 👨‍💻 Development Guide

### Running the Server

```bash
# Development mode (auto-reload)
uv run uvicorn main:app --reload

# Production mode
uv run uvicorn main:app --host 0.0.0.0 --port 8080
```

### Testing APIs

#### Using REST Client (VS Code)
```bash
# Open api_tests.http in VS Code
# Click "Send Request" above each endpoint
```

#### Using Postman
```bash
# Import postman_collection.json
# All endpoints are pre-configured
```

#### Using API Visualizer
```
http://127.0.0.1:8080/static/visualizer.html
```



#### Viewing Mock Logs
```bash
# SMS logs
cat mock_sms.txt

# WhatsApp logs  
cat mock_whatsapp.txt
```

### Common Development Tasks

#### Adding a New Stage
1. Update `src/config/constants.py`:
   ```python
   class CandidateStage(str, Enum):
       NEW_STAGE = "NEW_STAGE"
   ```

2. Update `STAGE_ORDER` list

3. Update database schema (add CHECK constraint)

#### Adding a New Channel
1. Update `src/config/constants.py`:
   ```python
   class Channel(str, Enum):
       NEW_CHANNEL = "new_channel"
   ```

2. Implement delivery in `messaging_service.py`:
   ```python
   elif channel == Channel.NEW_CHANNEL:
       self._send_new_channel(to, message)
   ```

3. Add prompt template in `message_personalizer.py`:
   ```python
   def _new_channel_prompt(self) -> ChatPromptTemplate:
       return ChatPromptTemplate.from_template(...)
   ```

### Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SUPABASE_URL` | ✅ | Supabase project URL | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | ✅ | Supabase anon key | `eyJhbGc...` |
| `GOOGLE_API_KEY` | ✅ | Gemini API key | `AIzaSy...` |
| `SMTP_SERVER` | ✅ | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | ✅ | SMTP port | `587` |
| `SMTP_EMAIL` | ✅ | Sender email | `your@gmail.com` |
| `SMTP_PASSWORD` | ✅ | App password | `xxxx xxxx xxxx xxxx` |
| `APP_HOST` | ❌ | Server host | `0.0.0.0` |
| `APP_PORT` | ❌ | Server port | `8080` |
| `DEBUG` | ❌ | Debug mode | `True` |
| `DEFAULT_TIMEZONE` | ❌ | Default timezone | `Asia/Kolkata` |

### Troubleshooting

#### SMTP Authentication Failed
```bash
# Enable 2FA on Gmail
# Generate app password: https://myaccount.google.com/apppasswords
# Use app password (not your Gmail password) in .env
```

#### Supabase Connection Error
```bash
# Verify URL and key in Supabase dashboard
# Check network connectivity
# Ensure IP is whitelisted (if applicable)
```

#### Gemini API Quota Exceeded
```bash
# Check quota: https://makersuite.google.com/app/apikey
# Reduce temperature for more deterministic outputs (lower token usage)
# Implement caching for repeated queries
```

#### Module Not Found
```bash
# Ensure virtual environment is activated
uv sync

# Or reinstall dependencies
uv pip install -r pyproject.toml
```

---

## 📊 Key Metrics & Monitoring

The dashboard provides real-time insights:

- **Active Candidates**: Total candidates in pipeline
- **Stage Distribution**: Visual breakdown of candidates per stage
- **Communication Channels**: Email vs SMS vs WhatsApp usage
- **Risk Alerts**: High-risk candidates (score ≥ 70)
- **Response Times**: Average candidate response time
- **Interview Scheduling**: Pending vs confirmed interviews

---



## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Google Gemini**: AI-powered message generation
- **LangChain**: AI orchestration framework
- **LangGraph**: Workflow automation
- **Supabase**: Database and backend infrastructure
- **FastAPI**: High-performance web framework

---

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Contact: theprateekdilaware@gmail.com

---


