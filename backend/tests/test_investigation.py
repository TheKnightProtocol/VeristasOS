"""
VeristasOS Automated Test Suite for Investigation Subsystem
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.services.semantic_search import search_engine
from app.services.evidence_engine import evaluate_claim_evidence
from app.services.source_intelligence import evaluate_source_intelligence
from app.services.reverse_search import search_image_perceptual
from app.services.correlation_engine import correlate_cross_source_signals

client = TestClient(app)


def test_semantic_search_engine():
    matches = search_engine.search_similar_claims("public transit budget increase", top_k=3)
    assert isinstance(matches, list)
    assert len(matches) > 0
    assert matches[0].evidence.id == "EV-101"
    assert matches[0].similarity_score > 0.0


def test_semantic_search_compute_similarity():
    sim = search_engine.compute_similarity("cancer cure protocol", "cancer treatment clinical trial")
    assert isinstance(sim, float)
    assert 0.0 <= sim <= 100.0


def test_evidence_retrieval_engine():
    res = evaluate_claim_evidence("Municipal council approved a 4.2 percent budget increase for public transit.")
    assert "status" in res
    assert "support_score" in res
    assert res["status"] in ("CORROBORATED_BY_EVIDENCE", "PARTIALLY_CORROBORATED", "INSUFFICIENT_EVIDENCE")


def test_source_intelligence_evaluator():
    intel = evaluate_source_intelligence(
        source_url="https://cityjournal.org/article",
        source_name="City Journal",
        author="Jane Doe",
        publication_date="2026-02-10",
        article_text="According to officials, the study published new transit data.",
    )
    assert intel["provenance_score"] > 50.0
    assert "metrics" in intel
    assert intel["metrics"]["https_security"] == 100.0


def test_reverse_search_dhash_matching():
    res = search_image_perceptual("hash123", "a1b2c3d4e5f60718")
    assert "search_provider" in res
    assert "matches_found" in res
    assert res["matches_found"] >= 1


def test_cross_source_correlation():
    res = correlate_cross_source_signals(
        claims=[{"claim": "Sample claim"}],
        evidence_matches=[{"relationship": "SUPPORTING"}],
        source_intel={"provenance_score": 85.0},
    )
    assert "consensus_status" in res
    assert res["consensus_score"] > 0.0


def test_api_investigate_endpoint():
    response = client.post(
        "/api/investigate",
        json={
            "text": "The city municipal council approved a budget increase of 4.2 percent for public transit.",
            "source_url": "https://cityjournal.org/transit",
            "source_name": "City Journal",
            "author": "Jane Doe",
            "publication_date": "2026-02-10",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "investigation" in data
    inv = data["investigation"]
    assert "claims" in inv
    assert "source_intelligence" in inv
    assert "correlation" in inv
    assert "graph" in inv


def test_api_semantic_search_endpoint():
    response = client.post(
        "/api/semantic-search",
        json={"query": "transit budget", "top_k": 2},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["results_count"] >= 1


def test_api_evidence_index_endpoint():
    response = client.get("/api/evidence")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "evidence" in data
    assert len(data["evidence"]) >= 1


def test_api_investigation_graph_endpoint():
    response = client.get("/api/investigation/INV-TEST01/graph")
    assert response.status_code == 200
    data = response.json()
    assert "graph" in data
    assert "nodes" in data["graph"]
    assert "edges" in data["graph"]
