"""Scheduling service - Manages interview scheduling."""
from datetime import datetime
from typing import List
from src.db import get_supabase
from src.config import InterviewStatus, CandidateStage, MessageType
from src.services.messaging_service import MessagingService
from src.services.pipeline_service import PipelineService

ALLOWED_SLOTS = ["10:00-12:00", "15:00-17:00", "18:00-20:00"]


class SchedulingService:
    """Service for interview scheduling operations."""

    def __init__(self):
        self.supabase = get_supabase()
        self.messaging_service = MessagingService()
        self.pipeline_service = PipelineService()

    def generate_time_slots(self, slots_per_day: int = 3) -> List[str]:
        """
        Generate interview slot windows (DB allowed values only).
        """
        return ALLOWED_SLOTS[:slots_per_day]

    async def propose_interview_slots(
        self,
        candidate_id: str,
        job_id: str,
        date: str
    ) -> dict:
        """
        Propose interview slots to candidate.
        """
        try:
            # 1. Fetch interviewer_email from jobs table
            job_resp = (
                self.supabase
                .table("jobs")
                .select("interviewer_email")
                .eq("job_id", job_id)
                .execute()
            )
            if not job_resp.data:
                raise Exception(f"Job not found: {job_id}")
            
            interviewer_email = job_resp.data[0]["interviewer_email"]

            # 2. Generate slots (allowed strings only for DB)
            proposed_slots = self.generate_time_slots()

            interview_data = {
                "candidate_id": candidate_id,
                "job_id": job_id,
                "interviewer_email": interviewer_email,
                "proposed_slots": proposed_slots,
                "meeting_link": date, # Store date here temporarily
                "status": InterviewStatus.PROPOSED.value,
                "created_at": datetime.utcnow().isoformat()
            }

            response = self.supabase.table("interview_slots").insert(
                interview_data
            ).execute()

            if not response.data:
                raise Exception("Failed to create interview slots")

            slots_list = "\n".join([f"- {slot}" for slot in proposed_slots])
            message = (
                f"Hi,\n\nWe would like to invite you for an interview on **{date}**.\n"
                "Please select a slot from the following options:\n\n"
                f"{slots_list}\n\n"
                "Reply with your chosen slot."
            )

            candidate_pipeline = await self.pipeline_service.get_candidate(candidate_id, job_id)
            preferred_channel = candidate_pipeline["preferred_channel"] if candidate_pipeline else "email"

            await self.messaging_service.send_message(
                candidate_id=candidate_id,
                job_id=job_id,
                stage=CandidateStage.SCREENED,
                message=message,
                preferred_channel=preferred_channel,
                message_type=MessageType.STAGE_UPDATE
            )

            return {
                "status": "proposed",
                "slots": proposed_slots,
                "interview_id": response.data[0]["id"]
            }

        except Exception as e:
            raise Exception(f"Error proposing interview slots: {str(e)}")

    async def confirm_interview_slot(
        self,
        candidate_id: str,
        job_id: str,
        chosen_slot: str
    ) -> dict:
        """
        Confirm candidate's chosen interview slot.
        """
        try:
            if chosen_slot not in ALLOWED_SLOTS:
                raise Exception("Invalid slot selected")

            response = (
                self.supabase
                .table("interview_slots")
                .select("*")
                .eq("candidate_id", candidate_id)
                .eq("job_id", job_id)
                .eq("status", InterviewStatus.PROPOSED.value)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )

            if not response.data:
                raise Exception("No proposed interview found for candidate")

            interview = response.data[0]
            date = interview.get("meeting_link") # Recover stored date

            meeting_link = f"https://meet.example.com/INT-{interview['id'][:8]}"

            update_data = {
                "chosen_slot": chosen_slot,
                "meeting_link": meeting_link,
                "status": InterviewStatus.CONFIRMED.value
            }

            update_response = (
                self.supabase
                .table("interview_slots")
                .update(update_data)
                .eq("id", interview["id"])
                .execute()
            )

            if not update_response.data:
                raise Exception("Failed to confirm interview slot")

            # Update pipeline stage
            await self.pipeline_service.update_candidate_stage(
                candidate_id=candidate_id,
                job_id=job_id,
                new_stage=CandidateStage.INTERVIEW_SCHEDULED
            )

            candidate_pipeline = await self.pipeline_service.get_candidate(candidate_id, job_id)
            preferred_channel = candidate_pipeline["preferred_channel"] if candidate_pipeline else "email"

            candidate_message = f"Your interview is confirmed for **{date}** at **{chosen_slot}**. Link: {meeting_link}"

            await self.messaging_service.send_message(
                candidate_id=candidate_id,
                job_id=job_id,
                stage=CandidateStage.INTERVIEW_SCHEDULED,
                message=candidate_message,
                preferred_channel=preferred_channel,
                message_type=MessageType.STAGE_UPDATE
            )

            # Send interviewer email manually
            interviewer_message = (
                f"Interview scheduled with candidate {candidate_id} on **{date}** at **{chosen_slot}**.\n"
                f"Meeting link: {meeting_link}"
            )

            self.messaging_service._send_email_smtp(
                interview["interviewer_email"],
                interviewer_message
            )

            return {
                "status": "confirmed",
                "meeting_link": meeting_link,
                "chosen_slot": chosen_slot,
                "interviewer_email": interview["interviewer_email"]
            }

        except Exception as e:
            raise Exception(f"Error confirming interview: {str(e)}")
