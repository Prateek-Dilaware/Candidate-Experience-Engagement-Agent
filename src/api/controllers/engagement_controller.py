"""Engagement controller - Orchestrates candidate engagement flow."""
from typing import List
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
    TimelineEvent,
    CandidatePipelineInfoResponse,
)
from src.services.pipeline_service import PipelineService
from src.services.messaging_service import MessagingService
from src.services.candidate_data_service import CandidateDataService
from src.services.scheduling_service import SchedulingService
from src.services.offer_service import OfferService
from src.services.risk_service import RiskService
from src.services.template_service import TemplateService
from src.config.constants import CandidateStage, MessageType


class EngagementController:
    """Controller for candidate engagement operations."""

    def __init__(self):
        self.pipeline_service = PipelineService()
        self.messaging_service = MessagingService()
        self.candidate_data_service = CandidateDataService()
        self.scheduling_service = SchedulingService()
        self.offer_service = OfferService()
        self.risk_service = RiskService()
        self.template_service = TemplateService()

    async def update_candidate_stage(
        self,
        request: UpdateStageRequest
    ) -> UpdateStageResponse:
        try:
            # 1. Candidate profile
            candidate_profile = await self.candidate_data_service.get_candidate_profile(
                request.candidateId
            )
            if not candidate_profile:
                raise Exception("Candidate profile not found")

            candidate_name = candidate_profile["full_name"]

            # 2. Job details
            job_details = await self.candidate_data_service.get_job_details(
                request.jobId
            )
            if not job_details:
                raise Exception("Job not found")

            job_title = job_details["title"]

            # 3. Pipeline
            candidate = await self.pipeline_service.get_candidate(
                request.candidateId,
                request.jobId
            )

            if not candidate:
                candidate = await self.pipeline_service.create_candidate(
                    candidate_id=request.candidateId,
                    job_id=request.jobId,
                    stage=CandidateStage.APPLIED
                )

            # 4. Update stage
            updated_candidate = await self.pipeline_service.update_candidate_stage(
                candidate_id=request.candidateId,
                job_id=request.jobId,
                new_stage=request.newStage
            )

            # 5. Send message
            await self.messaging_service.send_stage_update_notification(
                candidate_id=request.candidateId,
                job_id=request.jobId,
                new_stage=request.newStage,
                preferred_channel=updated_candidate["preferred_channel"],
                metadata={
                    "candidate_name": candidate_name,
                    "job_title": job_title,
                    "stage_transition": {
                        "from": candidate["stage"],
                        "to": request.newStage.value
                    },
                }
            )

            return UpdateStageResponse(
                candidateId=request.candidateId,
                jobId=request.jobId,
                stage=CandidateStage(updated_candidate["stage"]),
                stageUpdatedAt=updated_candidate["stage_updated_at"]
            )

        except Exception as e:
            raise Exception(f"Failed to update candidate stage: {str(e)}")

    async def send_status_update(
        self,
        request: SendStatusRequest
    ) -> SendStatusResponse:
        try:
            # 1. Fetch candidate profile for name
            candidate_profile = await self.candidate_data_service.get_candidate_profile(
                request.candidateId
            )
            candidate_name = candidate_profile["full_name"] if candidate_profile else "Candidate"

            # 2. Fetch job details for title
            job_details = await self.candidate_data_service.get_job_details(
                request.jobId
            )
            role_title = job_details["title"] if job_details else "Position"

            # 3. Fetch current stage from pipeline
            candidate = await self.pipeline_service.get_candidate_info(
                request.candidateId,
                request.jobId
            )

            # Generate message with real data
            message = self.template_service.generate_stage_update_message(
                candidate_name=candidate_name,
                role_title=role_title,
                new_stage=CandidateStage(candidate["stage"])
            )

            result = await self.messaging_service.send_message(
                candidate_id=request.candidateId,
                job_id=request.jobId,
                stage=CandidateStage(candidate["stage"]),
                message=message,
                preferred_channel=candidate["preferred_channel"],
                message_type=request.messageType,
                channel_override=request.channelOverride
            )

            return SendStatusResponse(
                sent=result["sent"],
                channel=result["channel"],
                message=result["message"]
            )
        except Exception as e:
            raise Exception(f"Failed to send status update: {str(e)}")

    async def propose_interview_slots(
        self,
        request: ProposeSlotsRequest
    ) -> ProposeSlotsResponse:
        try:
            result = await self.scheduling_service.propose_interview_slots(
                candidate_id=request.candidateId,
                job_id=request.jobId,
                date=request.date
            )
            return ProposeSlotsResponse(
                status=result["status"],
                slots=result["slots"]
            )
        except Exception as e:
            raise Exception(f"Failed to propose interview slots: {str(e)}")

    async def confirm_interview_slot(
        self,
        request: ConfirmInterviewRequest
    ) -> ConfirmInterviewResponse:
        try:
            result = await self.scheduling_service.confirm_interview_slot(
                candidate_id=request.candidateId,
                job_id=request.jobId,
                chosen_slot=request.chosenSlot
            )
            return ConfirmInterviewResponse(
                status=result["status"],
                meetingLink=result["meeting_link"],
                remindersScheduled=["24h", "1h"]  # Default reminders
            )
        except Exception as e:
            raise Exception(f"Failed to confirm interview slot: {str(e)}")

    async def generate_offer_letter(
        self,
        request: GenerateOfferRequest
    ) -> GenerateOfferResponse:
        try:
            result = await self.offer_service.generate_offer_letter(
                candidate_id=request.candidateId,
                job_id=request.jobId,
                joining_date=request.joiningDate
            )
            return GenerateOfferResponse(
                offerId=result["offer_id"],
                status=result["status"],
                offerPreview=result["offer_preview"]
            )
        except Exception as e:
            raise Exception(f"Failed to generate offer: {str(e)}")

    async def evaluate_candidate_risk(
        self,
        request: RiskEvaluationRequest
    ) -> RiskEvaluationResponse:
        try:
            result = await self.risk_service.evaluate_candidate_risk(
                candidate_id=request.candidateId,
                job_id=request.jobId
            )
            return RiskEvaluationResponse(
                riskScore=result["risk_score"],
                reasons=result["reasons"],
                alertTriggered=result["alert_triggered"]
            )
        except Exception as e:
            raise Exception(f"Failed to evaluate risk: {str(e)}")

    async def get_metadata(self) -> dict:
        """Fetch all metadata needed for the frontend (candidates, jobs, stages)."""
        try:
            candidates = await self.candidate_data_service.get_all_candidates()
            jobs = await self.candidate_data_service.get_all_jobs()
            stages = [stage.value for stage in CandidateStage]
            message_types = [m.value.lower() for m in MessageType]

            return {
                "candidates": candidates,
                "jobs": jobs,
                "stages": stages,
                "message_types": message_types
            }
        except Exception as e:
            raise Exception(f"Failed to fetch metadata: {str(e)}")

    async def get_candidate_timeline(
        self,
        candidate_id: str,
        job_id: str
    ) -> CandidateTimelineResponse:
        try:
            from src.db import get_supabase
            supabase = get_supabase()

            response = (
                supabase
                .table("candidate_touchpoints")
                .select("*")
                .eq("candidate_id", candidate_id)
                .eq("job_id", job_id)
                .order("created_at", desc=True)
                .execute()
            )

            events = []
            for tp in response.data:
                events.append(TimelineEvent(
                    id=tp.get("id"),
                    type=tp.get("type"),
                    timestamp=tp.get("created_at"),
                    stage=CandidateStage(tp.get("stage")) if tp.get("stage") else None,
                    channel=tp.get("channel"),
                    message=tp.get("message"),
                    metadata=tp.get("metadata")
                ))

            return CandidateTimelineResponse(
                candidateId=candidate_id,
                jobId=job_id,
                events=events
            )
        except Exception as e:
            raise Exception(f"Failed to get candidate timeline: {str(e)}")

    async def get_candidate_pipeline_info(
        self,
        candidate_id: str,
        job_id: str
    ) -> CandidatePipelineInfoResponse:
        try:
            info = await self.pipeline_service.get_candidate_info(candidate_id, job_id)
            return CandidatePipelineInfoResponse(**info)
        except Exception as e:
            raise Exception(f"Failed to get candidate pipeline info: {str(e)}")