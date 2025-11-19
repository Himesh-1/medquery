from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    question: str

class SourceDocument(BaseModel):
    content: str
    source: str
    title: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]

class IngestRequest(BaseModel):
    documents: List[dict]  # List of raw JSON objects from PubMed