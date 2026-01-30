"""Scheduling service - Manages interview scheduling."""
from datetime import datetime
from typing import List
from src.db import get_supabase
from src.config.constants import InterviewStatus, CandidateStage, MessageType
from src.services.messaging_service import MessagingService
from src.services.pipeline_service import PipelineService


class SchedulingService:
    """Service for interview scheduling operations."""

    def __init__(self):
        self.supabase = get_supabase()
        self.messaging_service = MessagingService()
        self.pipeline_service = PipelineService()

    def generate_time_slots(self, base_date: str, slots_per_day: int = 3) -> List[datetime]:
        """
        Generate interview slot timestamps for a given date.
        Args:
            base_date: ISO date string (e.g., '2026-02-15')
            slots_per_day: Number of slots to generate (default 3)
        Returns:
            List of datetime objects
        """
        try:
            date_obj = datetime.fromisoformat(base_date)

            slot_hours = [10, 15, 18][:slots_per_day]

            slots = []
            for hour in slot_hours:
                slot_time = date_obj.replace(hour=hour, minute=0, second=0, microsecond=0)
                slots.append(slot_time)

            return slots

        except Exception as e:
            raise Exception(f"Error generating time slots: {str(e)}")

    async def propose_interview_slots(
        self,
        candidate_id: str,
        job_id: str,
        date: str
    ) -> dict:
        """Propose interview slots to candidate."""
        try:
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

            proposed_slots = self.generate_time_slots(date)

            interview_data = {
                "candidate_id": candidate_id,
                "job_id": job_id,
                "interviewer_email": interviewer_email,
                "proposed_slots": [slot.isoformat() for slot in proposed_slots],
                "status": InterviewStatus.PROPOSED.value,
                "created_at": datetime.utcnow().isoformat()
            }

            response = (
                self.supabase
                .table("interview_slots")
                .insert(interview_data)
                .execute()
            )

            if not response.data:
                raise Exception("Failed to create interview slots")

            slots_list = "\n".join([
                f"- {slot.strftime('%Y-%m-%d %H:%M')}" for slot in proposed_slots
            ])

            message = (
                f"Hi,\n\nWe would like to invite you for an interview on **{date}**.\n"
                "Please select a slot from the following options:\n\n"
                f"{slots_list}\n\n"
                "Reply with your chosen slot."
            )

            await self.messaging_service.send_message(
                candidate_id=candidate_id,
                job_id=job_id,
                stage=CandidateStage.SCREENED,
                message=message,
                preferred_channel=None,  # Let MessagingService resolve from DB
                message_type=MessageType.STAGE_UPDATE
            )

            return {
                "status": "proposed",
                "slots": [slot.isoformat() for slot in proposed_slots],
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
        """Confirm candidate's chosen interview slot."""
        try:
            try:
                chosen_slot_dt = datetime.fromisoformat(chosen_slot)
            except Exception:
                raise Exception("Invalid slot format. Expected ISO timestamp string.")

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

            proposed_slots_iso = interview.get("proposed_slots", [])

            if chosen_slot not in proposed_slots_iso:
                raise Exception(
                    f"Chosen slot {chosen_slot} is not in the proposed slots: {proposed_slots_iso}"
                )

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

            await self.pipeline_service.update_candidate_stage(
                candidate_id=candidate_id,
                job_id=job_id,
                new_stage=CandidateStage.INTERVIEW_SCHEDULED
            )

            slot_display = chosen_slot_dt.strftime('%Y-%m-%d at %H:%M')
            candidate_message = f"Your interview is confirmed for **{slot_display}**. Link: {meeting_link}"

            await self.messaging_service.send_message(
                candidate_id=candidate_id,
                job_id=job_id,
                stage=CandidateStage.INTERVIEW_SCHEDULED,
                message=candidate_message,
                preferred_channel=None,
                message_type=MessageType.STAGE_UPDATE
            )

            interviewer_message = (
                f"Interview scheduled with candidate {candidate_id} on **{slot_display}**.\n"
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
