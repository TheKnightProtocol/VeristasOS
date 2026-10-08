"""
VeristasOS — Digital Trust Engine
Analyzes messages, requests, and tool actions for urgency, financial intent,
PII leaks, OTP exposure, KYC scams, malicious links, and risk levels.
"""

from typing import Any, Dict, List
from app.services.privacy_scanner import scan_privacy_signals
from app.services.scam_detector import analyze_scam_signals
from app.services.bharat_language_engine import analyze_bharat_language
from app.services.scam_dna import generate_scam_dna


class DigitalTrustEngine:
    """Evaluates request risk level (LOW, MEDIUM, HIGH) and intent signals."""

    def evaluate_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run multi-signal trust evaluation over user message or action."""
        if not message or not message.strip():
            return {
                "risk_level": "LOW",
                "risk_score": 0,
                "intent": "GENERAL_ASSISTANCE",
                "signals": [],
                "reasons": ["Empty message provided."],
            }

        text = message.strip()
        text_lower = text.lower()
        signals: List[str] = []
        reasons: List[str] = []
        risk_score = 10

        # 1. Privacy & PII Scanner (Aadhaar, PAN, UPI ID, OTP, Password)
        privacy_res = scan_privacy_signals(text)
        detected_types = privacy_res.get("detected_types", [])

        if any("OTP" in t for t in detected_types) or any(w in text_lower for w in ["otp", "one time password", "verification code"]):
            signals.append("OTP_EXPOSURE")
            reasons.append("Contains sensitive One-Time Password (OTP) or authentication code.")
            risk_score += 50

        if any("Aadhaar" in t or "PAN" in t for t in detected_types):
            signals.append("NATIONAL_ID_EXPOSURE")
            reasons.append("Contains government identity numbers (Aadhaar/PAN).")
            risk_score += 40

        if any("UPI" in t for t in detected_types) or "upi" in text_lower:
            signals.append("UPI_ID_PRESENT")
            reasons.append("Contains virtual payment address or UPI request.")
            risk_score += 30

        # Passwords / Bank PIN keywords
        if any(w in text_lower for w in ["password", "passcode", "pin", "netbanking password", "cvv"]):
            signals.append("CREDENTIAL_EXPOSURE")
            reasons.append("Mentions banking PIN, CVV, or password credentials.")
            risk_score += 45

        # 2. Scam Detector & Attack Vector Analysis
        scam_res = analyze_scam_signals(text)
        attack_vector = scam_res.get("top_attack_vector", "GENERIC")
        if scam_res.get("scam_score", 0) > 40 or attack_vector != "GENERIC":
            signals.append(f"SCAM_VECTOR_{attack_vector}")
            reasons.append(f"Matches {attack_vector} scam threat patterns.")
            risk_score += scam_res.get("scam_score", 30)

        # 3. Bharat Language Coercion & Urgency Engine
        bharat_res = analyze_bharat_language(text)
        if bharat_res.get("urgency_detected"):
            signals.append("URGENCY_PRESSURE")
            reasons.append("High-pressure urgency phrasing detected ('immediately', 'today', 'suspended').")
            risk_score += 25

        if bharat_res.get("coercion_detected"):
            signals.append("COERCION_THREAT")
            reasons.append("Coercive psychological pressure detected.")
            risk_score += 30

        # 4. Financial Action Intent (Money transfer, pay, send UPI, withdraw)
        financial_keywords = ["transfer money", "send money", "pay rs", "pay rupees", "upi pin", "deposit", "withdraw"]
        if any(k in text_lower for k in financial_keywords):
            signals.append("FINANCIAL_ACTION_REQUEST")
            reasons.append("Contains explicit financial transfer or payment request.")
            risk_score += 35

        # 5. External Link Detection
        if "http://" in text_lower or "https://" in text_lower or ".com/" in text_lower or "bit.ly" in text_lower:
            signals.append("EXTERNAL_LINK_PRESENT")
            reasons.append("Contains external URL / link.")
            risk_score += 20

        # 6. Intent Classification
        intent = self._classify_intent(signals, text_lower)

        # Normalize score and assign Risk Level
        risk_score = min(100, max(0, risk_score))
        if risk_score >= 60 or "OTP_EXPOSURE" in signals or "CREDENTIAL_EXPOSURE" in signals:
            risk_level = "HIGH"
        elif risk_score >= 30 or "FINANCIAL_ACTION_REQUEST" in signals or "EXTERNAL_LINK_PRESENT" in signals:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        if not reasons:
            reasons.append("Standard digital information evaluation.")

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "intent": intent,
            "signals": signals,
            "reasons": reasons,
            "scam_dna": generate_scam_dna(text),
        }

    def _classify_intent(self, signals: List[str], text_lower: str) -> str:
        """Classify primary message intent category."""
        if "OTP_EXPOSURE" in signals or "CREDENTIAL_EXPOSURE" in signals:
            return "CREDENTIAL_AUTHENTICATION"
        if "FINANCIAL_ACTION_REQUEST" in signals:
            return "FINANCIAL_TRANSACTION"
        if any("SCAM_VECTOR" in s for s in signals) or "URGENCY_PRESSURE" in signals:
            return "SCAM_VERIFICATION"
        if any(w in text_lower for w in ["send email", "email karo", "send message", "schedule"]):
            return "COMMUNICATION_ACTION"
        if any(w in text_lower for w in ["summarize", "summary", "explain", "what is", "translate"]):
            return "KNOWLEDGE_QUERY"
        return "GENERAL_ASSISTANCE"


trust_engine_instance = DigitalTrustEngine()
