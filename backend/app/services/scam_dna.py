"""
VeristasOS Scam DNA Engine

Extracts a 5-dimensional feature fingerprint representing attack patterns:
1. Urgency Pressure %
2. Impersonation / Authority %
3. Financial Pressure %
4. Credential Request %
5. Suspicious URL / Link %
"""

from __future__ import annotations

import re
from typing import Any


def generate_scam_dna(text: str) -> dict[str, Any]:
    """
    Extract 5-dimensional Scam DNA metrics and classify attack pattern.
    """
    if not text or not isinstance(text, str):
        return {
            "urgency_score": 0,
            "impersonation_score": 0,
            "financial_pressure_score": 0,
            "credential_request_score": 0,
            "suspicious_url_score": 0,
            "primary_pattern": "Neutral",
            "fingerprint": "DNA-00-00-00-00-00",
        }

    clean = text.lower()

    # 1. Urgency Score
    urgency_keywords = ["urgent", "immediately", "today", "within 24 hours", "expired", "blocked today", "act now", "last chance"]
    urgency_matches = sum(1 for k in urgency_keywords if k in clean)
    urgency_score = min(100, urgency_matches * 30 + (25 if "!" in text else 0))

    # 2. Impersonation / Authority Score
    impersonation_keywords = ["bank", "kyc", "customer support", "official", "government", "sbi", "hdfc", "icici", "customs", "courier", "police"]
    impersonation_matches = sum(1 for k in impersonation_keywords if k in clean)
    impersonation_score = min(100, impersonation_matches * 35)

    # 3. Financial Pressure Score
    financial_keywords = ["payment", "fee", "penalty", "tax", "fine", "account frozen", "deactivated", "upi", "paytm"]
    financial_matches = sum(1 for k in financial_keywords if k in clean)
    financial_score = min(100, financial_matches * 30)

    # 4. Credential Request Score
    credential_keywords = ["otp", "pin", "aadhaar", "pan", "password", "cvv", "verify details", "enter details", "login"]
    credential_matches = sum(1 for k in credential_keywords if k in clean)
    credential_score = min(100, credential_matches * 35)

    # 5. Suspicious URL Score
    has_url = "http" in clean or "www." in clean or ".com" in clean or ".xyz" in clean or ".link" in clean or "bit.ly" in clean
    suspicious_url_score = 90 if has_url else 0

    # Classify Primary Pattern
    primary_pattern = "General Phishing Risk"
    if "kyc" in clean or "bank" in clean:
        primary_pattern = "KYC & Bank Impersonation Fraud"
    elif "lottery" in clean or "winner" in clean or "prize" in clean:
        primary_pattern = "Lottery & Prize Bait"
    elif "courier" in clean or "customs" in clean or "package" in clean:
        primary_pattern = "Courier & Customs Trap"
    elif credential_score > 60:
        primary_pattern = "Credential & OTP Harvesting"

    fingerprint = f"DNA-{urgency_score:02d}-{impersonation_score:02d}-{financial_score:02d}-{credential_score:02d}-{suspicious_url_score:02d}"

    return {
        "urgency_score": urgency_score,
        "impersonation_score": impersonation_score,
        "financial_pressure_score": financial_score,
        "credential_request_score": credential_score,
        "suspicious_url_score": suspicious_url_score,
        "primary_pattern": primary_pattern,
        "fingerprint": fingerprint,
    }
