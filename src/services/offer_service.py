"""Offer service - Manages offer letter generation."""
from datetime import datetime
from typing import Dict, Any
from src.db import get_supabase
from src.config import OfferStatus
from src.agents.offer_writer import OfferWriter

class OfferService:
    """Service for offer letter generation and management."""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.offer_writer = OfferWriter()
    
    async def generate_offer_letter(
        self,
        candidate_id: str,
        job_id: str,
        compensation: Dict[str, Any],
        template_id: str = "OFFER_STD_V1"
    ) -> dict:
        """
        Generate and store offer letter using AI.
        
        Returns:
            dict with offer details
        """
        try:
            # TODO: Get candidate name and role from database
            candidate_name = "Candidate"
            role_title = "Software Engineer"
            
            # Generate offer text using AI
            try:
                offer_text = self.offer_writer.generate_offer_letter(
                    candidate_name=candidate_name,
                    role_title=role_title,
                    compensation=compensation
                )
            except Exception as e:
                print(f"⚠️ AI Offer Generation Failed: {e}. Using fallback.")
                offer_text = f"Offer for {role_title}. CTC: {compensation.get('ctc')}"
            
            # Store in database
            offer_data = {
                "candidate_id": candidate_id,
                "job_id": job_id,
                "offer_text": offer_text,
                "compensation_json": compensation,
                "status": OfferStatus.DRAFT.value,
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.supabase.table("offer_letters").insert(
                offer_data
            ).execute()
            
            if response.data and len(response.data) > 0:
                offer = response.data[0]
                
                return {
                    "offer_id": offer["id"],
                    "status": "draft",
                    "offer_preview": offer_text[:200] + "..."  # First 200 chars
                }
            
            raise Exception("Failed to create offer letter")
            
        except Exception as e:
            raise Exception(f"Error generating offer: {str(e)}")
    
    async def get_offer_by_id(self, offer_id: str) -> dict:
        """Get full offer letter by ID."""
        try:
            response = self.supabase.table("offer_letters").select(
                "*"
            ).eq("id", offer_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            
            raise Exception("Offer not found")
            
        except Exception as e:
            raise Exception(f"Error fetching offer: {str(e)}")
