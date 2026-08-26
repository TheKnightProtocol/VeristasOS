import os
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.services.deepfake_detector import deepfake_detector

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "VeristasOS"
    assert "version" in data
    assert "environment" in data


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


def test_media_authenticity_status_endpoint():
    response = client.get("/api/media/authenticity/status")
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is True
    assert "model" in data
    assert "type" in data
    assert "description" in data


def test_media_deepfake_status_endpoint():
    response = client.get("/api/media/deepfake/status")
    assert response.status_code == 200
    data = response.json()
    assert "available" in data
    assert "model" in data
    assert "type" in data


def test_deepfake_detector_disabled_by_default():
    fake_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    res = deepfake_detector.analyze_media(fake_png, "test.png")
    assert res["available"] is False or os.getenv("DEEPFAKE_ENABLED", "false").lower() == "true"
    assert "explanation" in res


def test_deepfake_detector_enabled_mode(monkeypatch):
    monkeypatch.setenv("DEEPFAKE_ENABLED", "true")
    fake_png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0"
        b"\x00\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    res = deepfake_detector.analyze_media(fake_png, "test.png")
    assert res["available"] is True
    assert "deepfake_risk" in res
    assert "manipulation_risk" in res
    assert "signals" in res


def test_search_endpoint_get_paginated():
    response = client.get("/api/search?q=transit&limit=10&offset=0&sort_by=relevance")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["query"] == "transit"
    assert "total_matches" in data
    assert "results" in data


def test_semantic_search_post_paginated():
    response = client.post(
        "/api/semantic-search",
        json={"query": "transit", "limit": 10, "offset": 0, "sort_by": "relevance"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "results" in data


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
    assert "authenticity_screening" in data["image_analysis"]
    assert "deepfake_analysis" in data["image_analysis"]


def test_api_version_endpoint():
    response = client.get("/api/version")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "VeristasOS"
    assert "version" in data


def test_ai_analyze_endpoint():
    response = client.post(
        "/api/ai/analyze",
        json={"text": "Breaking news regarding global financial markets."},
    )
    assert response.status_code == 200
    data = response.json()
    assert "verdict" in data
    assert "confidence" in data
    assert "reasoning" in data


def test_analyze_image_invalid_extension():
    response = client.post(
        "/api/analyze-image",
        files={"file": ("malicious.exe", b"binary content", "application/x-msdownload")},
    )
    assert response.status_code == 400
    assert "Unsupported" in response.json()["detail"]


def test_analyze_image_empty_file():
    response = client.post(
        "/api/analyze-image",
        files={"file": ("empty.png", b"", "image/png")},
    )
    assert response.status_code == 400
    assert "Empty" in response.json()["detail"]