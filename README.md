# MedQuery (scaffold)

Small scaffold for a RAG-powered medical QA system.

- `backend/`: FastAPI backend
- `frontend/`: Streamlit demo frontend
- `sample_data/`: sample dataset

Run backend:

```
cd backend
python -m uvicorn app.main:app --reload
```

Run frontend:

```
cd frontend
streamlit run app.py
```
