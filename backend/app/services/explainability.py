"""
VeristasOS Explainability Service — Signal Impact Analysis (LIME/SHAP Inspired)

Maps deterministic & linguistic features to feature impact levels (HIGH, MEDIUM, LOW)
and human-understandable explanations for transparency.

Honest & signal-grounded (No hallucinated predictions).
"""

from __future__ import annotations

from typing import Any


def generate_explainability_matrix(
    text_analysis: dict[str, Any],
    privacy_analysis: dict[str, Any],
    scam_analysis: dict[str, Any],
    provenance_analysis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Construct feature impact matrix explaining WHY the model generated its risk assessment.
    """
    feature_impacts: list[dict[str, str]] = []

    # 1. Sensational Wording
    sensational_words = text_analysis.get("sensational_words", [])
    if sensational_words:
        impact = "HIGH" if len(sensational_words) >= 3 else "MEDIUM"
        feature_impacts.append({
            "feature": "Sensational Wording",
            "impact": impact,
            "reason": f"Detected {len(sensational_words)} trigger terms: {', '.join(sensational_words[:4])}."
        })

    # 2. Uppercase Word Density
    uppercase_count = text_analysis.get("uppercase_word_count", 0)
    if uppercase_count > 0:
        impact = "HIGH" if uppercase_count >= 3 else "MEDIUM"
        feature_impacts.append({
            "feature": "ALL-CAPS Emphasis",
            "impact": impact,
            "reason": f"Detected {uppercase_count} uppercase words emphasizing claims."
        })

    # 3. Punctuation Exclamations
    exclamation_count = text_analysis.get("exclamation_count", 0)
    if exclamation_count > 0:
        impact = "HIGH" if exclamation_count >= 3 else "LOW"
        feature_impacts.append({
            "feature": "Exclamation Density",
            "impact": impact,
            "reason": f"Contains {exclamation_count} exclamation marks creating artificial urgency."
        })

    # 4. Sensitive Data Exposure
    sensitive_count = privacy_analysis.get("sensitive_data_detected", 0)
    if sensitive_count > 0:
        feature_impacts.append({
            "feature": "Sensitive Information Exposure",
            "impact": "CRITICAL",
            "reason": f"Contains {sensitive_count} sensitive identifier patterns ({', '.join(privacy_analysis.get('detected_types', []))})."
        })

    # 5. Scam Radar Triggers
    triggers = scam_analysis.get("triggers_found", [])
    for t in triggers:
        feature_impacts.append({
            "feature": f"Scam Indicator ({t['trigger']})",
            "impact": "HIGH" if t["score_impact"] >= 25 else "MEDIUM",
            "reason": f"Pattern matched: {', '.join(t['matches'])}."
        })

    # 6. Source Provenance
    if provenance_analysis:
        prov_score = provenance_analysis.get("provenance_score", 50)
        if prov_score < 40:
            feature_impacts.append({
                "feature": "Unverified Publisher Provenance",
                "impact": "MEDIUM",
                "reason": "Publisher information missing or unverified domain."
            })

    if not feature_impacts:
        feature_impacts.append({
            "feature": "Standard Prose Structure",
            "impact": "LOW",
            "reason": "Linguistic features align with standard neutral writing patterns."
        })

    return {
        "explainability_type": "Signal Impact Analysis — Feature Grounded",
        "feature_impacts": feature_impacts,
        "summary": "AI explains its decision by highlighting specific linguistic, privacy, and coercion indicators.",
    }
