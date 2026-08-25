import os
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "VeristasOS"


def test_api_info():
    response = client.get("/api")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "VeristasOS"
    assert "capabilities" in data
    assert "endpoints" in data


def test_ai_status_endpoint():
    response = client.get("/api/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert "available" in data
    assert data["provider"] == "llama.cpp"
    assert data["model"] == "Qwen2.5-3B-Instruct"


def test_analyze_endpoint_unified():
    response = client.post(
        "/analyze",
        json={
            "text": "BREAKING NEWS! Shocking discovery announced by scientists today!",
            "source_url": "https://example.com/news",
            "source_name": "Example Global",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "analysis" in data

    analysis = data["analysis"]
    assert "overall_risk_score" in analysis
    assert "classification" in analysis
    assert "confidence" in analysis
    assert "claims" in analysis
    assert "provenance" in analysis
    assert "indicators" in analysis
    assert "recommendations" in analysis


def test_api_analyze_alias():
    response = client.post(
        "/api/analyze",
        json={
            "text": "The municipal council held an open meeting on public infrastructure.",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["analysis"]["classification"] in ["LOW RISK", "MODERATE RISK", "HIGH RISK", "VERY HIGH RISK"]


def test_analyze_rejects_empty_text():
    response = client.post(
        "/analyze",
        json={"text": ""},
    )
    assert response.status_code == 422


def test_analyze_image_endpoint():
    fake_png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0"
        b"\x00\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    response = client.post(
        "/api/analyze-image",
        files={"file": ("test.png", fake_png, "image/png")},
        data={"article_text": "Sample text for consistency verification."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "image_analysis" in data
    assert data["image_analysis"]["filename"] == "test.png"
    assert "sha256" in data["image_analysis"]
    assert "perceptual_hash" in data["image_analysis"]