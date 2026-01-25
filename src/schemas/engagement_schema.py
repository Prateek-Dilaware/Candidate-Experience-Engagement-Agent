"""Request and response schemas for engagement APIs."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from src.config.constants import CandidateStage, Channel, MessageType


# ============= API 1: Update Stage =============
class UpdateStageRequest(BaseModel):
    """Request to update candidate stage."""
    candidateId: str
    jobId: str
    newStage: CandidateStage


class UpdateStageResponse(BaseModel):
    """Response after updating candidate stage."""
    candidateId: str
    stage: CandidateStage
    stageUpdatedAt: str  # ISO timestamp


# ============= API 2: Send Status Update =============
class SendStatusRequest(BaseModel):
    """Request to send status update."""
    candidateId: str
    messageType: MessageType
    channelOverride: Optional[Channel] = None


class SendStatusResponse(BaseModel):
    """Response after sending status update."""
    sent: bool
    channel: Channel
    message: str


# ============= API 3: Propose Interview Slots =============
class ProposeSlotWindow(BaseModel):
    """Time window for proposing slots."""
    startDate: str  # YYYY-MM-DD
    endDate: str    # YYYY-MM-DD


class ProposeSlotsRequest(BaseModel):
    """Request to propose interview slots."""
    candidateId: str
    jobId: str
    interviewerEmail: str
    durationMinutes: int = 30
    window: ProposeSlotWindow


class ProposeSlotsResponse(BaseModel):
    """Response with proposed interview slots."""
    status: str = "proposed"
    slots: List[str]  # ISO timestamps


# ============= API 4: Confirm Interview =============
class ConfirmInterviewRequest(BaseModel):
    """Request to confirm interview slot."""
    candidateId: str
    slot: str  # ISO timestamp


class ConfirmInterviewResponse(BaseModel):
    """Response after confirming interview."""
    status: str = "confirmed"
    meetingLink: str
    remindersScheduled: List[str]  # e.g., ["24h", "1h"]


# ============= API 5: Generate Offer =============
class CompensationDetails(BaseModel):
    """Compensation details for offer."""
    ctc: int
    joiningBonus: int
    joiningDate: str  # YYYY-MM-DD


class GenerateOfferRequest(BaseModel):
    """Request to generate offer letter."""
    candidateId: str
    jobId: str
    compensation: CompensationDetails
    templateId: str = "OFFER_STD_V1"


class GenerateOfferResponse(BaseModel):
    """Response with generated offer."""
    offerId: str
    status: str = "draft"
    offerPreview: str


# ============= API 6: Risk Evaluation =============
class RiskEvaluationRequest(BaseModel):
    """Request to evaluate candidate risk."""
    candidateId: str


class RiskEvaluationResponse(BaseModel):
    """Response with risk assessment."""
    riskScore: int
    reasons: List[str]
    alertTriggered: bool


# ============= API 7: Candidate Timeline =============
class TimelineEvent(BaseModel):
    """Single timeline event."""
    id: Optional[str] = None
    type: str
    timestamp: str
    channel: Optional[str] = None
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CandidateTimelineResponse(BaseModel):
    """Response with candidate timeline."""
    candidateId: str
    events: List[TimelineEvent]
