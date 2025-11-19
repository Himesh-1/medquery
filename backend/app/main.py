from fastapi import FastAPI, HTTPException
from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag import rag_service

app = FastAPI(title="MedQuery Automated API", version="2.0")

@app.get("/")
def health_check():
    return {"status": "ok", "mode": "Real-Time Automation"}

@app.post("/query", response_model=QueryResponse)
def query_knowledge_base(request: QueryRequest):
    try:
        # This now triggers a live PubMed search
        result = rag_service.get_answer(request.question)
        return result
    except Exception as e:
        # Typical errors: PubMed API timeout, or no results found
        raise HTTPException(status_code=500, detail=str(e))