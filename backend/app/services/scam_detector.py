"""
VeristasOS Scam Radar Service — Rule-Assisted Threat Detection

Evaluates content for financial scam patterns, KYC fraud threats, bank account suspension warnings,
unauthorized payment requests, and high-pressure urgency tactics.

Clearly labeled as 'Rule-assisted risk detection' (not absolute proof of fraud).
"""

from __future__ import annotations

import re
from typing import Any


SCAM_TRIGGERS = [
    (r"\b(?:kyc|know your customer)\b", "KYC Verification Request", 30),
    (r"\b(?:blocked|suspended|deactivated|frozen|terminated)\b", "Account Suspension Threat", 25),
    (r"\b(?:otp|one time password|pin|security code)\b", "Sensitive OTP / PIN Request", 35),
    (r"\b(?:upi|paytm|gpay|phonepe|bank account)\b", "Financial Credential / UPI Request", 20),
    (r"\b(?:immediately|urgent|today|within \d+ hours|act now)\b", "Urgency & Pressure Tactic", 20),
    (r"\b(?:lottery|winner|prize|congratulations|reward|\$\d+|\₹\d+)\b", "Lottery / Reward Bait", 30),
    (r"\b(?:loan approval|pre-approved|0% interest)\b", "Unsolicited Financial Offer", 20),
]


def detect_scam_signals(text: str) -> dict[str, Any]:
    """
    Analyze text for financial scam patterns, urgency coercion, and credential theft triggers.
    """
    if not text or not isinstance(text, str):
        return {
            "scam_risk": "LOW",
            "scam_score": 0,
            "triggers_found": [],
            "explanation": "No scam or coercion indicators detected.",
            "detector_type": "Scam Radar — Rule-Assisted Detection",
        }

    scam_score = 0
    triggers_found: list[dict[str, Any]] = []

    for pattern, name, points in SCAM_TRIGGERS:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        if matches:
            scam_score += points
            triggers_found.append({
                "trigger": name,
                "score_impact": points,
                "matches": list(set(matches))[:3]
            })

    scam_score = max(0, min(100, scam_score))

    if scam_score >= 70:
        risk = "HIGH RISK"
        explanation = "HIGH SCAM THREAT: High-pressure urgency combined with sensitive credential/KYC requests."
    elif scam_score >= 40:
        risk = "MODERATE RISK"
        explanation = "ELEVATED RISK: Financial or account action request detected. Verify through official bank/organization channels."
    else:
        risk = "LOW RISK"
        explanation = "LOW THREAT: No strong coercion or phishing triggers identified."

    return {
        "scam_risk": risk,
        "scam_score": scam_score,
        "triggers_found": triggers_found,
        "explanation": explanation,
        "detector_type": "Scam Radar — Rule-Assisted Detection",
    }
