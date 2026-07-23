import os
from dotenv import load_dotenv

# Load from root .env or backend .env
root_env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
backend_env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', '.env')
load_dotenv(root_env)
load_dotenv(backend_env)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not GEMINI_API_KEY:
    print(f"WARNING: GEMINI_API_KEY / GOOGLE_API_KEY not found")
