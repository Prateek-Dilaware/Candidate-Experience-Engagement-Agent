"""Database models (Pydantic) for Supabase tables."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from src.config.constants import (
    CandidateStage,
    Channel,
    TouchpointType,
    Sentiment,
    DeliveryStatus,
    InterviewStatus,
    OfferStatus,
)


class CandidateProfile(BaseModel):
    candidate_id: str
    full_name: str
    email: EmailStr
    created_at: Optional[datetime] = None


class Job(BaseModel):
    job_id: str
    title: str
    interviewer_email: EmailStr
    created_at: Optional[datetime] = None


class CandidatePipeline(BaseModel):
    candidate_id: str
    job_id: str
    stage: CandidateStage
    stage_updated_at: datetime
    preferred_channel: Channel
    timezone: str = "Asia/Kolkata"
    created_at: Optional[datetime] = None


class CandidateTouchpoint(BaseModel):
    id: Optional[str] = None
    candidate_id: str
    job_id: str
    stage: CandidateStage
    type: TouchpointType
    channel: Channel
    message: str
    sentiment: Optional[Sentiment] = None
    delivery_status: DeliveryStatus = DeliveryStatus.QUEUED
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None


class CandidateRiskSignal(BaseModel):
    id: Optional[str] = None
    candidate_id: str
    job_id: str
    stage: CandidateStage
    risk_score: int = Field(ge=0, le=100)
    reasons: List[str]
    last_response_at: Optional[datetime] = None
    response_gap_hours: Optional[int] = None
    created_at: Optional[datetime] = None


class InterviewSlot(BaseModel):
    id: Optional[str] = None
    candidate_id: str
    job_id: str
    interviewer_email: EmailStr
    proposed_slots: List[str]  # ['10:00-12:00','15:00-17:00','18:00-20:00']
    chosen_slot: Optional[str] = None
    meeting_link: Optional[str] = None
    status: InterviewStatus = InterviewStatus.PROPOSED
    created_at: Optional[datetime] = None


class OfferLetter(BaseModel):
    id: Optional[str] = None
    candidate_id: str
    job_id: str
    offer_text: str
    offer_pdf_path: Optional[str] = None
    status: OfferStatus = OfferStatus.DRAFT
    created_at: Optional[datetime] = None
