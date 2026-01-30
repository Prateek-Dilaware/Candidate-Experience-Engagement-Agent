"""Google Calendar integration service (Local OAuth)."""

from datetime import datetime, timedelta
from typing import List
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


class GoogleCalendarService:
    """Service for fetching interviewer availability from Google Calendar using Local OAuth."""

    def __init__(self):
        self.calendar_service = self._get_calendar_service()

    def _get_calendar_service(self):
        creds = None

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open("token.json", "w") as token:
                token.write(creds.to_json())

        service = build("calendar", "v3", credentials=creds)
        return service

    async def get_interviewer_free_slots(
        self,
        interviewer_email: str,
        start_date: str,
        end_date: str,
        duration_minutes: int = 30,
    ) -> List[str]:
        """Fetch interviewer's available slots (ISO timestamps)."""

        time_min = f"{start_date}T00:00:00Z"
        time_max = f"{end_date}T23:59:59Z"

        body = {
            "timeMin": time_min,
            "timeMax": time_max,
            "items": [{"id": interviewer_email}],
        }

        events_result = self.calendar_service.freebusy().query(body=body).execute()
        busy_periods = events_result["calendars"][interviewer_email]["busy"]

        free_slots = self._calculate_free_slots(
            busy_periods, start_date, end_date, duration_minutes
        )

        return free_slots

    def _calculate_free_slots(
        self,
        busy_periods: List[dict],
        start_date: str,
        end_date: str,
        duration_minutes: int,
    ) -> List[str]:
        """Calculate free slots between busy periods (10AM–6PM)."""

        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        busy = [
            (datetime.fromisoformat(b["start"]), datetime.fromisoformat(b["end"]))
            for b in busy_periods
        ]

        slots = []
        current = start

        while current <= end:
            if current.weekday() >= 5:  # skip weekends
                current += timedelta(days=1)
                continue

            day_start = current.replace(hour=10, minute=0, second=0, microsecond=0)
            day_end = current.replace(hour=18, minute=0, second=0, microsecond=0)

            slot = day_start
            while slot + timedelta(minutes=duration_minutes) <= day_end:
                overlap = any(
                    slot < b_end and slot + timedelta(minutes=duration_minutes) > b_start
                    for b_start, b_end in busy
                )

                if not overlap:
                    slots.append(slot.isoformat())

                slot += timedelta(minutes=duration_minutes)

            current += timedelta(days=1)

        return slots


# Singleton instance
google_calendar_service = GoogleCalendarService()
