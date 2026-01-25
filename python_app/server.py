from fastapi import FastAPI
from pydantic import BaseModel
from services.rag_chain import rag_pipeline
import uvicorn

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/api/query")
async def query_endpoint(req: QueryRequest):
    result = await rag_pipeline(req.query)
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
