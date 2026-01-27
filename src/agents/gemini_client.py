"""Gemini client wrapper for LangChain integration."""
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config.settings import settings

class GeminiClient:
    """Wrapper for Google Gemini model."""
    
    def __init__(self, model_name: str = "gemini-flash-latest", temperature: float = 0.4):
        """Initialize Gemini client."""
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.google_api_key,
            temperature=temperature,
            convert_system_message_to_human=True
        )
    
    def get_llm(self):
        """Get the underlying LangChain LLM instance."""
        return self.llm
