from fastapi import FastAPI, HTTPException
from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag import rag_service
from app.services.ingestion import ingestion_pipeline

app = FastAPI(title="MedQuery Automated API", version="2.0")

@app.get("/")
def health_check():
    return {"status": "ok", "mode": "Real-Time Automation"}

@app.post("/ingest")
def ingest_data():
    """Triggers the ingestion of local PubMed data."""
    try:
        result = ingestion_pipeline.ingest_from_file()
        if "❌" in result:
             raise HTTPException(status_code=400, detail=result)
        return {"status": "success", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
def query_knowledge_base(request: QueryRequest):
    try:
        # This now triggers a live PubMed search
        result = rag_service.get_answer(request.question)
        return result
    except Exception as e:
        # Typical errors: PubMed API timeout, or no results found
        raise HTTPException(status_code=500, detail=str(e))