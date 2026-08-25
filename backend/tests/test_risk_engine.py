import os
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.claim_analyzer import extract_claims
from app.services.provenance import analyze_provenance
from app.services.risk_engine import calculate_risk
from app.services.image_analyzer import analyze_image_bytes, analyze_text_image_consistency
from app.services.text_analyzer import analyze_text
from app.services.ai_analyzer import analyze_with_ai


def test_claim_extraction():
    text = "The government confirmed 500 new public transit vehicles were purchased in 2025. Scientists discovered a new energy efficient battery."
    claims = extract_claims(text)
    assert isinstance(claims, list)
    assert len(claims) >= 1
    assert claims[0]["verification_status"] == "unverified"
    assert claims[0]["type"] in ["factual", "declarative"]


def test_provenance_evaluation():
    prov = analyze_provenance(
        source_url="https://example-news.com/article",
        source_name="Example News",
        author="John Doe",
        publication_date="2026-01-15",
    )
    assert prov["source_available"] is True
    assert prov["provenance_score"] == 100
    assert prov["domain"] == "example-news.com"
    assert prov["status"] == "Source information provided"


def test_provenance_unspecified():
    prov = analyze_provenance()
    assert prov["source_available"] is False
    assert prov["provenance_score"] == 0
    assert prov["status"] == "Not provided"


def test_risk_calculation():
    text = "BREAKING! SHOCKING! Secret miracle cure confirmed by officials! YOU WON'T BELIEVE THIS!!!"
    linguistic = analyze_text(text)
    claims = extract_claims(text)
    prov = analyze_provenance()
    ai_res = {"available": False, "confidence": 0}

    risk = calculate_risk(linguistic, claims, prov, ai_res)
    assert 0 <= risk["overall_risk_score"] <= 100
    assert risk["classification"] in ["LOW RISK", "MODERATE RISK", "HIGH RISK", "VERY HIGH RISK"]
    assert len(risk["indicators"]) > 0
    assert len(risk["recommendations"]) > 0
    assert "disclaimer" in risk


def test_image_analyzer_bytes():
    fake_img = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0"
        b"\x00\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    result = analyze_image_bytes(fake_img, "sample.png")
    assert result["filename"] == "sample.png"
    assert result["width"] == 1
    assert result["height"] == 1
    assert len(result["sha256"]) == 64
    assert result["perceptual_hash"] != ""


def test_ai_analyzer_offline_fallback():
    text = "Simple test sentence."
    linguistic = analyze_text(text)
    res = analyze_with_ai(text, linguistic)
    assert "available" in res
    assert "verification_steps" in res
