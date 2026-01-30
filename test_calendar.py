import asyncio
from src.services.google_calendar_service import google_calendar_service

async def test():
    slots = await google_calendar_service.get_interviewer_free_slots(
        interviewer_email="pratikdilaware6683@gmail.com",
        start_date="2026-02-15",
        end_date="2026-02-15",
        duration_minutes=30
    )
    print(slots)

asyncio.run(test())
