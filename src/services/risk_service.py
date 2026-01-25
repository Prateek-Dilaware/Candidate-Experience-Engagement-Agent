"""Risk service - Evaluates candidate drop-off risk."""
from datetime import datetime, timedelta
from typing import List, Tuple
from src.db import get_supabase
from src.config import RISK_WEIGHTS, RISK_ALERT_THRESHOLD, Sentiment


class RiskService:
    """Service for evaluating candidate engagement risk."""
    
    def __init__(self):
        self.supabase = get_supabase()
    
    def calculate_response_gap(self, last_response_at: str) -> Tuple[int, int]:
        """
        Calculate hours since last response.
        
        Returns:
            (gap_hours, risk_points)
        """
        if not last_response_at:
            return 0, 0
        
        last_response = datetime.fromisoformat(last_response_at.replace('Z', '+00:00'))
        now = datetime.utcnow()
        gap = now - last_response
        gap_hours = int(gap.total_seconds() / 3600)
        
        # Calculate risk points based on gap
        if gap_hours >= 72:
            return gap_hours, RISK_WEIGHTS["response_gap_72h"]
        elif gap_hours >= 48:
            return gap_hours, RISK_WEIGHTS["response_gap_48h"]
        elif gap_hours >= 24:
            return gap_hours, RISK_WEIGHTS["response_gap_24h"]
        
        return gap_hours, 0
    
    def analyze_sentiment(self, candidate_id: str) -> Tuple[bool, int]:
        """
        Analyze recent message sentiment.
        
        Returns:
            (has_negative_sentiment, risk_points)
        """
        try:
            # Get last 3 touchpoints
            response = self.supabase.table("candidate_touchpoints").select(
                "sentiment"
            ).eq("candidate_id", candidate_id).order(
                "created_at", desc=True
            ).limit(3).execute()
            
            if response.data:
                for touchpoint in response.data:
                    if touchpoint.get("sentiment") == Sentiment.NEGATIVE.value:
                        return True, RISK_WEIGHTS["negative_sentiment"]
            
            return False, 0
            
        except:
            return False, 0
    
    def check_reschedules(self, candidate_id: str) -> Tuple[int, int]:
        """
        Check if candidate rescheduled multiple times.
        
        Returns:
            (reschedule_count, risk_points)
        """
        try:
            response = self.supabase.table("interview_slots").select(
                "status"
            ).eq("candidate_id", candidate_id).execute()
            
            reschedule_count = 0
            if response.data:
                for interview in response.data:
                    if interview.get("status") == "rescheduled":
                        reschedule_count += 1
            
            if reschedule_count >= 2:
                return reschedule_count, RISK_WEIGHTS["rescheduled_twice"]
            
            return reschedule_count, 0
            
        except:
            return 0, 0
    
    async def evaluate_candidate_risk(self, candidate_id: str) -> dict:
        """
        Evaluate overall candidate drop-off risk.
        
        Returns:
            dict with risk score, reasons, and alert status
        """
        try:
            reasons: List[str] = []
            risk_score = 0
            
            # Get candidate info
            candidate_response = self.supabase.table("candidate_pipeline").select(
                "*"
            ).eq("candidate_id", candidate_id).execute()
            
            if not candidate_response.data or len(candidate_response.data) == 0:
                raise Exception("Candidate not found")
            
            # Get last touchpoint to check response time
            touchpoint_response = self.supabase.table("candidate_touchpoints").select(
                "created_at"
            ).eq("candidate_id", candidate_id).order(
                "created_at", desc=True
            ).limit(1).execute()
            
            last_response_at = None
            if touchpoint_response.data and len(touchpoint_response.data) > 0:
                last_response_at = touchpoint_response.data[0].get("created_at")
            
            # Factor 1: Response gap
            gap_hours, gap_points = self.calculate_response_gap(last_response_at)
            if gap_points > 0:
                risk_score += gap_points
                reasons.append(f"No response in last {gap_hours} hours")
            
            # Factor 2: Negative sentiment
            has_negative, sentiment_points = self.analyze_sentiment(candidate_id)
            if has_negative:
                risk_score += sentiment_points
                reasons.append("Negative sentiment detected in last message")
            
            # Factor 3: Multiple reschedules
            reschedule_count, reschedule_points = self.check_reschedules(candidate_id)
            if reschedule_points > 0:
                risk_score += reschedule_points
                reasons.append(f"Rescheduled {reschedule_count} times")
            
            # Cap at 100
            risk_score = min(risk_score, 100)
            
            # Determine if alert should be triggered
            alert_triggered = risk_score >= RISK_ALERT_THRESHOLD
            
            # Store risk signal
            risk_data = {
                "candidate_id": candidate_id,
                "risk_score": risk_score,
                "reasons": reasons,
                "last_response_at": last_response_at,
                "response_gap_hours": gap_hours if last_response_at else None,
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.supabase.table("candidate_risk_signals").insert(risk_data).execute()
            
            # If alert triggered, send notification to recruiter (mock)
            if alert_triggered:
                print(f"🚨 ALERT: Candidate {candidate_id} at risk (score: {risk_score})")
                # TODO: Send actual alert to recruiter
            
            return {
                "risk_score": risk_score,
                "reasons": reasons if reasons else ["No risk factors detected"],
                "alert_triggered": alert_triggered
            }
            
        except Exception as e:
            raise Exception(f"Error evaluating risk: {str(e)}")
