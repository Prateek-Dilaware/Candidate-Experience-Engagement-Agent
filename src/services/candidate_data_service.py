"""Candidate service - Manages candidate profiles and job information."""
from typing import Optional, Dict
from src.db import get_supabase


class CandidateDataService:
    """Service for fetching candidate and job information."""

    def __init__(self):
        self.supabase = get_supabase()

    async def get_candidate_profile(self, candidate_id: str) -> Optional[Dict]:
        """Fetch candidate profile."""
        try:
            response = (
                self.supabase
                .table("candidate_profiles")
                .select("candidate_id, full_name, email, created_at")
                .eq("candidate_id", candidate_id)
                .execute()
            )

            return response.data[0] if response.data else None

        except Exception as e:
            raise Exception(f"Error fetching candidate profile: {str(e)}")

    async def get_job_details(self, job_id: str) -> Optional[Dict]:
        """Fetch job details."""
        try:
            response = (
                self.supabase
                .table("jobs")
                .select("job_id, title, interviewer_email, created_at")
                .eq("job_id", job_id)
                .execute()
            )

            return response.data[0] if response.data else None

        except Exception as e:
            raise Exception(f"Error fetching job details: {str(e)}")

    async def get_candidate_email(self, candidate_id: str) -> Optional[str]:
        """Get candidate's email address."""
        profile = await self.get_candidate_profile(candidate_id)
        return profile["email"] if profile else None

    async def get_candidate_name(self, candidate_id: str) -> str:
        """Get candidate's full name."""
        profile = await self.get_candidate_profile(candidate_id)
        if profile and profile.get("full_name"):
            return profile["full_name"]
        return "Candidate"

    async def get_job_title(self, job_id: str) -> str:
        """Get job title."""
        job = await self.get_job_details(job_id)
        if job and job.get("title"):
            return job["title"]
        return "Software Engineer"

    async def create_candidate_profile(
        self,
        candidate_id: str,
        full_name: str,
        email: str
    ) -> Dict:
        """Create a new candidate profile."""
        try:
            data = {
                "candidate_id": candidate_id,
                "full_name": full_name,
                "email": email,
            }

            response = (
                self.supabase
                .table("candidate_profiles")
                .insert(data)
                .execute()
            )

            if response.data:
                return response.data[0]

            raise Exception("Insert returned no data")

        except Exception as e:
            raise Exception(f"Error creating candidate profile: {str(e)}")

    async def create_job(
        self,
        job_id: str,
        title: str,
        interviewer_email: str
    ) -> Dict:
        """Create a new job."""
        try:
            data = {
                "job_id": job_id,
                "title": title,
                "interviewer_email": interviewer_email,
            }

            response = (
                self.supabase
                .table("jobs")
                .insert(data)
                .execute()
            )

            if response.data:
                return response.data[0]

            raise Exception("Insert returned no data")

        except Exception as e:
            raise Exception(f"Error creating job: {str(e)}")

    async def get_all_candidates(self) -> list:
        """Fetch all candidate profiles."""
        try:
            response = (
                self.supabase
                .table("candidate_profiles")
                .select("*")
                .execute()
            )
            return response.data
        except Exception as e:
            raise Exception(f"Error fetching all candidates: {str(e)}")

    async def get_all_jobs(self) -> list:
        """Fetch all jobs."""
        try:
            response = (
                self.supabase
                .table("jobs")
                .select("*")
                .execute()
            )
            return response.data
        except Exception as e:
            raise Exception(f"Error fetching all jobs: {str(e)}")
