# Deployment Guide (Split Services)

Since you previously had **Backend** and **Frontend** as separate services, you can maintain that structure. This allows you to scale them independently.

## Part 1: Update the Backend Service

This service will run the FastAPI Python API.

1.  **Select your EXISTING Backend Service** on Render.
2.  **Settings** > Update:
    - **Root Directory**: `python_app`
    - **Build Command**: `pip install -r requirements.txt`
    - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
3.  **Environment Variables**:
    - Add `GEMINI_API_KEY`: Your Google API Key.
    - Add `PYTHON_VERSION`: `3.10.12`.
4.  **Deploy**: Verification - this URL (e.g., `https://my-backend.onrender.com`) will return JSON if you visit `/docs`.

## Part 2: Update the Frontend Service

This service will run the Streamlit UI.
_Note: Ensure this is a "Web Service" on Render, not a "Static Site". Streamlit requires a server._

1.  **Select your EXISTING Frontend Service** on Render.
2.  **Settings** > Update:
    - **Root Directory**: `python_app`
    - **Build Command**: `pip install -r requirements.txt`
    - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
3.  **Environment Variables**:
    - Add `BACKEND_URL`: The URL of your **Backend Service** (from Part 1), e.g., `https://my-backend.onrender.com`.
      - _Important_: Do not include a trailing slash `/`.
    - Add `PYTHON_VERSION`: `3.10.12`.
4.  **Deploy**: This URL (e.g., `https://my-frontend.onrender.com`) is what you will share on your resume.

---

### Summary of Changes

- **Old Backend (Node)** -> **New Backend (FastAPI)**.
- **Old Frontend (React)** -> **New Frontend (Streamlit)**.
- **Connection**: The Frontend knows where the Backend is via the `BACKEND_URL` variable.
