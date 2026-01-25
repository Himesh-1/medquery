import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_API_KEY
from dotenv import load_dotenv
import os

# Ensure clean env load
load_dotenv()

async def test_llm():
    print("Testing LLM Connection...")
    print(f"Key loaded: {bool(GEMINI_API_KEY)}")
    if GEMINI_API_KEY:
        print(f"Key preview: {GEMINI_API_KEY[:5]}...")

    try:
        llm = ChatGoogleGenerativeAI(model="models/gemini-flash-latest", google_api_key=GEMINI_API_KEY)
        query = "Correct this typo: helo wrld"
        print(f"Invoking with: {query}")
        
        response = await llm.ainvoke(query)
        print("Response received!")
        print(response.content)
    except Exception as e:
        print(f"LLM Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm())
