"""Scheduling service - Manages interview scheduling."""
from datetime import datetime, timedelta
from typing import List
from src.db import get_supabase
from src.config import InterviewStatus


class SchedulingService:
    """Service for interview scheduling operations."""
    
    def __init__(self):
        self.supabase = get_supabase()
    
    def generate_time_slots(
        self,
        start_date: str,
        end_date: str,
        duration_minutes: int = 30,
        slots_per_day: int = 3
    ) -> List[str]:
        """
        Generate interview time slots within a date range.
        
        Mock implementation - generates slots avoiding lunch hours.
        In production, this would integrate with Google Calendar/Outlook.
        """
        slots = []
        
        # Parse dates
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        current_date = start
        
        while current_date <= end:
            # Skip weekends
            if current_date.weekday() >= 5:  # Saturday=5, Sunday=6
                current_date += timedelta(days=1)
                continue
            
            # Generate slots for the day
            # Morning slots: 10:00, 11:00
            morning_slots = [
                current_date.replace(hour=10, minute=0, second=0, microsecond=0),
                current_date.replace(hour=11, minute=0, second=0, microsecond=0),
            ]
            
            # Afternoon slot: 15:00 (avoiding 13:00-14:00 lunch)
            afternoon_slot = current_date.replace(hour=15, minute=0, second=0, microsecond=0)
            
            # Combine and add to slots
            day_slots = morning_slots + [afternoon_slot]
            
            # Take only requested number of slots per day
            for slot in day_slots[:slots_per_day]:
                # Format as ISO string with timezone
                slots.append(slot.isoformat() + "+05:30")  # Asia/Kolkata timezone
            
            current_date += timedelta(days=1)
        
        return slots[:10]  # Return max 10 slots
    
    async def propose_interview_slots(
        self,
        candidate_id: str,
        job_id: str,
        interviewer_email: str,
        start_date: str,
        end_date: str,
        duration_minutes: int = 30
    ) -> dict:
        """
        Propose interview slots to candidate.
        
        Returns:
            dict with proposed slots and interview record
        """
        try:
            # Generate slots
            proposed_slots = self.generate_time_slots(
                start_date=start_date,
                end_date=end_date,
                duration_minutes=duration_minutes
            )
            
            # Store in database
            interview_data = {
                "candidate_id": candidate_id,
                "job_id": job_id,
                "interviewer_email": interviewer_email,
                "proposed_slots": proposed_slots,
                "status": InterviewStatus.PROPOSED.value,
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.supabase.table("interview_slots").insert(
                interview_data
            ).execute()
            
            if response.data and len(response.data) > 0:
                return {
                    "status": "proposed",
                    "slots": proposed_slots,
                    "interview_id": response.data[0]["id"]
                }
            
            raise Exception("Failed to create interview slots")
            
        except Exception as e:
            raise Exception(f"Error proposing interview slots: {str(e)}")
    
    async def confirm_interview_slot(
        self,
        candidate_id: str,
        chosen_slot: str
    ) -> dict:
        """
        Confirm candidate's chosen interview slot.
        
        Returns:
            dict with confirmation details and meeting link
        """
        try:
            # Find the interview record
            response = self.supabase.table("interview_slots").select(
                "*"
            ).eq("candidate_id", candidate_id).eq(
                "status", InterviewStatus.PROPOSED.value
            ).order("created_at", desc=True).limit(1).execute()
            
            if not response.data or len(response.data) == 0:
                raise Exception("No proposed interview found for candidate")
            
            interview = response.data[0]
            
            # Verify chosen slot is in proposed slots
            if chosen_slot not in interview["proposed_slots"]:
                raise Exception("Chosen slot not in proposed slots")
            
            # Generate mock meeting link
            meeting_link = f"https://meet.example.com/INT-{interview['id'][:8]}"
            
            # Update interview record
            update_data = {
                "chosen_slot": chosen_slot,
                "meeting_link": meeting_link,
                "status": InterviewStatus.CONFIRMED.value
            }
            
            update_response = self.supabase.table("interview_slots").update(
                update_data
            ).eq("id", interview["id"]).execute()
            
            if update_response.data and len(update_response.data) > 0:
                # Schedule reminders (mock)
                reminders = ["24h", "1h"]
                
                return {
                    "status": "confirmed",
                    "meeting_link": meeting_link,
                    "reminders_scheduled": reminders,
                    "chosen_slot": chosen_slot
                }
            
            raise Exception("Failed to confirm interview slot")
            
        except Exception as e:
            raise Exception(f"Error confirming interview: {str(e)}")
