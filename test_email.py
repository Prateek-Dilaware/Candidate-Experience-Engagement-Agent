"""Test script for real email sending."""
from src.services.messaging_service import MessagingService
from src.config import MessageType, Channel
import asyncio

async def test_email():
    print("📧 Testing Real Email Sending...")
    service = MessagingService()
    
    # Use the test email provided by user
    to_email = "govindkushwaha6263@gmail.com"
    
    # Create a test candidate first to satisfy FK constraint
    from src.services.pipeline_service import PipelineService
    from src.config import CandidateStage
    pipeline_service = PipelineService()
    try:
        await pipeline_service.create_candidate(
            candidate_id=to_email,
            job_id="TEST-JOB-001",
            stage=CandidateStage.APPLIED
        )
    except:
        pass # Candidate might already exist

    try:
        result = await service.send_message(
            candidate_id=to_email,
            message="Hello! This is a test email from your Candidate Engagement Agent via SMTP.",
            channel=Channel.EMAIL,
            message_type=MessageType.STAGE_UPDATE
        )
        print("\n✅ Email Sent Successfully!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"\n❌ Email Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_email())
