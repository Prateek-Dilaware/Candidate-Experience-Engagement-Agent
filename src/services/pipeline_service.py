"""Pipeline service - Manages candidate stage transitions."""
from datetime import datetime
from typing import Optional
from src.db import get_supabase, CandidatePipeline
from src.config import CandidateStage, STAGE_ORDER, CLOSED_STAGES


class PipelineService:
    """Service for managing candidate pipeline stages."""
    
    def __init__(self):
        self.supabase = get_supabase()
    
    def validate_stage_transition(
        self, 
        current_stage: CandidateStage, 
        new_stage: CandidateStage
    ) -> tuple[bool, Optional[str]]:
        """
        Validate if stage transition is allowed.
        
        Returns:
            (is_valid, error_message)
        """
        # Cannot transition from closed stages
        if current_stage in CLOSED_STAGES:
            return False, f"Cannot transition from closed stage: {current_stage}"
        
        # Can always move to closed stages
        if new_stage in CLOSED_STAGES:
            return True, None
        
        # Check if stages are in correct order
        try:
            current_index = STAGE_ORDER.index(current_stage)
            new_index = STAGE_ORDER.index(new_stage)
            
            # Cannot skip stages (must be sequential or same)
            if new_index > current_index + 1:
                return False, f"Cannot skip from {current_stage} to {new_stage}. Must progress sequentially."
            
            # Cannot move backwards
            if new_index < current_index:
                return False, f"Cannot move backwards from {current_stage} to {new_stage}"
            
            return True, None
            
        except ValueError as e:
            return False, f"Invalid stage: {str(e)}"
    
    async def get_candidate(self, candidate_id: str) -> Optional[dict]:
        """Get candidate pipeline record."""
        try:
            response = self.supabase.table("candidate_pipeline").select("*").eq(
                "candidate_id", candidate_id
            ).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
            
        except Exception as e:
            raise Exception(f"Error fetching candidate: {str(e)}")
    
    async def create_candidate(
        self,
        candidate_id: str,
        job_id: str,
        stage: CandidateStage = CandidateStage.APPLIED,
        preferred_channel: str = "email",
        timezone: str = "Asia/Kolkata"
    ) -> dict:
        """Create new candidate pipeline record."""
        try:
            data = {
                "candidate_id": candidate_id,
                "job_id": job_id,
                "stage": stage.value,
                "stage_updated_at": datetime.utcnow().isoformat(),
                "preferred_channel": preferred_channel,
                "timezone": timezone,
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.supabase.table("candidate_pipeline").insert(data).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            raise Exception("Failed to create candidate record")
            
        except Exception as e:
            raise Exception(f"Error creating candidate: {str(e)}")
    
    async def update_candidate_stage(
        self,
        candidate_id: str,
        new_stage: CandidateStage
    ) -> dict:
        """
        Update candidate stage with validation.
        
        Returns:
            Updated candidate record
        """
        try:
            # Get current candidate
            candidate = await self.get_candidate(candidate_id)
            
            if not candidate:
                raise Exception(f"Candidate {candidate_id} not found")
            
            current_stage = CandidateStage(candidate["stage"])
            
            # Validate transition
            is_valid, error = self.validate_stage_transition(current_stage, new_stage)
            if not is_valid:
                raise Exception(error)
            
            # Update stage
            update_data = {
                "stage": new_stage.value,
                "stage_updated_at": datetime.utcnow().isoformat()
            }
            
            response = self.supabase.table("candidate_pipeline").update(
                update_data
            ).eq("candidate_id", candidate_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            raise Exception("Failed to update candidate stage")
            
        except Exception as e:
            raise Exception(f"Error updating candidate stage: {str(e)}")
    
    async def get_candidate_info(self, candidate_id: str) -> dict:
        """Get candidate info including current stage."""
        candidate = await self.get_candidate(candidate_id)
        if not candidate:
            raise Exception(f"Candidate {candidate_id} not found")
        return candidate
