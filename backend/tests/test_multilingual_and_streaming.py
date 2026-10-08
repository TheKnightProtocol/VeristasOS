"""
VeristasOS — General-Purpose Multilingual AI & Streaming Test Suite
Tests general knowledge, programming, Indian multilingual queries, SSE streaming,
and internationalization components.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ai_service import ai_service_instance

client = TestClient(app)


def test_general_knowledge_quantum_computing():
    """Test general-purpose quantum computing question."""
    res = client.post("/api/chat", json={"message": "What is quantum computing?", "user_name": "TestUser"})
    assert res.status_code == 200
    data = res.json()
    assert "message" in data
    assert "quantum" in data["message"].lower() or "qubit" in data["message"].lower()
    assert data["action"] == "RESPOND"


def test_programming_python_sort_code():
    """Test Python programming code generation request."""
    res = client.post("/api/chat", json={"message": "Write a Python program to sort a list.", "user_name": "Coder"})
    assert res.status_code == 200
    data = res.json()
    assert "```python" in data["message"] or "python" in data["message"].lower()
    assert data["action"] == "RESPOND"


def test_programming_java_binary_search():
    """Test Java binary search code request."""
    res = client.post("/api/chat", json={"message": "Give me Java code for binary search.", "user_name": "Coder"})
    assert res.status_code == 200
    data = res.json()
    assert "java" in data["message"].lower() or "binary" in data["message"].lower()
    assert data["action"] == "RESPOND"


def test_hindi_upi_query():
    """Test Hindi language query response."""
    res = client.post("/api/chat", json={"message": "भारत में UPI कैसे काम करता है?", "user_name": "User"})
    assert res.status_code == 200
    data = res.json()
    assert "message" in data
    assert data["action"] == "RESPOND"


def test_email_draft_generation():
    """Test email draft writing request."""
    res = client.post("/api/chat", json={"message": "Write an email to my professor asking for an extension.", "user_name": "Student"})
    assert res.status_code == 200
    data = res.json()
    assert "Subject:" in data["message"] or "Professor" in data["message"] or "Dear" in data["message"]
    assert data["action"] == "RESPOND"


def test_study_plan_generation():
    """Test 7-day machine learning study plan request."""
    res = client.post("/api/chat", json={"message": "Make a 7-day study plan for machine learning.", "user_name": "Learner"})
    assert res.status_code == 200
    data = res.json()
    assert "Day" in data["message"] or "Python" in data["message"] or "Machine Learning" in data["message"]


def test_chat_streaming_endpoint():
    """Test POST /api/chat/stream SSE endpoint."""
    res = client.post("/api/chat/stream", json={"message": "Explain AI simply.", "user_name": "User"})
    assert res.status_code == 200
    assert "text/event-stream" in res.headers["content-type"]
    body_text = res.text
    assert "data:" in body_text


def test_multilingual_indian_language_queries():
    """Test queries in Bengali, Tamil, Telugu, Urdu, and Hinglish."""
    bengali_res = client.post("/api/chat", json={"message": "এই সিস্টেম কীভাবে কাজ করে?", "user_name": "User"})
    assert bengali_res.status_code == 200

    tamil_res = client.post("/api/chat", json={"message": "செயற்கை நுண்ணறிவு என்றால் என்ன?", "user_name": "User"})
    assert tamil_res.status_code == 200

    urdu_res = client.post("/api/chat", json={"message": "کمپیوٹر سائنس کیا ہے؟", "user_name": "User"})
    assert urdu_res.status_code == 200
