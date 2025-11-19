import os
from typing import List
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from app.services.gemini import gemini_service

class IngestionPipeline:
    def __init__(self):
        self.embeddings = gemini_service.get_embeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.vector_store = None

    def clean_text(self, text: str) -> str:
        """Basic text cleaning."""
        if not text:
            return ""
        return " ".join(text.split())

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
                    "source": item.get("pmid", "Unknown ID")
                }
                documents.append(Document(page_content=content, metadata=meta))

        if not documents:
            return "No valid documents to ingest."

        chunks = self.text_splitter.split_documents(documents)
        
        # Create/Overwrite Index
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        
        # Persist to disk (optional, but good for restarts)
        # self.vector_store.save_local("faiss_index") 
        
        return f"Successfully indexed {len(chunks)} chunks from {len(documents)} documents."

    def get_vector_store(self):
        return self.vector_store

# Singleton instance
ingestion_pipeline = IngestionPipeline()