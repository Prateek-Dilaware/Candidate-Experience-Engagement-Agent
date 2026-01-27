"""Pipeline service - Manages candidate stage transitions."""
from datetime import datetime
from typing import Optional, Tuple
from src.db import get_supabase
from src.config.constants import CandidateStage, STAGE_ORDER, CLOSED_STAGES, Channel


class PipelineService:
    """Service for managing candidate pipeline stages."""

    def __init__(self):
        self.supabase = get_supabase()

    def validate_stage_transition(
        self,
        current_stage: CandidateStage,
        new_stage: CandidateStage
    ) -> Tuple[bool, Optional[str]]:
        """Validate if stage transition is allowed."""
        if current_stage in CLOSED_STAGES:
            return False, f"Cannot transition from closed stage: {current_stage.value}"

        if new_stage in CLOSED_STAGES:
            return True, None

        try:
            current_index = STAGE_ORDER.index(current_stage)
            new_index = STAGE_ORDER.index(new_stage)

            if new_index > current_index + 1:
                return False, f"Cannot skip from {current_stage.value} to {new_stage.value}"

            if new_index < current_index:
                return False, f"Cannot move backwards from {current_stage.value} to {new_stage.value}"

            return True, None

        except ValueError:
            return False, "Invalid stage value"

    async def get_candidate(
        self,
        candidate_id: str,
        job_id: str
    ) -> Optional[dict]:
        """Get candidate pipeline record for a specific job."""
        try:
            response = (
                self.supabase
                .table("candidate_pipeline")
                .select("*")
                .eq("candidate_id", candidate_id)
                .eq("job_id", job_id)
                .execute()
            )

            if response.data:
                return response.data[0]
            return None

        except Exception as e:
            raise Exception(f"Error fetching candidate pipeline: {str(e)}")

    async def create_candidate(
        self,
        candidate_id: str,
        job_id: str,
        stage: CandidateStage = CandidateStage.APPLIED,
        preferred_channel: Channel = Channel.EMAIL,
        timezone: str = "Asia/Kolkata"
    ) -> dict:
        """Create new candidate pipeline record."""
        try:
            data = {
                "candidate_id": candidate_id,
                "job_id": job_id,
                "stage": stage.value,
                "stage_updated_at": datetime.utcnow().isoformat(),
                "preferred_channel": preferred_channel.value,
                "timezone": timezone,
            }

            response = (
                self.supabase
                .table("candidate_pipeline")
                .insert(data)
                .execute()
            )

            if response.data:
                return response.data[0]

            raise Exception("Failed to create candidate pipeline record")

        except Exception as e:
            raise Exception(f"Error creating candidate pipeline: {str(e)}")

    async def update_candidate_stage(
        self,
        candidate_id: str,
        job_id: str,
        new_stage: CandidateStage
    ) -> dict:
        """Update candidate stage with validation."""
        try:
            candidate = await self.get_candidate(candidate_id, job_id)

            if not candidate:
                raise Exception("Candidate pipeline record not found")

            current_stage = CandidateStage(candidate["stage"])

            is_valid, error = self.validate_stage_transition(current_stage, new_stage)
            if not is_valid:
                raise Exception(error)

            update_data = {
                "stage": new_stage.value,
                "stage_updated_at": datetime.utcnow().isoformat()
            }

            response = (
                self.supabase
                .table("candidate_pipeline")
                .update(update_data)
                .eq("candidate_id", candidate_id)
                .eq("job_id", job_id)
                .execute()
            )

            if response.data:
                return response.data[0]

            raise Exception("Failed to update candidate stage")

        except Exception as e:
            raise Exception(f"Error updating candidate stage: {str(e)}")

    async def get_candidate_info(
        self,
        candidate_id: str,
        job_id: str
    ) -> dict:
        """Get candidate pipeline info."""
        candidate = await self.get_candidate(candidate_id, job_id)
        if not candidate:
            raise Exception("Candidate pipeline record not found")
        return candidate
