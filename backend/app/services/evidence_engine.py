"""
VeristasOS Evidence Retrieval & Evaluation Engine
"""

from __future__ import annotations

from typing import Any
from app.services.semantic_search import search_engine
from app.models.schemas import EvidenceMatch


def evaluate_claim_evidence(claim_text: str) -> dict[str, Any]:
    """
    Retrieve and evaluate semantically matched evidence for a given factual claim.
    """
    if not claim_text.strip():
        return {
            "claim": claim_text,
            "evidence": [],
            "support_score": 0.0,
            "contradiction_score": 0.0,
            "confidence": 0.0,
            "status": "INSUFFICIENT_EVIDENCE",
            "summary": "No text content provided for claim evaluation.",
        }

    matches: list[EvidenceMatch] = search_engine.search_similar_claims(claim_text, top_k=5)

    supporting = [m for m in matches if m.relationship == "SUPPORTING"]
    contradicting = [m for m in matches if m.relationship == "CONTRADICTING"]
    related = [m for m in matches if m.relationship in ("RELATED", "INSUFFICIENT")]

    support_score = max([m.similarity_score for m in supporting], default=0.0)
    contradiction_score = max([m.similarity_score for m in contradicting], default=0.0)

    if contradicting:
        status = "CONTRADICTED_BY_EVIDENCE"
        confidence = round(contradiction_score, 1)
        summary = "Indexed authoritative reporting directly disputes or contradicts key assertions in this claim."
    elif supporting and support_score >= 50:
        status = "CORROBORATED_BY_EVIDENCE"
        confidence = round(support_score, 1)
        summary = "Indexed authoritative evidence corroborates the core details of this claim."
    elif matches and max([m.similarity_score for m in matches], default=0.0) >= 20:
        status = "PARTIALLY_CORROBORATED"
        confidence = 50.0
        summary = "Related subject context was found, but full independent verification remains unconfirmed."
    else:
        status = "INSUFFICIENT_EVIDENCE"
        confidence = 30.0
        summary = "No direct matching evidence found in current evidence index. Further investigation required."

    return {
        "claim": claim_text,
        "evidence": [m.model_dump() if hasattr(m, "model_dump") else m.dict() for m in matches],
        "support_score": support_score,
        "contradiction_score": contradiction_score,
        "confidence": confidence,
        "status": status,
        "summary": summary,
        "counts": {
            "supporting": len(supporting),
            "contradicting": len(contradicting),
            "related": len(related),
        },
    }
