"""Application constants for candidate journey management."""
from enum import Enum


class CandidateStage(str, Enum):
    """Candidate pipeline stages."""
    APPLIED = "APPLIED"
    SCREENED = "SCREENED"
    INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED"
    INTERVIEWED = "INTERVIEWED"
    OFFERED = "OFFERED"
    OFFER_ACCEPTED = "OFFER_ACCEPTED"
    ONBOARDING = "ONBOARDING"
    CLOSED_REJECTED = "CLOSED_REJECTED"
    CLOSED_WITHDRAWN = "CLOSED_WITHDRAWN"


class MessageType(str, Enum):
    """Types of messages that can be sent."""
    STAGE_UPDATE = "stage_update"
    REMINDER_24H = "reminder_24h"
    REMINDER_1H = "reminder_1h"
    OFFER_SENT = "offer_sent"
    FEEDBACK_SURVEY = "feedback_survey"
    RE_ENGAGEMENT = "re_engagement"
    CLOSURE_REJECTION = "closure_rejection"


class Channel(str, Enum):
    """Communication channels."""
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    SYSTEM = "system"


class TouchpointType(str, Enum):
    """Types of candidate touchpoints."""
    STATUS_UPDATE = "status_update"
    REMINDER = "reminder"
    SCHEDULE = "schedule"
    OFFER = "offer"
    SURVEY = "survey"
    ALERT = "alert"


class Sentiment(str, Enum):
    """Sentiment classification."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class DeliveryStatus(str, Enum):
    """Message delivery status."""
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"


class InterviewStatus(str, Enum):
    """Interview scheduling status."""
    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    RESCHEDULED = "rescheduled"
    CANCELLED = "cancelled"


class OfferStatus(str, Enum):
    """Offer letter status."""
    DRAFT = "draft"
    SENT = "sent"
    SIGNED = "signed"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"


# Stage progression rules
STAGE_ORDER = [
    CandidateStage.APPLIED,
    CandidateStage.SCREENED,
    CandidateStage.INTERVIEW_SCHEDULED,
    CandidateStage.INTERVIEWED,
    CandidateStage.OFFERED,
    CandidateStage.OFFER_ACCEPTED,
    CandidateStage.ONBOARDING,
]

CLOSED_STAGES = [
    CandidateStage.CLOSED_REJECTED,
    CandidateStage.CLOSED_WITHDRAWN,
]

# Risk scoring weights
RISK_WEIGHTS = {
    "response_gap_24h": 15,
    "response_gap_48h": 25,
    "response_gap_72h": 40,
    "negative_sentiment": 25,
    "rescheduled_twice": 20,
    "missed_interview": 35,
}

RISK_ALERT_THRESHOLD = 70
