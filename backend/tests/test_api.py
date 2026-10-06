import os
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.services.deepfake_detector import deepfake_detector
from app.services.privacy_scanner import scan_privacy_signals
from app.services.scam_detector import detect_scam_signals

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


def test_privacy_scanner_aadhaar_pan_upi_masking():
    sample_text = "Please send your Aadhaar 4589 1234 5678 and PAN ABCDE1234F to user@upi immediately."
    res = scan_privacy_signals(sample_text)
    assert res["sensitive_data_detected"] >= 3
    assert "XXXX XXXX 5678" in res["masked_text"]
    assert "XXXXX1234X" in res["masked_text"]
    assert "u***@upi" in res["masked_text"]
    assert res["privacy_grade"] in ["C", "F"]


def test_scam_detector_kyc_threat():
    sample_text = "Your bank account will be blocked today. Verify your KYC immediately or send OTP."
    res = detect_scam_signals(sample_text)
    assert res["scam_risk"] == "HIGH RISK"
    assert res["scam_score"] >= 50
    assert len(res["triggers_found"]) >= 2


def test_api_verify_dual_layer_endpoint():
    response = client.post(
        "/api/verify",
        json={"text": "BREAKING! Secret discovery announced overnight by unverified sources!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "verification" in data
    v = data["verification"]
    assert "truth_status" in v
    assert "truth_and_integrity" in v
    assert "privacy_shield" in v


def test_api_forward_check_endpoint():
    response = client.post(
        "/api/forward-check",
        json={"text": "Forwarded message: Your account will be frozen today. Contact support."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["mode"] == "Forward Checker"
    assert "verification" in data


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
    assert "verification" in data


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
    assert "verification" in data