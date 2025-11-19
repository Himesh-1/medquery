import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from app.core.config import settings

class GeminiService:
    """
    Reusable wrapper for Gemini 2.0 Flash API interactions.
    """
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.2, # Low temp for factual accuracy
            convert_system_message_to_human=True
        )
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY
        )

    def get_llm(self):
        return self.llm

    def get_embeddings(self):
        return self.embeddings

gemini_service = GeminiService()