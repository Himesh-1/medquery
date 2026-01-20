import os
import json
from typing import List
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from app.services.gemini import gemini_service
from app.core.config import settings

class IngestionPipeline:
    def __init__(self):
        self.embeddings = gemini_service.get_embeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.vector_store = None
        self._load_local_index()

    def _load_local_index(self):
        """Attempts to load an existing FAISS index."""
        if os.path.exists(settings.VECTOR_DB_PATH):
            try:
                self.vector_store = FAISS.load_local(
                    settings.VECTOR_DB_PATH, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print(f"✅ Loaded existing vector store from {settings.VECTOR_DB_PATH}")
            except Exception as e:
                print(f"⚠️ Could not load vector store: {e}")

    def clean_text(self, text: str) -> str:
        """Basic text cleaning."""
        if not text:
            return ""
        return " ".join(text.split())

    def ingest_from_file(self, file_path: str = "data/pubmed_data.json") -> str:
        """Loads JSON data from file and ingests it."""
        if not os.path.exists(file_path):
             # Try root path fallback
            root_path = os.path.join(os.getcwd(), "..", "pubmed_data.json")
            if os.path.exists(root_path):
                file_path = root_path
            else:
                return f"❌ File not found: {file_path}"
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return self.process_documents(data)
        except Exception as e:
            return f"❌ Error reading file: {e}"

    def process_documents(self, raw_docs: List[dict]) -> str:
        """
        Takes raw JSON, creates Documents, chunks them, and creates FAISS index.
        """
        documents = []
        for item in raw_docs:
            content = self.clean_text(item.get("abstract", "") or item.get("body", ""))
            if content:
                meta = {
                    "title": item.get("title", "Unknown Title"),
                    "source": item.get("pmid", "Unknown ID"),
                    "pmid": item.get("pmid", "Unknown ID") # Ensure pmid is available
                }
                documents.append(Document(page_content=content, metadata=meta))

        if not documents:
            return "No valid documents to ingest."

        chunks = self.text_splitter.split_documents(documents)
        
        # Create/Overwrite Index
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        
        # Persist to disk
        self.vector_store.save_local(settings.VECTOR_DB_PATH)
        
        return f"Successfully indexed {len(chunks)} chunks from {len(documents)} documents."

    def get_vector_store(self):
        return self.vector_store

# Singleton instance
ingestion_pipeline = IngestionPipeline()