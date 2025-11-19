FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
# Attempt to install from file
RUN pip install --no-cache-dir -r requirements.txt

# --- FORCE INSTALLATION HERE ---
# This guarantees langchain is installed, overriding any cache issues
RUN pip install langchain langchain-community langchain-google-genai
# -------------------------------

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]