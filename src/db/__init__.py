"""Database module."""
from .supabase_client import get_supabase
from .models import (
    CandidatePipeline,
    CandidateTouchpoint,
    InterviewSlot,
    OfferLetter,
    CandidateRiskSignal,
)

__all__ = [
    "get_supabase",
    "CandidatePipeline",
    "CandidateTouchpoint",
    "InterviewSlot",
    "OfferLetter",
    "CandidateRiskSignal",
]
