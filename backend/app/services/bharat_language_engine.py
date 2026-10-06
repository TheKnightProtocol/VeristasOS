"""
VeristasOS Bharat Language Safety Engine

Detects code-mixed Indian digital communication (Hinglish/English), classifies intent,
and provides contextual Indian safety advice.
"""

from __future__ import annotations

import re
from typing import Any


HINGLISH_KEYWORDS = [
    "bhai", "ye", "yeh", "wala", "kya", "link", "mat", "karna", "karo", "hoga",
    "kisi", "par", "hai", "hu", "mera", "meri", "sir", "send", "karo"
]


def analyze_bharat_language(text: str) -> dict[str, Any]:
    """
    Detect code-mixed Hinglish vs. English, classify intent, and format safety guidance.
    """
    if not text or not isinstance(text, str):
        return {
            "language": "English",
            "is_code_mixed": False,
            "intent": "General Query",
            "safety_advice_hinglish": "",
            "safety_advice_english": "Verify untrusted links before entering sensitive details.",
        }

    words = [w.lower() for w in re.findall(r"\b\w+\b", text)]
    hinglish_count = sum(1 for w in words if w in HINGLISH_KEYWORDS)

    is_hinglish = (hinglish_count >= 1)
    language = "Hinglish (Code-Mixed)" if is_hinglish else "English"

    clean = text.lower()
    intent = "General Verification"
    if "kyc" in clean:
        intent = "KYC Verification Query"
    elif "link" in clean or "http" in clean or "www." in clean:
        intent = "Link Verification Query"
    elif "otp" in clean or "pin" in clean:
        intent = "OTP / Credential Safety Query"
    elif "bank" in clean or "account" in clean:
        intent = "Bank Security Query"

    # Contextual Advice Generation
    if "kyc" in clean or "blocked" in clean or "bank" in clean:
        advice_hinglish = "⚠️ Ye link suspicious lag raha hai. Kisi bhi anjaan link par bank details, OTP ya UPI PIN share mat karna. Bank branch ya official app se verify karo."
        advice_english = "⚠️ High Phishing Risk: Do not enter OTP or UPI PIN on unverified web links. Confirm status directly in your official banking application."
    elif "lottery" in clean or "prize" in clean or "winner" in clean:
        advice_hinglish = "⚠️ Ye fake lottery scam ho sakta hai. Kisi ko bhi claim fee ya UPI se payment mat bhejo."
        advice_english = "⚠️ Lottery Bait Warning: Genuine organizations never demand advance fees or UPI payments to claim prizes."
    else:
        advice_hinglish = "ℹ️ Content suspicious lag sakta hai. Official source se cross-check karein."
        advice_english = "ℹ️ Content requires verification against official authoritative sources."

    return {
        "language": language,
        "is_code_mixed": is_hinglish,
        "intent": intent,
        "safety_advice_hinglish": advice_hinglish,
        "safety_advice_english": advice_english,
    }
