from fastapi import FastAPI, HTTPException
import traceback
import sys

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
        if "ERROR:" in result:
             raise HTTPException(status_code=400, detail=result)
        return {"status": "success", "message": result}
    except Exception as e:
        with open("error_log.txt", "a") as f:
            f.write(f"INGEST ERROR: {str(e)}\n")
            traceback.print_exc(file=f)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
def query_knowledge_base(request: QueryRequest):
    try:
        print(f"--- Processing Query: {request.question} ---")
        result = rag_service.get_answer(request.question)
        return result
    except Exception as e:
        # Avoid printing the exception directly to console if it might contain emojis
        # though str(e) from an API usually doesn't.
        with open("error_log.txt", "a") as f:
            f.write(f"QUERY ERROR: {str(e)}\n")
            traceback.print_exc(file=f)
        raise HTTPException(status_code=500, detail=str(e))