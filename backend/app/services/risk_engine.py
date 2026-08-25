"""
VeristasOS Risk Engine

Calculates transparent, objective risk indicators, risk factor breakdown,
flagged indicators with severity levels, and verification recommendations.

Distinguishes LINGUISTIC RISK from FACTUAL VERIFICATION.
"""

from __future__ import annotations

import re
from typing import Any


def calculate_risk(
    text_analysis: dict[str, Any],
    claims: list[dict[str, Any]],
    provenance: dict[str, Any],
    ai_analysis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Compute structured, transparent risk assessment for the input content.
    """
    sensationalism_score = float(text_analysis.get("sensationalism_score", 0.0))
    exclamation_count = int(text_analysis.get("exclamation_count", 0))
    question_count = int(text_analysis.get("question_count", 0))
    uppercase_count = int(text_analysis.get("uppercase_word_count", 0))
    repeated_ratio = float(text_analysis.get("repeated_word_ratio", 0.0))
    sensational_words = text_analysis.get("sensational_words", [])
    word_count = int(text_analysis.get("word_count", 0))

    # 1. Linguistic Risk Signal
    linguistic_risk = min(100.0, sensationalism_score * 0.95 + (exclamation_count * 4.0))

    # 2. Emotional Language Signal
    emotional_language = min(
        100.0,
        (len(sensational_words) * 12.0) + (exclamation_count * 8.0) + (uppercase_count * 5.0),
    )

    # 3. Repetition Signal
    repetition = min(100.0, repeated_ratio * 350.0)

    # 4. Excessive Certainty Signal (Detection of absolute words like "100%", "definitely", "always", "never", "guaranteed", "secret")
    certainty_matches = len(
        re.findall(
            r"\b(definitely|absolutely|100%|guaranteed|proven|undeniable|always|never|secret|undoubted)\b",
            text_analysis.get("text", "") if "text" in text_analysis else "",
            re.IGNORECASE,
        )
    )
    excessive_certainty = min(100.0, (certainty_matches * 25.0) + (uppercase_count * 4.0))

    # 5. Source Risk Signal
    provenance_score = float(provenance.get("provenance_score", 0))
    if not provenance.get("source_available", False):
        source_risk = 65.0  # High default risk when no source provided
    else:
        source_risk = max(0.0, 100.0 - provenance_score)

    # 6. Claim Density Signal
    claim_count = len(claims)
    claim_density = min(100.0, (claim_count / max(1, (word_count / 30.0))) * 50.0) if word_count else 0.0

    # Overall Risk Score Weighted Calculation
    overall_risk_score = round(
        (sensationalism_score * 0.30)
        + (emotional_language * 0.20)
        + (source_risk * 0.25)
        + (excessive_certainty * 0.15)
        + (repetition * 0.10),
        1,
    )

    # Classifications
    if overall_risk_score <= 25.0:
        classification = "LOW RISK"
    elif overall_risk_score <= 55.0:
        classification = "MODERATE RISK"
    elif overall_risk_score <= 80.0:
        classification = "HIGH RISK"
    else:
        classification = "VERY HIGH RISK"

    # Confidence calculation based on text length and data availability
    base_confidence = 65.0
    if word_count > 40:
        base_confidence += 15.0
    if word_count > 150:
        base_confidence += 10.0
    if provenance.get("source_available", False):
        base_confidence += 10.0

    if ai_analysis and ai_analysis.get("available", False):
        ai_conf = ai_analysis.get("confidence", 0)
        if ai_conf > 0:
            confidence = round((base_confidence * 0.5) + (ai_conf * 0.5), 1)
        else:
            confidence = min(98.0, base_confidence)
    else:
        confidence = min(92.0, base_confidence)

    # Risk Factor Breakdown Object
    risk_factors = {
        "linguistic_risk": round(linguistic_risk, 1),
        "emotional_language": round(emotional_language, 1),
        "sensationalism": round(sensationalism_score, 1),
        "repetition": round(repetition, 1),
        "excessive_certainty": round(excessive_certainty, 1),
        "source_risk": round(source_risk, 1),
        "claim_density": round(claim_density, 1),
    }

    # Top Flagged Indicators ("Why did VeristasOS flag this?")
    indicators = []

    if sensationalism_score >= 40:
        indicators.append(
            {
                "indicator": "Excessive sensational language",
                "severity": "HIGH" if sensationalism_score >= 65 else "MEDIUM",
                "reason": f"Detected sensational words ({', '.join(sensational_words[:4]) or 'high emphasis'}).",
            }
        )

    if exclamation_count > 1 or uppercase_count > 2:
        indicators.append(
            {
                "indicator": "High emotional punctuation & ALL CAPS",
                "severity": "HIGH" if exclamation_count >= 3 else "MEDIUM",
                "reason": f"Contains {exclamation_count} exclamation marks and {uppercase_count} uppercase words.",
            }
        )

    if not provenance.get("source_available", False):
        indicators.append(
            {
                "indicator": "Unspecified source origin",
                "severity": "MEDIUM",
                "reason": "No publisher, URL, or author metadata was provided with this submission.",
            }
        )

    if repetition >= 30:
        indicators.append(
            {
                "indicator": "Elevated linguistic repetition",
                "severity": "LOW" if repetition < 50 else "MEDIUM",
                "reason": "Frequent repetition of key terms may indicate circular emphasis.",
            }
        )

    if excessive_certainty >= 40:
        indicators.append(
            {
                "indicator": "Unsupported absolute certainty",
                "severity": "MEDIUM",
                "reason": "Uses absolute framing language without presenting backing evidence.",
            }
        )

    if not indicators:
        indicators.append(
            {
                "indicator": "Standard linguistic structure",
                "severity": "LOW",
                "reason": "No aggressive sensationalism or emotional manipulation signals detected.",
            }
        )

    # Recommendations
    recommendations = [
        "Cross-verify claims with reputable primary reporting outlets.",
        "Check publication date and author background credentials.",
        "Verify quoted statistics against original peer-reviewed or official sources.",
        "Compare sensational headlines against the factual body text.",
        "Distinguish between opinion commentary and verified factual reporting.",
    ]

    return {
        "overall_risk_score": overall_risk_score,
        "classification": classification,
        "confidence": confidence,
        "risk_factors": risk_factors,
        "indicators": indicators[:5],
        "recommendations": recommendations,
        "disclaimer": (
            "VeristasOS provides AI-assisted risk indicators and analytical signals. "
            "It does not independently establish whether a claim is true or false. "
            "Users should verify important claims using reliable primary sources."
        ),
    }
