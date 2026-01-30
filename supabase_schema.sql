-- ================================
-- DROP OLD TABLES (if exist)
-- ================================
DROP TABLE IF EXISTS public.offer_letters CASCADE;
DROP TABLE IF EXISTS public.interview_slots CASCADE;
DROP TABLE IF EXISTS public.candidate_risk_signals CASCADE;
DROP TABLE IF EXISTS public.candidate_touchpoints CASCADE;
DROP TABLE IF EXISTS public.candidate_pipeline CASCADE;
DROP TABLE IF EXISTS public.jobs CASCADE;
DROP TABLE IF EXISTS public.candidate_profiles CASCADE;

-- ================================
-- 1. Candidate Profiles
-- ================================
CREATE TABLE public.candidate_profiles (
  candidate_id text PRIMARY KEY,
  full_name text NOT NULL,
  email text UNIQUE NOT NULL,
  whatsapp_number TEXT
    CHECK (whatsapp_number ~ '^[0-9]{10}$'),
  preferred_channel text NOT NULL DEFAULT 'email'
    CHECK (preferred_channel IN ('email','whatsapp','sms')),
  created_at timestamptz DEFAULT now()
);


-- ================================
-- 2. Jobs
-- ================================
CREATE TABLE public.jobs (
  job_id text PRIMARY KEY,
  title text NOT NULL,
  interviewer_email text NOT NULL,
  ctc numeric,
  created_at timestamptz DEFAULT now()
);

-- ================================
-- 3. Candidate Pipeline
-- ================================
CREATE TABLE public.candidate_pipeline (
  candidate_id text NOT NULL,
  job_id text NOT NULL,
  stage text NOT NULL CHECK (stage IN (
    'APPLIED','SCREENED','INTERVIEW_SCHEDULED','INTERVIEWED',
    'OFFERED','OFFER_ACCEPTED','ONBOARDING',
    'CLOSED_REJECTED','CLOSED_WITHDRAWN'
  )),
  stage_updated_at timestamptz NOT NULL,
  preferred_channel text NOT NULL DEFAULT 'email'
    CHECK (preferred_channel IN ('email','whatsapp','sms')),
  timezone text DEFAULT 'Asia/Kolkata',
  created_at timestamptz DEFAULT now(),
  PRIMARY KEY (candidate_id, job_id),
  FOREIGN KEY (candidate_id)
    REFERENCES public.candidate_profiles(candidate_id)
    ON DELETE CASCADE,
  FOREIGN KEY (job_id)
    REFERENCES public.jobs(job_id)
    ON DELETE CASCADE
);

-- ================================
-- 4. Candidate Touchpoints
-- ================================
CREATE TABLE public.candidate_touchpoints (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id text NOT NULL,
  job_id text NOT NULL,
  stage text NOT NULL CHECK (stage IN (
    'APPLIED','SCREENED','INTERVIEW_SCHEDULED','INTERVIEWED',
    'OFFERED','OFFER_ACCEPTED','ONBOARDING',
    'CLOSED_REJECTED','CLOSED_WITHDRAWN'
  )),
  type text NOT NULL,
  channel text NOT NULL CHECK (channel IN ('email','whatsapp','sms')),
  message text NOT NULL,
  sentiment text CHECK (sentiment IN ('positive','neutral','negative')),
  delivery_status text NOT NULL DEFAULT 'queued'
    CHECK (delivery_status IN ('queued','sent','failed')),
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now(),
  FOREIGN KEY (candidate_id, job_id)
    REFERENCES public.candidate_pipeline(candidate_id, job_id)
    ON DELETE CASCADE
);

-- ================================
-- 5. Candidate Risk Signals
-- ================================
CREATE TABLE public.candidate_risk_signals (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id text NOT NULL,
  job_id text NOT NULL,
  stage text NOT NULL CHECK (stage IN (
    'APPLIED','SCREENED','INTERVIEW_SCHEDULED','INTERVIEWED',
    'OFFERED','OFFER_ACCEPTED','ONBOARDING',
    'CLOSED_REJECTED','CLOSED_WITHDRAWN'
  )),
  risk_score int NOT NULL CHECK (risk_score BETWEEN 0 AND 100),
  reasons text[] NOT NULL,
  last_response_at timestamptz,
  response_gap_hours int,
  created_at timestamptz DEFAULT now(),
  FOREIGN KEY (candidate_id, job_id)
    REFERENCES public.candidate_pipeline(candidate_id, job_id)
    ON DELETE CASCADE
);

-- ================================
-- 6. Interview Slots (Calendar Ready)
-- ================================
CREATE TABLE public.interview_slots (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id text NOT NULL,
  job_id text NOT NULL,
  interviewer_email text NOT NULL,
  proposed_slots timestamptz[] NOT NULL,
  chosen_slot timestamptz,
  meeting_link text,
  status text NOT NULL DEFAULT 'proposed'
    CHECK (status IN ('proposed','confirmed','cancelled')),
  created_at timestamptz DEFAULT now(),
  FOREIGN KEY (candidate_id, job_id)
    REFERENCES public.candidate_pipeline(candidate_id, job_id)
    ON DELETE CASCADE
);

-- ================================
-- 7. Offer Letters
-- ================================
CREATE TABLE public.offer_letters (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id text NOT NULL,
  job_id text NOT NULL,
  offer_text text NOT NULL,
  offer_pdf_path text,
  status text NOT NULL DEFAULT 'draft'
    CHECK (status IN ('draft','sent','accepted','rejected')),
  created_at timestamptz DEFAULT now(),
  FOREIGN KEY (candidate_id, job_id)
    REFERENCES public.candidate_pipeline(candidate_id, job_id)
    ON DELETE CASCADE
);
