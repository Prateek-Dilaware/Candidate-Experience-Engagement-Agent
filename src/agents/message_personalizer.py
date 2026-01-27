"""Message personalization agent using Gemini (safe, structured, channel-aware)."""

from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from src.agents.gemini_client import GeminiClient
from src.config import CandidateStage, MessageType, Channel


# ---------- Structured Output Models ----------

class MessageOutput(BaseModel):
    subject: Optional[str] = Field(
        default=None,
        description="Email subject (null for SMS/WhatsApp)."
    )
    body: str = Field(
        description="Main message content to send to candidate."
    )


# ---------- Agent Class ----------

class MessagePersonalizer:
    """Agent for generating personalized candidate messages."""

    def __init__(self):
        self.client = GeminiClient(temperature=0.5)
        self.llm = self.client.get_llm()

        # Enforce structured output
        self.structured_llm = self.llm.with_structured_output(MessageOutput)

    # ---------------------------
    # Prompt Builders (by channel)
    # ---------------------------

    def _email_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_template("""
You are a professional HR recruiter at {company_name}.
Write a formal but warm EMAIL for a candidate.

Candidate Name: {candidate_name}
Role: {role_title}
New Stage: {new_stage}

Stage meanings:
- SCREENED: Application reviewed and moving forward
- INTERVIEW_SCHEDULED: Interview is being scheduled
- INTERVIEWED: Thank them, feedback in progress
- OFFERED: Congratulate, offer coming soon
- REJECTED: Polite rejection

Rules:
- Provide subject and body.
- Professional and encouraging tone.
- Max 150 words for body.
- No emojis.
""")

    def _sms_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_template("""
You are a recruiter sending an SMS.

Candidate Name: {candidate_name}
Role: {role_title}
New Stage: {new_stage}

Rules:
- Only short body text (no subject).
- Max 40 words.
- Very clear and polite.
- No emojis.
""")

    def _whatsapp_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_template("""
You are a recruiter sending a WhatsApp message.

Candidate Name: {candidate_name}
Role: {role_title}
New Stage: {new_stage}

Rules:
- Friendly but professional.
- No subject.
- Max 60 words.
- Light conversational tone allowed.
- No emojis unless appropriate.
""")

    # ---------------------------
    # Main Public API (SAFE)
    # ---------------------------

    def generate_stage_update_message(
        self,
        candidate_name: str,
        role_title: str,
        new_stage: CandidateStage,
        company_name: str = "TalentFlow",
        channel: Channel = Channel.EMAIL
    ) -> str:
        """
        Generate a personalized stage update message.
        SAFE: returns string (body only) so current APIs do not break.
        """

        prompt = self._select_prompt(channel)
        chain = prompt | self.structured_llm

        try:
            result: MessageOutput = chain.invoke({
                "company_name": company_name,
                "candidate_name": candidate_name,
                "role_title": role_title,
                "new_stage": new_stage.value,
            })

            # Backward compatibility: return only body
            return result.body.strip()

        except Exception as e:
            # Hard fallback (never let LLM break pipeline)
            return f"Update: Your application has moved to stage {new_stage.value}."

    def generate_status_update(
        self,
        candidate_name: str,
        role_title: str,
        message_type: MessageType,
        context: dict = None,
        channel: Channel = Channel.EMAIL
    ) -> str:
        """
        Generate reminder / feedback messages (safe).
        """

        prompt = ChatPromptTemplate.from_template("""
You are an HR recruiter.

Candidate: {candidate_name}
Role: {role_title}
Message Type: {message_type}
Context: {context}

Rules:
- Be brief and helpful.
- Follow channel style: {channel}.
""")

        chain = prompt | self.structured_llm

        try:
            result: MessageOutput = chain.invoke({
                "candidate_name": candidate_name,
                "role_title": role_title,
                "message_type": message_type.value,
                "context": str(context or {}),
                "channel": channel.value
            })

            return result.body.strip()

        except Exception:
            return "Reminder: Please check your interview schedule."

    # ---------------------------
    # Helper
    # ---------------------------

    def _select_prompt(self, channel: Channel) -> ChatPromptTemplate:
        if channel == Channel.SMS:
            return self._sms_prompt()
        elif channel == Channel.WHATSAPP:
            return self._whatsapp_prompt()
        else:
            return self._email_prompt()
