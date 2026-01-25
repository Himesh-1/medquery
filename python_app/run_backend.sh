#!/bin/bash
# Wrapper to run Backend cleanly
echo "Starting Backend on port $PORT..."
uvicorn server:app --host 0.0.0.0 --port $PORT
