#!/bin/bash
# Wrapper to run Frontend cleanly
echo "Starting Frontend on port $PORT..."
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
