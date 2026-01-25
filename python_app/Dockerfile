# Use official Python runtime
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed (e.g. for build tools)
# RUN apt-get update && apt-get install -y build-essential

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Make the start script executable
RUN chmod +x start.sh

# Expose ports (FastAPI=8000, Streamlit=8501 or $PORT)
EXPOSE 8000
EXPOSE 8501

# Default command: Run the start script (Hybrid Backend+Frontend)
# You can override this in Render 'Docker Command' field
CMD ["./start.sh"]
