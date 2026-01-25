"""Message personalization agent using Gemini."""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.agents.gemini_client import GeminiClient
from src.config import CandidateStage, MessageType

class MessagePersonalizer:
    """Agent for generating personalized candidate messages."""
    
    def __init__(self):
        """Initialize the agent."""
        self.client = GeminiClient(temperature=0.7)
        self.llm = self.client.get_llm()
        
    def generate_stage_update_message(
        self,
        candidate_name: str,
        role_title: str,
        new_stage: CandidateStage,
        company_name: str = "TechCorp"
    ) -> str:
        """
        Generate a personalized message for a stage transition.
        """
        template = """
        You are a professional HR recruiter at {company_name}.
        Draft a friendly and professional {channel} message for a candidate.
        
        Candidate Name: {candidate_name}
        Role: {role_title}
        New Stage: {new_stage}
        
        Context based on stage:
        - SCREENED: Inform them their application has been reviewed and we want to move forward.
        - INTERVIEW_SCHEDULED: Confirm the interview is being scheduled.
        - INTERVIEWED: Thank them for their time and mention we are gathering feedback.
        - OFFERED: Congratulate them and mention an offer is on the way!
        - REJECTED: Politely let them know we are not moving forward.
        
        Tone: Professional, Warm, Encouraging.
        Length: Concise (under 150 words).
        
        Draft the message content only (no subject line needed for SMS/WhatsApp, but include for Email if implied).
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        
        # Determine channel tone (implicitly handled by LLM but good for context)
        channel = "email" # default
        
        return chain.invoke({
            "company_name": company_name,
            "candidate_name": candidate_name,
            "role_title": role_title,
            "new_stage": new_stage.value,
            "channel": channel
        })

    def generate_status_update(
        self,
        candidate_name: str,
        role_title: str,
        message_type: MessageType,
        context: dict = None
    ) -> str:
        """
        Generate a specific status update message.
        """
        template = """
        You are a professional HR recruiter.
        Draft a message for {candidate_name} applying for {role_title}.
        
        Message Type: {message_type}
        Additional Context: {context}
        
        Guidelines:
        - REMINDER_24H: Remind them about interview in 24 hours.
        - REMINDER_1H: Remind them about interview in 1 hour.
        - FEEDBACK_SURVEY: Ask for feedback on their experience.
        
        Keep it brief and helpful.
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        
        return chain.invoke({
            "candidate_name": candidate_name,
            "role_title": role_title,
            "message_type": message_type.value,
            "context": str(context or {})
        })
