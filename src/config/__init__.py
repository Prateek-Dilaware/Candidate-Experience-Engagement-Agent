"""Configuration module."""
from .settings import settings
from .constants import (
    CandidateStage,
    MessageType,
    Channel,
    TouchpointType,
    Sentiment,
    DeliveryStatus,
    InterviewStatus,
    OfferStatus,
    STAGE_ORDER,
    CLOSED_STAGES,
    RISK_WEIGHTS,
    RISK_ALERT_THRESHOLD,
)

__all__ = [
    "settings",
    "CandidateStage",
    "MessageType",
    "Channel",
    "TouchpointType",
    "Sentiment",
    "DeliveryStatus",
    "InterviewStatus",
    "OfferStatus",
    "STAGE_ORDER",
    "CLOSED_STAGES",
    "RISK_WEIGHTS",
    "RISK_ALERT_THRESHOLD",
]
