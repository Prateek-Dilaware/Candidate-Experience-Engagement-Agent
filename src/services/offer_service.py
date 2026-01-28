"""Offer service - Manages offer letter generation (no compensation, joining_date input)."""

from datetime import datetime
from src.db import get_supabase
from src.config import OfferStatus, CandidateStage, MessageType, Channel
from src.agents.offer_writer import OfferWriter
from src.services.messaging_service import MessagingService


class OfferService:
    """Service for offer letter generation and management."""

    def __init__(self):
        self.supabase = get_supabase()
        self.offer_writer = OfferWriter()
        self.messaging_service = MessagingService()  # ✅ Added

    async def generate_offer_letter(
        self,
        candidate_id: str,
        job_id: str,
        joining_date: str
    ) -> dict:
        """Generate, store, and send offer letter using AI."""
        try:
            # Fetch candidate name
            profile_resp = (
                self.supabase
                .table("candidate_profiles")
                .select("full_name")
                .eq("candidate_id", candidate_id)
                .execute()
            )
            candidate_name = (
                profile_resp.data[0]["full_name"]
                if profile_resp.data else "Candidate"
            )

            # Fetch job title
            job_resp = (
                self.supabase
                .table("jobs")
                .select("title")
                .eq("job_id", job_id)
                .execute()
            )
            role_title = (
                job_resp.data[0]["title"]
                if job_resp.data else "Software Engineer"
            )

            # Generate offer text using AI
            try:
                offer_text = self.offer_writer.generate_offer_letter(
                    candidate_name=candidate_name,
                    role_title=role_title,
                    joining_date=joining_date
                )
            except Exception as e:
                print(f"⚠️ AI Offer Generation Failed: {e}. Using fallback.")
                offer_text = (
                    f"Dear {candidate_name}, we are pleased to offer you the position of "
                    f"{role_title} with a joining date of {joining_date}."
                )

            # Store in database
            offer_data = {
                "candidate_id": candidate_id,
                "job_id": job_id,
                "offer_text": offer_text,
                "status": OfferStatus.DRAFT.value,
                "created_at": datetime.utcnow().isoformat()
            }

            response = (
                self.supabase
                .table("offer_letters")
                .insert(offer_data)
                .execute()
            )

            if response.data:
                offer = response.data[0]

                # ✅ SEND OFFER VIA MessagingService
                await self.messaging_service.send_message(
                    candidate_id=candidate_id,
                    job_id=job_id,
                    stage=CandidateStage.OFFERED,
                    message=offer_text,
                    preferred_channel=Channel.EMAIL.value,
                    message_type=MessageType.OFFER_SENT
                )

                return {
                    "offer_id": offer["id"],
                    "status": offer["status"],
                    "offer_preview": offer_text[:200] + "..."
                }

            raise Exception("Failed to create offer letter")

        except Exception as e:
            raise Exception(f"Error generating offer: {str(e)}")

    async def get_offer_by_id(self, offer_id: str) -> dict:
        """Get full offer letter by ID."""
        try:
            response = (
                self.supabase
                .table("offer_letters")
                .select("*")
                .eq("id", offer_id)
                .execute()
            )

            if response.data:
                return response.data[0]

            raise Exception("Offer not found")

        except Exception as e:
            raise Exception(f"Error fetching offer: {str(e)}")
