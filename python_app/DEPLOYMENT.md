# Migration Guide (Final Fix)

It seems Render is struggling with the complex commands. I have created simple **wrapper scripts** to fix this definitively.

## Phase 1: Update Code

1.  **Commit & Push** your latest changes (I added `run_backend.sh` and `run_frontend.sh` and updated `Dockerfile`).

## Phase 2: Update Backend Service

1.  **Select Backend Service** on Render.
2.  **Settings** -> **Build & Deploy**.
3.  **Docker Command**:
    ```bash
    ./run_backend.sh
    ```
4.  **Environment**: Ensure `PORT` is set to `10000` (or leave it, Render creates it automatically, script uses it).
5.  **Deploy**.

## Phase 3: Update Frontend Service

1.  **Select Frontend Service** on Render.
2.  **Settings** -> **Build & Deploy**.
3.  **Docker Command**:
    ```bash
    ./run_frontend.sh
    ```
4.  **Environment**: Ensure `PORT` is set to `10000` (optional).
    - **CRITICAL**: Ensure `BACKEND_URL` is set to your Backend URL.
5.  **Deploy**.

---

## Why this fixes the error

The error `sh: 1: uvicorn server:app ... : not found` happened because Render was treating the entire command string as a single filename (likely due to copy-paste quotes).
By using `./run_backend.sh`, we give it a single, clean file to execute, which contains the logic.
