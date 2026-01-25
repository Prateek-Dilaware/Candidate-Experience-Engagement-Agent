"""Database models (Pydantic) for Supabase tables."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from src.config.constants import (
    CandidateStage,
    Channel,
    TouchpointType,
    Sentiment,
    DeliveryStatus,
    InterviewStatus,
    OfferStatus,
)


class CandidatePipeline(BaseModel):
    """Candidate pipeline record."""
    candidate_id: str
    job_id: str
    stage: CandidateStage
    stage_updated_at: datetime
    preferred_channel: Channel
    timezone: str = "Asia/Kolkata"
    created_at: Optional[datetime] = None


class CandidateTouchpoint(BaseModel):
    """Candidate touchpoint/interaction record."""
    id: Optional[str] = None
    candidate_id: str
    type: TouchpointType
    channel: Channel
    message: str
    sentiment: Optional[Sentiment] = None
    delivery_status: DeliveryStatus = DeliveryStatus.QUEUED
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None


class InterviewSlot(BaseModel):
    """Interview scheduling record."""
    id: Optional[str] = None
    candidate_id: str
    job_id: str
    interviewer_email: str
    proposed_slots: List[str]  # ISO timestamp strings
    chosen_slot: Optional[str] = None
    meeting_link: Optional[str] = None
    status: InterviewStatus = InterviewStatus.PROPOSED
    created_at: Optional[datetime] = None


class OfferLetter(BaseModel):
    """Offer letter record."""
    id: Optional[str] = None
    candidate_id: str
    job_id: str
    offer_text: str
    offer_pdf_path: Optional[str] = None
    compensation_json: Dict[str, Any]
    status: OfferStatus = OfferStatus.DRAFT
    created_at: Optional[datetime] = None


class CandidateRiskSignal(BaseModel):
    """Candidate risk/drop-off signal record."""
    id: Optional[str] = None
    candidate_id: str
    risk_score: int = Field(ge=0, le=100)
    reasons: List[str]
    last_response_at: Optional[datetime] = None
    response_gap_hours: Optional[int] = None
    created_at: Optional[datetime] = None
