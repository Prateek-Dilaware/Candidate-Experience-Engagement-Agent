"""Risk service - Evaluates candidate drop-off risk."""
from datetime import datetime, timezone
from typing import List, Tuple
from src.db import get_supabase
from src.config import RISK_WEIGHTS, RISK_ALERT_THRESHOLD, Sentiment, CandidateStage


class RiskService:
    """Service for evaluating candidate engagement risk."""

    def __init__(self):
        self.supabase = get_supabase()

    def calculate_response_gap(self, last_response_at: str) -> Tuple[int, int]:
        """Calculate hours since last response."""
        if not last_response_at:
            return 0, 0

        last_response = datetime.fromisoformat(
            last_response_at.replace("Z", "+00:00")
        )
        now = datetime.now(timezone.utc)
        gap = now - last_response
        gap_hours = int(gap.total_seconds() / 3600)

        if gap_hours >= 72:
            return gap_hours, RISK_WEIGHTS["response_gap_72h"]
        elif gap_hours >= 48:
            return gap_hours, RISK_WEIGHTS["response_gap_48h"]
        elif gap_hours >= 24:
            return gap_hours, RISK_WEIGHTS["response_gap_24h"]

        return gap_hours, 0

    def analyze_sentiment(
        self,
        candidate_id: str,
        job_id: str
    ) -> Tuple[bool, int]:
        """Analyze recent message sentiment."""
        try:
            response = (
                self.supabase
                .table("candidate_touchpoints")
                .select("sentiment")
                .eq("candidate_id", candidate_id)
                .eq("job_id", job_id)
                .order("created_at", desc=True)
                .limit(3)
                .execute()
            )

            if response.data:
                for touchpoint in response.data:
                    if touchpoint.get("sentiment") == Sentiment.NEGATIVE.value:
                        return True, RISK_WEIGHTS["negative_sentiment"]

            return False, 0

        except Exception:
            return False, 0

    async def evaluate_candidate_risk(
        self,
        candidate_id: str,
        job_id: str
    ) -> dict:
        """Evaluate overall candidate drop-off risk."""
        try:
            reasons: List[str] = []
            risk_score = 0

            # Get pipeline stage
            pipeline_resp = (
                self.supabase
                .table("candidate_pipeline")
                .select("stage")
                .eq("candidate_id", candidate_id)
                .eq("job_id", job_id)
                .execute()
            )

            if not pipeline_resp.data:
                raise Exception("Candidate pipeline record not found")

            stage = CandidateStage(pipeline_resp.data[0]["stage"])

            # Get last touchpoint time
            touchpoint_resp = (
                self.supabase
                .table("candidate_touchpoints")
                .select("created_at")
                .eq("candidate_id", candidate_id)
                .eq("job_id", job_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )

            last_response_at = (
                touchpoint_resp.data[0]["created_at"]
                if touchpoint_resp.data else None
            )

            # Factor 1: Response gap
            gap_hours, gap_points = self.calculate_response_gap(last_response_at)
            if gap_points > 0:
                risk_score += gap_points
                reasons.append(f"No response in last {gap_hours} hours")

            # Factor 2: Negative sentiment
            has_negative, sentiment_points = self.analyze_sentiment(candidate_id, job_id)
            if has_negative:
                risk_score += sentiment_points
                reasons.append("Negative sentiment detected in recent message")

            # Cap at 100
            risk_score = min(risk_score, 100)

            alert_triggered = risk_score >= RISK_ALERT_THRESHOLD

            # Store risk signal
            risk_data = {
                "candidate_id": candidate_id,
                "job_id": job_id,
                "stage": stage.value,
                "risk_score": risk_score,
                "reasons": reasons,
                "last_response_at": last_response_at,
                "response_gap_hours": gap_hours if last_response_at else None,
                "created_at": datetime.utcnow().isoformat()
            }

            self.supabase.table("candidate_risk_signals").insert(risk_data).execute()

            if alert_triggered:
                print(
                    f"🚨 ALERT: Candidate {candidate_id} ({job_id}) at risk (score: {risk_score})"
                )

            return {
                "risk_score": risk_score,
                "reasons": reasons if reasons else ["No risk factors detected"],
                "alert_triggered": alert_triggered
            }

        except Exception as e:
            raise Exception(f"Error evaluating risk: {str(e)}")
