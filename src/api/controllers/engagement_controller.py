"""Engagement controller - Orchestrates business logic for engagement APIs."""
from typing import List
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
    TimelineEvent,
    CandidateTimelineResponse,
)
from src.services.pipeline_service import PipelineService
from src.services.template_service import TemplateService
from src.services.messaging_service import MessagingService
from src.services.scheduling_service import SchedulingService
from src.services.offer_service import OfferService
from src.services.risk_service import RiskService
from src.config import CandidateStage, MessageType


class EngagementController:
    """Controller for candidate engagement operations."""
    
    def __init__(self):
        self.pipeline_service = PipelineService()
        self.template_service = TemplateService()
        self.messaging_service = MessagingService()
        self.scheduling_service = SchedulingService()
        self.offer_service = OfferService()
        self.risk_service = RiskService()
    
    async def update_candidate_stage(
        self, 
        request: UpdateStageRequest
    ) -> UpdateStageResponse:
        """
        Update candidate stage and send notification via LangGraph workflow.
        """
        try:
            # Step 1: Get candidate info
            candidate = await self.pipeline_service.get_candidate(request.candidateId)
            
            # If candidate doesn't exist, create them (for testing)
            if not candidate:
                candidate = await self.pipeline_service.create_candidate(
                    candidate_id=request.candidateId,
                    job_id=request.jobId,
                    stage=CandidateStage.APPLIED
                )
            
            # Step 2: Update stage with validation
            updated_candidate = await self.pipeline_service.update_candidate_stage(
                candidate_id=request.candidateId,
                new_stage=request.newStage
            )
            
            # Step 3: Trigger LangGraph Workflow
            try:
                from src.agents.engagement_flow import EngagementGraph
                graph = EngagementGraph()
                
                # Run the graph (fire and forget for now, or await)
                await graph.run_stage_update(
                    candidate_id=request.candidateId,
                    candidate_name="Candidate", # TODO: Get from profile
                    role_title="Software Engineer", # TODO: Get from job
                    new_stage=request.newStage,
                    channel=updated_candidate.get("preferred_channel", "email")
                )
            except Exception as graph_error:
                print(f"⚠️ Workflow Error: {graph_error}. Manual fallbacks normally trigger here.")
            
            # Step 4: Return response
            return UpdateStageResponse(
                candidateId=request.candidateId,
                stage=CandidateStage(updated_candidate["stage"]),
                stageUpdatedAt=updated_candidate["stage_updated_at"]
            )
            
        except Exception as e:
            raise Exception(f"Failed to update candidate stage: {str(e)}")
    
    async def send_status_update(
        self,
        request: SendStatusRequest
    ) -> SendStatusResponse:
        """
        Send personalized status update to candidate.
        
        Process:
        1. Get candidate info
        2. Determine appropriate channel
        3. Generate message based on type
        4. Send message
        5. Return confirmation
        """
        try:
            # Get candidate info
            candidate = await self.pipeline_service.get_candidate_info(request.candidateId)
            
            current_stage = CandidateStage(candidate["stage"])
            
            # Generate message based on message type
            if request.messageType == MessageType.STAGE_UPDATE:
                message = self.template_service.generate_stage_update_message(
                    candidate_name="Candidate",
                    role_title="Software Engineer",
                    new_stage=current_stage
                )
            else:
                # For other message types, use generic template
                template = self.template_service.get_template(
                    request.messageType,
                    current_stage
                )
                message = self.template_service.render_template(
                    template,
                    {
                        "candidateName": "Candidate",
                        "roleTitle": "Software Engineer"
                    }
                )
            
            # Send message
            result = await self.messaging_service.send_stage_update_notification(
                candidate_id=request.candidateId,
                message=message,
                preferred_channel=candidate.get("preferred_channel", "email"),
                channel_override=request.channelOverride,
                metadata={
                    "message_type": request.messageType.value,
                    "current_stage": current_stage.value
                }
            )
            
            return SendStatusResponse(
                sent=result["sent"],
                channel=result["channel"],
                message=message
            )
            
        except Exception as e:
            raise Exception(f"Failed to send status update: {str(e)}")
    
    async def get_candidate_timeline(
        self,
        candidate_id: str
    ) -> CandidateTimelineResponse:
        """
        Get complete timeline of candidate interactions.
        
        Returns all touchpoints, stage changes, and events
        """
        try:
            from src.db import get_supabase
            supabase = get_supabase()
            
            # Get all touchpoints for this candidate
            touchpoints_response = supabase.table("candidate_touchpoints").select(
                "*"
            ).eq("candidate_id", candidate_id).order(
                "created_at", desc=True
            ).execute()
            
            events: List[TimelineEvent] = []
            
            for touchpoint in touchpoints_response.data:
                events.append(TimelineEvent(
                    id=touchpoint.get("id"),
                    type=touchpoint.get("type"),
                    timestamp=touchpoint.get("created_at"),
                    channel=touchpoint.get("channel"),
                    message=touchpoint.get("message"),
                    metadata=touchpoint.get("metadata")
                ))
            
            return CandidateTimelineResponse(
                candidateId=candidate_id,
                events=events
            )
            
        except Exception as e:
            raise Exception(f"Failed to get candidate timeline: {str(e)}")
    
    async def propose_interview_slots(
        self,
        request: ProposeSlotsRequest
    ) -> ProposeSlotsResponse:
        """
        Propose interview time slots to candidate.
        """
        try:
            result = await self.scheduling_service.propose_interview_slots(
                candidate_id=request.candidateId,
                job_id=request.jobId,
                interviewer_email=request.interviewerEmail,
                start_date=request.window.startDate,
                end_date=request.window.endDate,
                duration_minutes=request.durationMinutes
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
        """
        Confirm candidate's chosen interview slot.
        """
        try:
            result = await self.scheduling_service.confirm_interview_slot(
                candidate_id=request.candidateId,
                chosen_slot=request.slot
            )
            
            return ConfirmInterviewResponse(
                status=result["status"],
                meetingLink=result["meeting_link"],
                remindersScheduled=result["reminders_scheduled"]
            )
            
        except Exception as e:
            raise Exception(f"Failed to confirm interview: {str(e)}")
    
    async def generate_offer_letter(
        self,
        request: GenerateOfferRequest
    ) -> GenerateOfferResponse:
        """
        Generate personalized offer letter.
        """
        try:
            # Verify candidate is at appropriate stage
            candidate = await self.pipeline_service.get_candidate_info(request.candidateId)
            current_stage = CandidateStage(candidate["stage"])
            
            # Check if candidate is at least INTERVIEWED
            stage_index = [
                CandidateStage.APPLIED,
                CandidateStage.SCREENED,
                CandidateStage.INTERVIEW_SCHEDULED,
                CandidateStage.INTERVIEWED,
                CandidateStage.OFFERED,
                CandidateStage.OFFER_ACCEPTED,
                CandidateStage.ONBOARDING,
            ].index(current_stage) if current_stage in [
                CandidateStage.APPLIED,
                CandidateStage.SCREENED,
                CandidateStage.INTERVIEW_SCHEDULED,
                CandidateStage.INTERVIEWED,
                CandidateStage.OFFERED,
                CandidateStage.OFFER_ACCEPTED,
                CandidateStage.ONBOARDING,
            ] else -1
            
            interviewed_index = 3  # INTERVIEWED position
            
            if stage_index < interviewed_index:
                raise Exception("Offer can only be generated for candidates who have been interviewed")
            
            # Generate offer
            result = await self.offer_service.generate_offer_letter(
                candidate_id=request.candidateId,
                job_id=request.jobId,
                compensation=request.compensation.model_dump(),
                template_id=request.templateId
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
        """
        Evaluate candidate drop-off risk.
        """
        try:
            result = await self.risk_service.evaluate_candidate_risk(
                candidate_id=request.candidateId
            )
            
            return RiskEvaluationResponse(
                riskScore=result["risk_score"],
                reasons=result["reasons"],
                alertTriggered=result["alert_triggered"]
            )
            
        except Exception as e:
            raise Exception(f"Failed to evaluate risk: {str(e)}")
