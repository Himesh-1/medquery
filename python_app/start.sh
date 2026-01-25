#!/bin/bash

# Start FastAPI in the background on port 8000
echo "Starting Backend on port 8000..."
uvicorn server:app --host 0.0.0.0 --port 8000 &

# Start Streamlit in the foreground on the Render-assigned PORT
echo "Starting Frontend on port $PORT..."
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
