from datetime import datetime
import asyncio
from typing import Optional
from src.db import get_supabase
from src.config import Channel, TouchpointType, DeliveryStatus, MessageType, CandidateStage
from src.agents.message_personalizer import MessagePersonalizer

class MessagingService:
    """Service for sending messages across multiple channels."""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.personalizer = MessagePersonalizer()
    
    def _determine_channel(
        self, 
        preferred_channel: str, 
        message_type: MessageType,
        override: Optional[Channel] = None
    ) -> Channel:
        """
        Determine which channel to use based on rules.
        """
        if override:
            return override
        
        if preferred_channel:
            return Channel(preferred_channel)
        
        # Default channel selection based on message type
        if message_type in [MessageType.REMINDER_24H, MessageType.REMINDER_1H]:
            return Channel.SMS
        elif message_type == MessageType.OFFER_SENT:
            return Channel.EMAIL
        
        return Channel.EMAIL
    
    async def send_message(
        self,
        candidate_id: str,
        message: str,
        channel: Channel,
        message_type: MessageType,
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Send message to candidate.
        Uses SMTP for emails, mocks others.
        Records touchpoint in database.
        """
        try:
            sent_successfully = False
            error_details = None

            # 1. Send via Real Channel
            if channel == Channel.EMAIL:
                try:
                    # Run SMTP in a separate thread to avoid blocking event loop
                    loop = asyncio.get_running_loop()
                    await loop.run_in_executor(None, self._send_email_smtp, candidate_id, message)
                    
                    print(f"📧 [SMTP] Sent email to {candidate_id}")
                    sent_successfully = True
                except Exception as e:
                    print(f"❌ [SMTP] Failed to send email: {e}")
                    error_details = str(e)
                    # Don't raise yet, we still want to record the attempt
            else:
                # Mock sending for other channels
                print(f"[{channel.value.upper()}] Sending to {candidate_id}: {message[:50]}...")
                sent_successfully = True

            # 2. Record touchpoint
            touchpoint_data = {
                "candidate_id": candidate_id,
                "type": TouchpointType.STATUS_UPDATE.value,
                "channel": channel.value,
                "message": message,
                "sentiment": None,
                "delivery_status": DeliveryStatus.SENT.value if sent_successfully else DeliveryStatus.FAILED.value,
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat()
            }
            
            if error_details:
                touchpoint_data["metadata"]["error"] = error_details
            
            response = self.supabase.table("candidate_touchpoints").insert(
                touchpoint_data
            ).execute()
            
            if response.data and len(response.data) > 0:
                result = {
                    "sent": sent_successfully,
                    "channel": channel.value,
                    "touchpoint_id": response.data[0]["id"],
                    "message": message
                }
                if not sent_successfully:
                    result["error"] = error_details
                return result
            
            raise Exception("Failed to record touchpoint")
            
        except Exception as e:
            # If recording failed, we still want to surface that
            raise Exception(f"Error sending message: {str(e)}")

    def _send_email_smtp(self, candidate_id: str, body: str):
        """Send email using SMTP."""
        import smtplib
        from email.mime.text import MIMEText
        from src.config.settings import settings
        
        # TODO: Get actual candidate email from DB
        # For now, using a test email or checking if candidate_id looks like an email
        to_email = candidate_id if "@" in candidate_id else "govindkushwaha6263@gmail.com" # Fallback test email
        
        msg = MIMEText(body)
        msg["Subject"] = "Update from TechCorp" # TODO: Make dynamic
        msg["From"] = settings.smtp_email
        msg["To"] = to_email

        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_email, settings.smtp_password)
            server.sendmail(settings.smtp_email, to_email, msg.as_string())
    
    async def send_stage_update_notification(
        self,
        candidate_id: str,
        message: Optional[str] = None,
        preferred_channel: str = "email",
        channel_override: Optional[Channel] = None,
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Send stage update notification to candidate.
        If message is not provided, generates one using AI.
        """
        
        # If message not provided, generate with AI (requires metadata)
        if not message and metadata and "stage_transition" in metadata:
            new_stage_val = metadata["stage_transition"]["to"]
            new_stage = CandidateStage(new_stage_val)
            
            # TODO: Fetch candidate name from DB ideally
            candidate_name = "Candidate" 
            role_title = "Software Engineer"
            
            try:
                message = self.personalizer.generate_stage_update_message(
                    candidate_name=candidate_name,
                    role_title=role_title,
                    new_stage=new_stage
                )
            except Exception as e:
                print(f"⚠️ AI Generation Failed: {e}. Falling back to default.")
                message = f"Update: You have moved to stage {new_stage_val}."

        channel = self._determine_channel(
            preferred_channel,
            MessageType.STAGE_UPDATE,
            channel_override
        )
        
        return await self.send_message(
            candidate_id=candidate_id,
            message=message or "Status Update",
            channel=channel,
            message_type=MessageType.STAGE_UPDATE,
            metadata=metadata
        )
