import requests
import time
import sys
import subprocess
import os

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    print(f"Testing Health Check at {BASE_URL}...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Health Check Passed")
            return True
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def test_ingestion():
    print("\nTesting Ingestion Endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/ingest", timeout=60)
        if response.status_code == 200:
            print("✅ Ingestion Success:", response.json())
            return True
        else:
            print(f"❌ Ingestion Failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def test_query():
    print("\nTesting Query Endpoint (Expecting Local Results)...")
    payload = {"question": "What are the effects of metformin?"}
    try:
        response = requests.post(f"{BASE_URL}/query", json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            print("✅ Query Success")
            print("Answer Preview:", data["answer"][:100])
            print("Sources:")
            for src in data["sources"]:
                print(f" - [{src['source']}] {src['title']}")
            
            # Check for local knowledge
            if any(s['source'] in ["Local Knowledge", "PubMed"] for s in data["sources"]):
                print("🎉 SUCCESS: Found Local Knowledge/PubMed citations!")
                return True
            else:
                print("⚠️ WARNING: No Local Knowledge/PubMed citations found. (Might be using fallbacks)")
                return False
        else:
            print(f"❌ Query Failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

if __name__ == "__main__":
    if not test_health():
        sys.exit(1)
    
    if not test_ingestion():
        sys.exit(1)
        
    time.sleep(2)
    if not test_query():
        sys.exit(1)
    
    print("\n✅ ALL TESTS PASSED")
