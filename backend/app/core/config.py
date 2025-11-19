import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "MedQuery API"
    GOOGLE_API_KEY: str
    GEMINI_MODEL_NAME: str = "gemini-2.0-flash"
    EMBEDDING_MODEL_NAME: str = "models/text-embedding-004" # Standard latest embedding
    VECTOR_DB_PATH: str = "faiss_index"

    class Config:
        env_file = ".env"

settings = Settings()