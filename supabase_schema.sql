-- Supabase Database Schema for Candidate Engagement System
-- Run this in Supabase SQL Editor

-- Table 1: Candidate Pipeline
CREATE TABLE IF NOT EXISTS candidate_pipeline (
    candidate_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    stage_updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    preferred_channel TEXT DEFAULT 'email',
    timezone TEXT DEFAULT 'Asia/Kolkata',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 2: Candidate Touchpoints
CREATE TABLE IF NOT EXISTS candidate_touchpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id TEXT NOT NULL REFERENCES candidate_pipeline(candidate_id),
    type TEXT NOT NULL,
    channel TEXT NOT NULL,
    message TEXT NOT NULL,
    sentiment TEXT,
    delivery_status TEXT DEFAULT 'queued',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 3: Interview Slots
CREATE TABLE IF NOT EXISTS interview_slots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id TEXT NOT NULL REFERENCES candidate_pipeline(candidate_id),
    job_id TEXT NOT NULL,
    interviewer_email TEXT NOT NULL,
    proposed_slots JSONB NOT NULL,
    chosen_slot TIMESTAMP WITH TIME ZONE,
    meeting_link TEXT,
    status TEXT DEFAULT 'proposed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 4: Offer Letters
CREATE TABLE IF NOT EXISTS offer_letters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id TEXT NOT NULL REFERENCES candidate_pipeline(candidate_id),
    job_id TEXT NOT NULL,
    offer_text TEXT NOT NULL,
    offer_pdf_path TEXT,
    compensation_json JSONB NOT NULL,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 5: Candidate Risk Signals
CREATE TABLE IF NOT EXISTS candidate_risk_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id TEXT NOT NULL REFERENCES candidate_pipeline(candidate_id),
    risk_score INTEGER NOT NULL CHECK (risk_score >= 0 AND risk_score <= 100),
    reasons TEXT[] NOT NULL,
    last_response_at TIMESTAMP WITH TIME ZONE,
    response_gap_hours INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_touchpoints_candidate ON candidate_touchpoints(candidate_id);
CREATE INDEX IF NOT EXISTS idx_touchpoints_created ON candidate_touchpoints(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_interview_slots_candidate ON interview_slots(candidate_id);
CREATE INDEX IF NOT EXISTS idx_offer_letters_candidate ON offer_letters(candidate_id);
CREATE INDEX IF NOT EXISTS idx_risk_signals_candidate ON candidate_risk_signals(candidate_id);

-- Enable Row Level Security (optional, but recommended)
ALTER TABLE candidate_pipeline ENABLE ROW LEVEL SECURITY;
ALTER TABLE candidate_touchpoints ENABLE ROW LEVEL SECURITY;
ALTER TABLE interview_slots ENABLE ROW LEVEL SECURITY;
ALTER TABLE offer_letters ENABLE ROW LEVEL SECURITY;
ALTER TABLE candidate_risk_signals ENABLE ROW LEVEL SECURITY;

-- Create policies (allow all for testing - restrict in production!)
CREATE POLICY "Allow all operations" ON candidate_pipeline FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON candidate_touchpoints FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON interview_slots FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON offer_letters FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON candidate_risk_signals FOR ALL USING (true);
