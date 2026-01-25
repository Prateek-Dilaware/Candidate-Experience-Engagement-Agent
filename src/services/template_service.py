"""Template service - Manages message templates."""
from typing import Dict, Any
from src.config import MessageType, CandidateStage


class TemplateService:
    """Service for managing message templates."""
    
    # Basic templates (will be enhanced with Gemini later)
    TEMPLATES = {
        MessageType.STAGE_UPDATE: {
            CandidateStage.SCREENED: "Hi {{candidateName}}, great news! Your application for {{roleTitle}} has been reviewed and you've been shortlisted for the next stage.",
            CandidateStage.INTERVIEW_SCHEDULED: "Hi {{candidateName}}, your interview for {{roleTitle}} is being scheduled. We'll share the details shortly.",
            CandidateStage.INTERVIEWED: "Hi {{candidateName}}, thank you for taking the time to interview with us for {{roleTitle}}. We're reviewing your performance and will get back to you soon.",
            CandidateStage.OFFERED: "Hi {{candidateName}}, congratulations! We're pleased to extend an offer for the {{roleTitle}} position. Details are being prepared.",
            CandidateStage.OFFER_ACCEPTED: "Hi {{candidateName}}, welcome aboard! We're excited to have you join us for {{roleTitle}}. Onboarding details coming soon.",
            CandidateStage.ONBOARDING: "Hi {{candidateName}}, your onboarding for {{roleTitle}} is about to begin. We'll guide you through the process.",
            CandidateStage.CLOSED_REJECTED: "Hi {{candidateName}}, thank you for your interest in {{roleTitle}}. Unfortunately, we won't be moving forward at this time. We wish you the best in your job search.",
            CandidateStage.CLOSED_WITHDRAWN: "Hi {{candidateName}}, we've noted your decision to withdraw from the {{roleTitle}} position. Thank you for your time and consideration.",
        }
    }
    
    def get_template(
        self, 
        message_type: MessageType, 
        stage: CandidateStage
    ) -> str:
        """Get template for message type and stage."""
        if message_type in self.TEMPLATES:
            return self.TEMPLATES[message_type].get(
                stage, 
                "Hi {{candidateName}}, we have an update regarding your application for {{roleTitle}}."
            )
        return "Hi {{candidateName}}, we have an update regarding your application."
    
    def render_template(
        self, 
        template: str, 
        variables: Dict[str, Any]
    ) -> str:
        """Render template with variables."""
        message = template
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            message = message.replace(placeholder, str(value))
        return message
    
    def generate_stage_update_message(
        self,
        candidate_name: str,
        role_title: str,
        new_stage: CandidateStage
    ) -> str:
        """Generate stage update message."""
        template = self.get_template(MessageType.STAGE_UPDATE, new_stage)
        
        variables = {
            "candidateName": candidate_name,
            "roleTitle": role_title
        }
        
        return self.render_template(template, variables)
