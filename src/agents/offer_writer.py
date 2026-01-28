"""Offer writer agent using Gemini (no compensation, structured)."""

from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from src.agents.gemini_client import GeminiClient


class OfferOutput(BaseModel):
    title: Optional[str] = Field(default="Employment Offer Letter")
    body: str


class OfferWriter:
    """Agent for generating professional offer letters."""

    def __init__(self):
        self.client = GeminiClient(temperature=0.3)
        self.llm = self.client.get_llm()
        self.structured_llm = self.llm.with_structured_output(OfferOutput)

    def generate_offer_letter(
        self,
        candidate_name: str,
        role_title: str,
        joining_date: str,
        company_name: str = "TalentFlow"
    ) -> str:
        """
        Generate a formal offer letter (without compensation).
        SAFE: returns string body only.
        """

        template = """

You are an HR recruiter at {company_name}.

Write a short, professional offer letter email.

Candidate Name: {candidate_name}
Role: {role_title}
Joining Date: {joining_date}

Rules:
- This email itself IS the full offer letter.
- Do NOT mention any separate documents, attachments, or future packages.
- Do NOT mention compensation or salary.
- Do NOT use placeholders like [HR Manager], [Address], or [Location].
- Keep it under 150 words.
- Use a warm and professional tone.
- Start with: "Dear {candidate_name},"
- Clearly ask the candidate to reply to this email to accept the offer.
- End with: "Regards, {company_name} HR Team"
"""


        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.structured_llm

        try:
            result: OfferOutput = chain.invoke({
                "company_name": company_name,
                "candidate_name": candidate_name,
                "role_title": role_title,
                "joining_date": joining_date
            })
            return result.body.strip()

        except Exception:
            return (
                f"Dear {candidate_name}, we are pleased to offer you the position of "
                f"{role_title} with a joining date of {joining_date}."
            )
