from enum import Enum


class CandidateStage(str, Enum):
    APPLIED = "APPLIED"
    SCREENED = "SCREENED"
    INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED"
    INTERVIEWED = "INTERVIEWED"
    OFFERED = "OFFERED"
    OFFER_ACCEPTED = "OFFER_ACCEPTED"
    ONBOARDING = "ONBOARDING"
    CLOSED_REJECTED = "CLOSED_REJECTED"
    CLOSED_WITHDRAWN = "CLOSED_WITHDRAWN"


class Channel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"


class TouchpointType(str, Enum):
    STATUS_UPDATE = "status_update"
    REMINDER = "reminder"
    SCHEDULE = "schedule"
    OFFER = "offer"
    SURVEY = "survey"
    ALERT = "alert"


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class DeliveryStatus(str, Enum):
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"


class InterviewStatus(str, Enum):
    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class OfferStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class MessageType(str, Enum):
    """Types of messages that can be sent."""
    STAGE_UPDATE = "STAGE_UPDATE"
    REMINDER_24H = "REMINDER_24H"
    REMINDER_1H = "REMINDER_1H"
    OFFER_SENT = "OFFER_SENT"
    FEEDBACK_SURVEY = "FEEDBACK_SURVEY"
    RE_ENGAGEMENT = "RE_ENGAGEMENT"
    CLOSURE_REJECTION = "CLOSURE_REJECTION"


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

RISK_WEIGHTS = {
    "response_gap_24h": 15,
    "response_gap_48h": 25,
    "response_gap_72h": 40,
    "negative_sentiment": 25,
    "rescheduled_twice": 20,
    "missed_interview": 35,
}

RISK_ALERT_THRESHOLD = 70
