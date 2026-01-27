"""Request and response schemas for engagement APIs."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from src.config.constants import CandidateStage, Channel, MessageType


# ============= API 1: Update Stage =============
class UpdateStageRequest(BaseModel):
    candidateId: str
    jobId: str
    newStage: CandidateStage


class UpdateStageResponse(BaseModel):
    candidateId: str
    jobId: str
    stage: CandidateStage
    stageUpdatedAt: str


# ============= API 2: Send Status Update =============
class SendStatusRequest(BaseModel):
    candidateId: str
    jobId: str
    messageType: MessageType
    channelOverride: Optional[Channel] = None


class SendStatusResponse(BaseModel):
    sent: bool
    channel: Channel
    message: str




# ============= API 3: Propose Interview Slots =============
class ProposeSlotsRequest(BaseModel):
    candidateId: str
    jobId: str
    date: str  # YYYY-MM-DD


class ProposeSlotsResponse(BaseModel):
    status: str = "proposed"
    slots: List[str]


# ============= API 4: Confirm Interview =============
class ConfirmInterviewRequest(BaseModel):
    candidateId: str
    jobId: str
    chosenSlot: str


class ConfirmInterviewResponse(BaseModel):
    status: str = "confirmed"
    meetingLink: str
    remindersScheduled: List[str]


# ============= API 5: Generate Offer =============
class GenerateOfferRequest(BaseModel):
    candidateId: str
    jobId: str
    joiningDate: str  # YYYY-MM-DD


class GenerateOfferResponse(BaseModel):
    offerId: str
    status: str
    offerPreview: str



# ============= API 6: Risk Evaluation =============
class RiskEvaluationRequest(BaseModel):
    candidateId: str
    jobId: str


class RiskEvaluationResponse(BaseModel):
    riskScore: int
    reasons: List[str]
    alertTriggered: bool


# ============= API 7: Candidate Timeline =============
class TimelineEvent(BaseModel):
    id: Optional[str] = None
    type: str
    timestamp: str
    stage: Optional[CandidateStage] = None
    channel: Optional[Channel] = None
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CandidateTimelineResponse(BaseModel):
    candidateId: str
    jobId: str
    events: List[TimelineEvent]


class CandidatePipelineInfoResponse(BaseModel):
    candidate_id: str
    job_id: str
    stage: CandidateStage
    preferred_channel: Channel
    timezone: str
    stage_updated_at: str
