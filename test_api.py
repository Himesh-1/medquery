import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")

print(f"Testing API Key: {api_key[:10]}...")
print(f"Model: {model_name}")

genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name)

try:
    response = model.generate_content("Say hello")
    print(f"Success! Response: {response.text}")
except Exception as e:
    print(f"FAILED: {e}")
