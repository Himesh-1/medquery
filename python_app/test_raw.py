import google.generativeai as genai
from config import GEMINI_API_KEY
import os

genai.configure(api_key=GEMINI_API_KEY)

model_name = "models/gemini-2.0-flash"

print(f"Testing raw SDK with {model_name}...")
try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Hello world")
    print("Success:")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
