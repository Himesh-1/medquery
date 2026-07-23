# MedQuery RAG

A RAG-powered medical QA system that verifies medical questions with live scientific sources from **PubMed**, **ClinicalTrials.gov**, **CDC/NIH**, **DuckDuckGo**, and **Wikipedia** using Google Gemini.

## Project Structure

- `python_app/`: Core application (FastAPI backend + Streamlit frontend)
  - `app.py`: Streamlit UI (`⚕️ MedQuery RAG`)
  - `server.py`: FastAPI server (`/api/query`)
  - `services/`: RAG retrieval pipeline and API wrappers
- `.env`: Environment API configuration (`GOOGLE_API_KEY`)

## How to Run

### 1. Start the Backend API Server
```bash
python python_app/server.py
```
*(Runs on http://localhost:8000)*

### 2. Start the Streamlit Frontend UI
```bash
streamlit run python_app/app.py
```
*(Runs on http://localhost:8501)*
