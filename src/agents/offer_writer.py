"""Offer writer agent using Gemini."""
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.agents.gemini_client import GeminiClient

class OfferWriter:
    """Agent for generating professional offer letters."""
    
    def __init__(self):
        """Initialize the agent."""
        self.client = GeminiClient(temperature=0.3)  # Lower temperature for formal documents
        self.llm = self.client.get_llm()
        
    def generate_offer_letter(
        self,
        candidate_name: str,
        role_title: str,
        compensation: Dict[str, Any],
        company_name: str = "TechCorp"
    ) -> str:
        """
        Generate a formal offer letter.
        """
        
        template = """
        You are an HR Manager at {company_name}.
        Write a formal employment offer letter.
        
        Candidate: {candidate_name}
        Role: {role_title}
        
        Compensation Details:
        - Annual CTC: {ctc}
        - Joining Bonus: {joining_bonus}
        - Joining Date: {joining_date}
        
        Structure:
        1. Header with Date
        2. Salutation
        3. Opening (Pleasure to offer)
        4. Role & Reporting (Report to Engineering Manager)
        5. Compensation Breakdown (Clear bullet points)
        6. Benefits Summary (Standard health, leave, remote work options)
        7. Next Steps (Sign by date)
        8. Welcoming Closing
        9. Signature
        
        Format: Markdown.
        Tone: Professional, Formal, Welcoming.
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        
        # Format currency for better reading
        ctc = f"₹{compensation.get('ctc', 0):,}"
        bonus = f"₹{compensation.get('joiningBonus', 0):,}"
        
        return chain.invoke({
            "company_name": company_name,
            "candidate_name": candidate_name,
            "role_title": role_title,
            "ctc": ctc,
            "joining_bonus": bonus,
            "joining_date": compensation.get("joiningDate", "TBD")
        })
