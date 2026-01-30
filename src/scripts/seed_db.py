import asyncio
import os
import sys
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.db.supabase_client import get_supabase
from src.config.constants import CandidateStage, Channel, DeliveryStatus

# --- CONFIGURATION ---
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
    supabase = get_supabase()

    print(f"🌱 Seeding database with {len(TEST_EMAILS)} candidates...")

    candidates_created = 0

    for email in TEST_EMAILS:
        try:
            # 1️⃣ Check if candidate profile exists
            profile_check = (
                supabase.table("candidate_profiles")
                .select("candidate_id")
                .eq("candidate_id", email)
                .execute()
            )

            if not profile_check.data:
                profile_data = {
                    "candidate_id": email,
                    "full_name": email.split("@")[0].title(),
                    "email": email,
                    "whatsapp_number": None,
                    "preferred_channel": Channel.EMAIL.value,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }

                supabase.table("candidate_profiles").insert(profile_data).execute()
                print(f"✅ Created candidate profile: {email}")
            else:
                print(f"⚠️ Profile already exists: {email}")

            # 2️⃣ Check if pipeline exists
            pipeline_check = (
                supabase.table("candidate_pipeline")
                .select("*")
                .eq("candidate_id", email)
                .eq("job_id", JOB_ID)
                .execute()
            )

            if pipeline_check.data:
                print(f"⚠️ Pipeline already exists for {email}. Skipping.")
                continue

            pipeline_data = {
                "candidate_id": email,
                "job_id": JOB_ID,
                "stage": CandidateStage.APPLIED.value,
                "stage_updated_at": datetime.now(timezone.utc).isoformat(),
                "preferred_channel": Channel.EMAIL.value,
                "timezone": "Asia/Kolkata",
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            supabase.table("candidate_pipeline").insert(pipeline_data).execute()
            print(f"✅ Created pipeline for: {email}")
            candidates_created += 1

            # 3️⃣ Create initial touchpoint
            touchpoint_data = {
                "candidate_id": email,
                "job_id": JOB_ID,
                "stage": CandidateStage.APPLIED.value,
                "type": "status_update",
                "channel": Channel.EMAIL.value,
                "message": "Application received for Software Engineer position.",
                "sentiment": "neutral",
                "delivery_status": DeliveryStatus.SENT.value,
                "metadata": {"source": "manual_seed"},
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            supabase.table("candidate_touchpoints").insert(touchpoint_data).execute()
            print(f"   ↳ Added initial touchpoint")

        except Exception as e:
            print(f"❌ Error processing {email}: {e}")

    print(f"\n🎉 Seeding complete! Added {candidates_created} new candidates.")

if __name__ == "__main__":
    asyncio.run(seed_database())
