from datetime import datetime
import asyncio
from typing import Optional
from src.db import get_supabase
from src.config.constants import Channel, DeliveryStatus, MessageType, CandidateStage
from src.agents.message_personalizer import MessagePersonalizer


class MessagingService:
    """Service for sending messages across multiple channels."""

    def __init__(self):
        self.supabase = get_supabase()
        self.personalizer = MessagePersonalizer()

    def _determine_channel(
        self,
        preferred_channel: Channel,
        message_type: MessageType,
        override: Optional[Channel] = None
    ) -> Channel:
        if override:
            return override

        if preferred_channel:
            return preferred_channel

        if message_type in [MessageType.REMINDER_24H, MessageType.REMINDER_1H]:
            return Channel.SMS
        elif message_type == MessageType.OFFER_SENT:
            return Channel.EMAIL

        return Channel.EMAIL

    async def _get_candidate_email(self, candidate_id: str) -> str:
        response = (
            self.supabase
            .table("candidate_profiles")
            .select("email")
            .eq("candidate_id", candidate_id)
            .execute()
        )

        if not response.data:
            raise Exception("Candidate email not found")

        return response.data[0]["email"]

    async def _get_candidate_whatsapp_number(self, candidate_id: str) -> Optional[str]:
        response = (
            self.supabase
            .table("candidate_profiles")
            .select("whatsapp_number")
            .eq("candidate_id", candidate_id)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0].get("whatsapp_number")

    async def _get_candidate_preferred_channel(self, candidate_id: str) -> Channel:
        response = (
            self.supabase
            .table("candidate_profiles")
            .select("preferred_channel")
            .eq("candidate_id", candidate_id)
            .execute()
        )

        if not response.data or not response.data[0].get("preferred_channel"):
            return Channel.EMAIL

        return Channel(response.data[0]["preferred_channel"])

    async def send_message(
        self,
        candidate_id: str,
        job_id: str,
        stage: CandidateStage,
        message: str,
        preferred_channel: Optional[Channel],
        message_type: MessageType,
        channel_override: Optional[Channel] = None,
        metadata: Optional[dict] = None,
        to_email: Optional[str] = None
    ) -> dict:
        try:
            db_preferred_channel = await self._get_candidate_preferred_channel(candidate_id)
            final_preferred_channel = preferred_channel or db_preferred_channel

            channel = self._determine_channel(
                final_preferred_channel,
                message_type,
                channel_override
            )

            target_email = None
            target_whatsapp = None

            if channel == Channel.EMAIL:
                target_email = to_email or await self._get_candidate_email(candidate_id)

            if channel in [Channel.SMS, Channel.WHATSAPP]:
                target_whatsapp = await self._get_candidate_whatsapp_number(candidate_id)
                if not target_whatsapp:
                    raise Exception(
                        f"{channel.value} channel selected but candidate {candidate_id} has no whatsapp_number"
                    )

            sent_successfully = False
            error_details = None

            if channel == Channel.EMAIL:
                try:
                    loop = asyncio.get_running_loop()
                    await loop.run_in_executor(
                        None, self._send_email_smtp, target_email, message
                    )
                    sent_successfully = True
                except Exception as e:
                    error_details = str(e)

            elif channel == Channel.SMS:
                self._mock_sms_delivery(target_whatsapp, message)
                sent_successfully = True

            elif channel == Channel.WHATSAPP:
                self._mock_whatsapp_delivery(target_whatsapp, message)
                sent_successfully = True

            touchpoint_data = {
                "candidate_id": candidate_id,
                "job_id": job_id,
                "stage": stage.value,
                "type": "status_update" if message_type == MessageType.STAGE_UPDATE else "notification",
                "channel": channel.value,
                "message": message,
                "sentiment": None,
                "delivery_status": (
                    DeliveryStatus.SENT.value
                    if sent_successfully
                    else DeliveryStatus.FAILED.value
                ),
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat()
            }

            response = (
                self.supabase
                .table("candidate_touchpoints")
                .insert(touchpoint_data)
                .execute()
            )

            if response.data:
                result = {
                    "sent": sent_successfully,
                    "channel": channel.value,
                    "touchpoint_id": response.data[0]["id"],
                    "message": message,
                }
                if error_details:
                    result["error"] = error_details
                return result

            raise Exception("Failed to record touchpoint")

        except Exception as e:
            raise Exception(f"Error sending message: {str(e)}")

    def _mock_sms_delivery(self, to: str, message: str):
        with open("mock_sms.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] TO: {to}\nMESSAGE: {message}\n{'-'*30}\n")

    def _mock_whatsapp_delivery(self, to: str, message: str):
        with open("mock_whatsapp.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] TO: {to}\nMESSAGE: {message}\n{'-'*30}\n")

    def _send_email_smtp(self, to_email: str, body: str):
        import smtplib
        from email.mime.text import MIMEText
        from src.config.settings import settings

        msg = MIMEText(body)
        msg["Subject"] = "Update on your application"
        msg["From"] = settings.smtp_email
        msg["To"] = to_email

        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_email, settings.smtp_password)
            server.sendmail(settings.smtp_email, to_email, msg.as_string())

    async def send_stage_update_notification(
        self,
        candidate_id: str,
        job_id: str,
        new_stage: CandidateStage,
        preferred_channel: Optional[Channel] = None,
        channel_override: Optional[Channel] = None,
        metadata: Optional[dict] = None
    ) -> dict:
        channel = self._determine_channel(
            preferred_channel or await self._get_candidate_preferred_channel(candidate_id),
            MessageType.STAGE_UPDATE,
            channel_override
        )

        profile_resp = (
            self.supabase
            .table("candidate_profiles")
            .select("full_name")
            .eq("candidate_id", candidate_id)
            .execute()
        )
        candidate_name = profile_resp.data[0]["full_name"] if profile_resp.data else "Candidate"

        role_resp = (
            self.supabase
            .table("jobs")
            .select("title")
            .eq("job_id", job_id)
            .execute()
        )
        role_title = role_resp.data[0]["title"] if role_resp.data else "Software Engineer"

        try:
            message = self.personalizer.generate_stage_update_message(
                candidate_name=candidate_name,
                role_title=role_title,
                new_stage=new_stage,
                channel=channel
            )
        except Exception:
            message = f"Update: You have moved to stage {new_stage.value}."

        return await self.send_message(
            candidate_id=candidate_id,
            job_id=job_id,
            stage=new_stage,
            message=message,
            preferred_channel=channel,
            message_type=MessageType.STAGE_UPDATE,
            channel_override=channel_override,
            metadata=metadata
        )
