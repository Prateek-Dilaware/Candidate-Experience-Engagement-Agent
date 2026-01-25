# Quick Start - Test API 1

This guide will help you test the first API endpoint in 5 minutes.

## 🚀 Quick Setup

### Step 1: Install Dependencies (1 min)
```bash
pip install -e .
```

### Step 2: Create `.env` File (1 min)
Copy `.env.example` to `.env` and add your credentials:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
GOOGLE_API_KEY=your-gemini-key-here
```

**Don't have Supabase yet?**
1. Go to https://supabase.com
2. Create free account
3. Create new project
4. Copy URL and anon key from Settings → API

### Step 3: Setup Database (1 min)
1. Open Supabase SQL Editor
2. Copy content from `supabase_schema.sql`
3. Click "Run"

### Step 4: Start Server (30 sec)
```bash
uv run uvicorn main:app --reload
```

Should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8080
```

### Step 5: Test API (30 sec)

**Option A: Using Browser**
Go to: http://localhost:8080/docs
Click on `/hr/engagement/stage/update` → Try it out

**Option B: Using cURL**
```bash
curl -X POST http://localhost:8080/hr/engagement/stage/update \
  -H "Content-Type: application/json" \
  -d '{
    "candidateId": "CAND-001",
    "jobId": "JOB-101",
    "newStage": "SCREENED"
  }'
```

**Option C: Using Postman**
- Import the request from `TESTING_GUIDE.md`

---

## ✅ Expected Result

```json
{
  "candidateId": "CAND-001",
  "stage": "SCREENED",
  "stageUpdatedAt": "2026-01-24T10:30:00.000Z"
}
```

Console should show:
```
📤 [EMAIL] Sending to CAND-001: Hi Candidate, great news! Your application...
```

---

## 🔍 Verify in Database

Go to Supabase Table Editor:

**candidate_pipeline table:**
- Should see CAND-001 with stage = SCREENED

**candidate_touchpoints table:**
- Should see message sent to CAND-001

---

## 🎯 Try These Tests

### Test 1: Progress Through Stages
```bash
# Screened → Interview Scheduled
curl -X POST http://localhost:8080/hr/engagement/stage/update \
  -H "Content-Type: application/json" \
  -d '{"candidateId": "CAND-001", "jobId": "JOB-101", "newStage": "INTERVIEW_SCHEDULED"}'
```

### Test 2: Invalid Transition (Should Fail)
```bash
# Try to skip directly to OFFERED - should get error
curl -X POST http://localhost:8080/hr/engagement/stage/update \
  -H "Content-Type: application/json" \
  -d '{"candidateId": "CAND-001", "jobId": "JOB-101", "newStage": "OFFERED"}'
```

Expected error:
```json
{
  "detail": "Failed to update candidate stage: Cannot skip from INTERVIEW_SCHEDULED to OFFERED..."
}
```

---

## 🐛 Troubleshooting

### Error: "Module not found"
```bash
# Make sure you're in the Task4 directory
cd D:\code\Task4
pip install -e .
```

### Error: "Connection refused"
- Check if server is running: `uv run uvicorn main:app --reload`
- Check port 8080 is not in use

### Error: "Supabase connection failed"
- Verify URL and key in `.env`
- Check Supabase project is active

### Error: "Candidate not found"
- First call creates the candidate automatically
- Check database tables exist

---

## 📚 Next Steps

See `TESTING_GUIDE.md` for:
- Complete test cases
- All stage transitions
- Database queries
- Advanced scenarios

See `README.md` for:
- Full API documentation
- Project architecture
- Development roadmap
