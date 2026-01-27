"""Engagement API routes."""
from fastapi import APIRouter, HTTPException
from src.schemas.engagement_schema import (
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
    CandidatePipelineInfoResponse,
)
from src.api.controllers.engagement_controller import EngagementController

router = APIRouter()
controller = EngagementController()


@router.get("/metadata")
async def get_metadata():
    try:
        return await controller.get_metadata()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/stage/update", response_model=UpdateStageResponse)
async def update_candidate_stage(request: UpdateStageRequest):
    try:
        return await controller.update_candidate_stage(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/status/send", response_model=SendStatusResponse)
async def send_status_update(request: SendStatusRequest):
    try:
        return await controller.send_status_update(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/interview/propose-slots", response_model=ProposeSlotsResponse)
async def propose_interview_slots(request: ProposeSlotsRequest):
    try:
        return await controller.propose_interview_slots(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/interview/confirm", response_model=ConfirmInterviewResponse)
async def confirm_interview_slot(request: ConfirmInterviewRequest):
    try:
        return await controller.confirm_interview_slot(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/offer/generate", response_model=GenerateOfferResponse)
async def generate_offer_letter(request: GenerateOfferRequest):
    try:
        return await controller.generate_offer_letter(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/risk/evaluate", response_model=RiskEvaluationResponse)
async def evaluate_candidate_risk(request: RiskEvaluationRequest):
    try:
        return await controller.evaluate_candidate_risk(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/candidate/{candidateId}/job/{jobId}/timeline", response_model=CandidateTimelineResponse)
async def get_candidate_timeline(candidateId: str, jobId: str):
    try:
        return await controller.get_candidate_timeline(candidateId, jobId)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/candidate/{candidateId}/job/{jobId}/pipeline", response_model=CandidatePipelineInfoResponse)
async def get_candidate_pipeline_info(candidateId: str, jobId: str):
    try:
        return await controller.get_candidate_pipeline_info(candidateId, jobId)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
