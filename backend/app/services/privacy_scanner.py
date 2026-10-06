"""
VeristasOS Privacy Shield Service — India-First Privacy Scanner

Detects and masks sensitive personal and financial identifiers (Aadhaar, PAN, UPI IDs,
OTPs, Indian phone numbers, emails) to protect user data before external transmission.
Computes a prototype Privacy Grade (A/B/C/D/F).

DO NOT store sensitive data.
"""

from __future__ import annotations

import re
from typing import Any


# REGEX PATTERNS FOR SENSITIVE IDENTIFIERS
PATTERNS = {
    "Aadhaar Number": r"\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b",
    "PAN Card": r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
    "UPI ID": r"\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b",
    "OTP / Security PIN": r"\b(?:OTP|otp|code|pin|PIN)\D*(\d{4,8})\b",
    "Indian Mobile Number": r"\b(?:\+91[\-\s]?)?[6-9]\d{9}\b",
    "Email Address": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b",
}


def scan_privacy_signals(text: str) -> dict[str, Any]:
    """
    Scan text for sensitive Indian identifiers, calculate privacy risk score,
    and generate a masked version of the text.
    """
    if not text or not isinstance(text, str):
        return {
            "privacy_risk": "LOW",
            "privacy_grade": "A",
            "sensitive_data_detected": 0,
            "detected_types": [],
            "masked_text": "",
            "explanation": "No sensitive data detected.",
            "assessment_type": "Privacy Shield Scanner — India-First Protection",
        }

    detected_items: list[dict[str, str]] = []
    masked_text = text

    # Scan Aadhaar
    aadhaar_matches = re.findall(PATTERNS["Aadhaar Number"], text)
    for m in aadhaar_matches:
        digits = re.sub(r"\D", "", m)
        if len(digits) == 12:
            masked = f"XXXX XXXX {digits[-4:]}"
            masked_text = masked_text.replace(m, masked)
            detected_items.append({"type": "Aadhaar Number", "masked": masked})

    # Scan PAN Card
    pan_matches = re.findall(PATTERNS["PAN Card"], text)
    for m in pan_matches:
        masked = f"XXXXX{m[5:9]}X"
        masked_text = masked_text.replace(m, masked)
        detected_items.append({"type": "PAN Card", "masked": masked})

    # Scan UPI ID
    upi_matches = re.findall(PATTERNS["UPI ID"], text)
    for m in upi_matches:
        parts = m.split("@")
        masked = f"{parts[0][0]}***@{parts[1]}"
        masked_text = masked_text.replace(m, masked)
        detected_items.append({"type": "UPI ID", "masked": masked})

    # Scan OTP
    otp_matches = re.findall(PATTERNS["OTP / Security PIN"], text)
    for m in otp_matches:
        if isinstance(m, tuple):
            m = m[0]
        masked = "****"
        masked_text = masked_text.replace(m, masked)
        detected_items.append({"type": "OTP / Security PIN", "masked": masked})

    # Scan Indian Mobile Number
    phone_matches = re.findall(PATTERNS["Indian Mobile Number"], text)
    for m in phone_matches:
        digits = re.sub(r"\D", "", m)
        if len(digits) >= 10:
            masked = f"+91 {digits[-10:-7]}XXX XXX"
            masked_text = masked_text.replace(m, masked)
            detected_items.append({"type": "Indian Mobile Number", "masked": masked})

    count = len(detected_items)
    unique_types = sorted(list({item["type"] for item in detected_items}))

    # Privacy Grade Computation
    if count == 0:
        grade = "A"
        risk = "LOW"
        explanation = "Clean. No sensitive personal or financial identifiers were detected in the content."
    elif count == 1:
        grade = "B"
        risk = "MODERATE"
        explanation = f"Caution. Detected 1 sensitive identifier ({', '.join(unique_types)}). Verify recipient before sharing."
    elif count <= 3:
        grade = "C"
        risk = "HIGH"
        explanation = f"High Risk. Detected {count} sensitive identifiers ({', '.join(unique_types)}). Do not post or share publicly."
    else:
        grade = "F"
        risk = "CRITICAL"
        explanation = f"Critical Privacy Risk. Multiple sensitive credentials ({count}) exposed. Avoid transmitting over untrusted networks."

    return {
        "privacy_risk": risk,
        "privacy_grade": grade,
        "sensitive_data_detected": count,
        "detected_types": unique_types,
        "detected_items": detected_items,
        "masked_text": masked_text,
        "explanation": explanation,
        "assessment_type": "Privacy Shield Scanner — India-First Protection",
    }
