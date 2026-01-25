"""Engagement API routes."""
from fastapi import APIRouter, HTTPException
from src.schemas import (
    UpdateStageRequest,
    UpdateStageResponse,
    SendStatusRequest,
    SendStatusResponse,
    ProposeSlotsRequest,
    ProposeSlotsResponse,
    ConfirmInterviewRequest,
    ConfirmInterviewResponse,
    GenerateOfferRequest,
    GenerateOfferResponse,
    RiskEvaluationRequest,
    RiskEvaluationResponse,
    CandidateTimelineResponse,
)
from src.api.controllers.engagement_controller import EngagementController

router = APIRouter()
controller = EngagementController()


@router.post("/stage/update", response_model=UpdateStageResponse)
async def update_candidate_stage(request: UpdateStageRequest):
    """Update candidate pipeline stage."""
    try:
        return await controller.update_candidate_stage(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/status/send", response_model=SendStatusResponse)
async def send_status_update(request: SendStatusRequest):
    """Send personalized status update to candidate."""
    try:
        return await controller.send_status_update(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/interview/propose-slots", response_model=ProposeSlotsResponse)
async def propose_interview_slots(request: ProposeSlotsRequest):
    """Propose interview time slots to candidate."""
    try:
        return await controller.propose_interview_slots(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/interview/confirm", response_model=ConfirmInterviewResponse)
async def confirm_interview_slot(request: ConfirmInterviewRequest):
    """Confirm candidate's chosen interview slot."""
    try:
        return await controller.confirm_interview_slot(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/offer/generate", response_model=GenerateOfferResponse)
async def generate_offer_letter(request: GenerateOfferRequest):
    """Generate personalized offer letter for candidate."""
    try:
        return await controller.generate_offer_letter(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/risk/evaluate", response_model=RiskEvaluationResponse)
async def evaluate_candidate_risk(request: RiskEvaluationRequest):
    """Evaluate candidate drop-off risk and trigger alerts."""
    try:
        return await controller.evaluate_candidate_risk(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/candidate/{candidateId}/timeline", response_model=CandidateTimelineResponse)
async def get_candidate_timeline(candidateId: str):
    """Get complete timeline of candidate interactions."""
    try:
        return await controller.get_candidate_timeline(candidateId)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
