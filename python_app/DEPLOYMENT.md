# Migration Guide: Node/React -> Python/Streamlit (Docker)

Follow these exact steps to update your existing Render services.

## Phase 1: GitHub

1.  **Commit & Push**: Ensure your `python_app` folder (containing `Dockerfile`, `requirements.txt`, `server.py`, `app.py`) is pushed to your GitHub repository.

---

## Phase 2: Update Backend Service

_Goal: Replace Node.js server with FastAPI._

1.  **Open Render Dashboard** and click on your **Backend Service**.
2.  Go to **Settings** -> **Build & Deploy**.
3.  Update the following fields (scroll down to "Docker" section if needed):
    - **Root Directory**: `python_app`
    - **Dockerfile Path**: `Dockerfile`
    - **Docker Build Context**: `.`
    - **Docker Command**: `sh -c "uvicorn server:app --host 0.0.0.0 --port $PORT"`
4.  Go to **Environment**.
5.  Add/Update:
    - `GEMINI_API_KEY`: (Your Google API Key)
    - `PORT`: `10000` (Optional, ensures it matches the command default)
6.  **Save Changes** (if applicable) or trigger a **Manual Deploy** > **Clear build cache & deploy** (recommended to switch runtimes cleanly).

---

## Phase 3: Update Frontend Service

_Goal: Replace React Static Site with Streamlit Web Service._

**Important**: If your previous frontend was a **Static Site** on Render, you **cannot** change it to a generic Web Service. You must delete it and create a **New Web Service**.
_However, if it was already a Web Service (Docker), follow these steps:_

1.  **Open Render Dashboard** and click on your **Frontend Service**.
2.  Go to **Settings** -> **Build & Deploy**.
3.  Update fields:
    - **Root Directory**: `python_app`
    - **Dockerfile Path**: `Dockerfile`
    - **Docker Build Context**: `.`
    - **Docker Command**: `sh -c "streamlit run app.py --server.port $PORT --server.address 0.0.0.0"`
4.  Go to **Environment**.
5.  Add/Update:
    - `BACKEND_URL`: `https://your-backend-service-name.onrender.com` (Copy url from Phase 2)
6.  **Deploy**.

---

## Troubleshooting

- **"Port Bound" Error**: If logs say "Address already in use", remove the `PORT` env var and let Render assign it automatically.
- **"Static Site" Limitation**: As mentioned, Streamlit requires a CPU to run python. Static sites (free CDN) cannot run Streamlit. You need a "Web Service" (Free Tier available).
