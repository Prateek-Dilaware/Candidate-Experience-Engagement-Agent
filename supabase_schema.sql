-- 1. Candidate Profiles
CREATE TABLE public.candidate_profiles (
  candidate_id TEXT PRIMARY KEY,
  full_name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Jobs
CREATE TABLE public.jobs (
  job_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  interviewer_email TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. Candidate Pipeline
CREATE TABLE public.candidate_pipeline (
  candidate_id TEXT NOT NULL,
  job_id TEXT NOT NULL,

  stage TEXT NOT NULL CHECK (
    stage IN (
      'APPLIED',
      'SCREENED',
      'INTERVIEW_SCHEDULED',
      'INTERVIEWED',
      'OFFERED',
      'OFFER_ACCEPTED',
      'ONBOARDING',
      'CLOSED_REJECTED',
      'CLOSED_WITHDRAWN'
    )
  ),

  stage_updated_at TIMESTAMPTZ NOT NULL,

  preferred_channel TEXT DEFAULT 'email'
    CHECK (preferred_channel IN ('email', 'whatsapp', 'sms')) NOT NULL,

  timezone TEXT DEFAULT 'Asia/Kolkata',

  created_at TIMESTAMPTZ DEFAULT now(),

  PRIMARY KEY (candidate_id, job_id),

  FOREIGN KEY (candidate_id)
    REFERENCES public.candidate_profiles(candidate_id)
    ON DELETE CASCADE,

  FOREIGN KEY (job_id)
    REFERENCES public.jobs(job_id)
    ON DELETE CASCADE
);

-- 4. Candidate Touchpoints (messages)
CREATE TABLE public.candidate_touchpoints (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id TEXT NOT NULL,
  job_id TEXT NOT NULL,

  stage TEXT NOT NULL CHECK (
    stage IN (
      'APPLIED',
      'SCREENED',
      'INTERVIEW_SCHEDULED',
      'INTERVIEWED',
      'OFFERED',
      'OFFER_ACCEPTED',
      'ONBOARDING',
      'CLOSED_REJECTED',
      'CLOSED_WITHDRAWN'
    )
  ),

  type TEXT NOT NULL,

  channel TEXT NOT NULL CHECK (channel IN ('email', 'whatsapp', 'sms')),

  message TEXT NOT NULL,

  sentiment TEXT CHECK (sentiment IN ('positive', 'neutral', 'negative')),

  delivery_status TEXT DEFAULT 'queued'
    CHECK (delivery_status IN ('queued', 'sent', 'failed')) NOT NULL,

  metadata JSONB DEFAULT '{}'::jsonb,

  created_at TIMESTAMPTZ DEFAULT now(),

  FOREIGN KEY (candidate_id, job_id)
    REFERENCES public.candidate_pipeline(candidate_id, job_id)
    ON DELETE CASCADE
);

-- 5. Candidate Risk Signals
CREATE TABLE public.candidate_risk_signals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id TEXT NOT NULL,
  job_id TEXT NOT NULL,

  stage TEXT NOT NULL CHECK (
    stage IN (
      'APPLIED',
      'SCREENED',
      'INTERVIEW_SCHEDULED',
      'INTERVIEWED',
      'OFFERED',
      'OFFER_ACCEPTED',
      'ONBOARDING',
      'CLOSED_REJECTED',
      'CLOSED_WITHDRAWN'
    )
  ),

  risk_score INT NOT NULL CHECK (risk_score >= 0 AND risk_score <= 100),

  reasons TEXT[] NOT NULL,

  last_response_at TIMESTAMPTZ,

  response_gap_hours INT,

  created_at TIMESTAMPTZ DEFAULT now(),

  FOREIGN KEY (candidate_id, job_id)
    REFERENCES public.candidate_pipeline(candidate_id, job_id)
    ON DELETE CASCADE
);

-- 6. Interview Slots
CREATE TABLE public.interview_slots (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id TEXT NOT NULL,
  job_id TEXT NOT NULL,

  interviewer_email TEXT NOT NULL,

  proposed_slots TEXT[] NOT NULL CHECK (
    proposed_slots <@ ARRAY['10:00-12:00','15:00-17:00','18:00-20:00']
  ),

  chosen_slot TEXT CHECK (
    chosen_slot IN ('10:00-12:00','15:00-17:00','18:00-20:00')
  ),

  meeting_link TEXT,

  status TEXT DEFAULT 'proposed'
    CHECK (status IN ('proposed','confirmed','cancelled')) NOT NULL,

  created_at TIMESTAMPTZ DEFAULT now(),

  FOREIGN KEY (candidate_id, job_id)
    REFERENCES public.candidate_pipeline(candidate_id, job_id)
    ON DELETE CASCADE
);

-- 7. Offer Letters
CREATE TABLE public.offer_letters (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id TEXT NOT NULL,
  job_id TEXT NOT NULL,

  offer_text TEXT NOT NULL,

  offer_pdf_path TEXT,

  status TEXT DEFAULT 'draft'
    CHECK (status IN ('draft', 'sent', 'accepted', 'rejected')) NOT NULL,

  created_at TIMESTAMPTZ DEFAULT now(),

  FOREIGN KEY (candidate_id, job_id)
    REFERENCES public.candidate_pipeline(candidate_id, job_id)
    ON DELETE CASCADE
);
