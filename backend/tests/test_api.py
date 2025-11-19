from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model": "Gemini-2.0-Flash"}

def test_query_empty_db():
    # Expecting a polite response even if DB is empty
    response = client.post("/query", json={"question": "What is diabetes?"})
    assert response.status_code == 200
    assert "answer" in response.json()