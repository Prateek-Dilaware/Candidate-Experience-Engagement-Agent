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
You are an HR Manager at {company_name}.
Write a formal employment offer letter.

Candidate: {candidate_name}
Role: {role_title}
Joining Date: {joining_date}

Structure:
1. Header with Date
2. Salutation
3. Opening (pleasure to offer)
4. Role & Reporting
5. Joining Date clearly mentioned
6. Benefits Summary (standard benefits only)
7. Next Steps (sign & respond)
8. Professional Closing

Rules:
- Return markdown content only.
- Formal and professional tone.
- No emojis.
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
