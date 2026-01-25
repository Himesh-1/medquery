import os
from dotenv import load_dotenv

# Load from parent's server folder since we are reusing keys
# d:/med/server/.env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'server', '.env')
load_dotenv(env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print(f"WARNING: GEMINI_API_KEY not found at {env_path}")
