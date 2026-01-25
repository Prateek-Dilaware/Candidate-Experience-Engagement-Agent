import asyncio
import os
import sys
from datetime import datetime, timezone
import random

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.db.supabase_client import get_supabase
from src.config.constants import CandidateStage, Channel

# --- CONFIGURATION ---
# TODO: Replace these with your authentic emails for testing
TEST_EMAILS = [
    "herofreefireop@gmail.com",
    "govindkushwaha6263@gmail.com",
    "Sweetysingh122003@gmail.com",
    "sophos101010101010@gmail.com",
    "pratikdilaware6683@gmail.com",
    "govindkushwaham6263@gmail.com"
]

JOB_ID = "JOB-2025-001"

async def seed_database():
    """Seed the database with test candidates."""
    supabase = get_supabase()
    
    print(f"🌱 Seeding database with {len(TEST_EMAILS)} candidates...")
    print(f"📧 Emails: {TEST_EMAILS}")
    
    candidates_created = 0
    
    for email in TEST_EMAILS:
        # Check if candidate exists
        try:
            existing = supabase.table("candidate_pipeline").select("*").eq("candidate_id", email).execute()
            if existing.data:
                print(f"⚠️  Candidate {email} already exists. Skipping.")
                continue
        except Exception as e:
            print(f"❌ Error checking candidate {email}: {e}")
            continue

        # Create Candidate
        candidate_data = {
            "candidate_id": email,
            "job_id": JOB_ID,
            "stage": CandidateStage.APPLIED.value,
            "stage_updated_at": datetime.now(timezone.utc).isoformat(),
            "preferred_channel": Channel.EMAIL.value,
            "timezone": "Asia/Kolkata",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            res = supabase.table("candidate_pipeline").insert(candidate_data).execute()
            print(f"✅ Created candidate: {email}")
            candidates_created += 1
            
            # Create Initial Touchpoint (Application Received)
            touchpoint_data = {
                "candidate_id": email,
                "type": "EMAIL", # Using string literal matching TouchpointType
                "channel": Channel.EMAIL.value,
                "message": "Application received for Software Engineer position.",
                "sentiment": "NEUTRAL",
                "delivery_status": "SENT",
                "metadata": {"source": "manual_seed"},
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            supabase.table("candidate_touchpoints").insert(touchpoint_data).execute()
            print(f"   ↳ Added 'Application Received' touchpoint")
            
        except Exception as e:
            print(f"❌ Error creating candidate {email}: {e}")

    print(f"\n🎉 Seeding complete! Added {candidates_created} new candidates.")

if __name__ == "__main__":
    asyncio.run(seed_database())
