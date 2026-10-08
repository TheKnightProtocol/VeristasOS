"""
VeristasOS — Permission Engine
Manages policy permissions for AI Saathi actions:
- AUTO_ALLOWED: Q&A, explain, summarize, translate, scam analysis, URL analysis, draft generation
- ASK_USER: send email, send message, schedule appointment, external communication
- BLOCK: financial transfers, UPI PIN, OTP submission, password submission, Aadhaar/PAN submission
"""

from typing import Any, Dict, List, Optional
from app.services.policy_engine import UserPolicyEngine


class PermissionEngine:
    """Policy engine dictating action authorization state."""

    # Explicit policy mappings
    AUTO_ALLOWED_INTENTS = {
        "KNOWLEDGE_QUERY",
        "SCAM_VERIFICATION",
        "GENERAL_ASSISTANCE",
        "SUMMARIZE",
        "TRANSLATE",
        "EXPLAIN",
        "CLASSIFY",
        "ANALYZE_URL",
        "DRAFT_GENERATION",
    }

    ASK_USER_INTENTS = {
        "COMMUNICATION_ACTION",
        "SEND_EMAIL",
        "SEND_MESSAGE",
        "SCHEDULE_APPOINTMENT",
        "CREATE_CALENDAR_EVENT",
        "EXTERNAL_COMMUNICATION",
    }

    BLOCKED_INTENTS = {
        "FINANCIAL_TRANSACTION",
        "CREDENTIAL_AUTHENTICATION",
        "PAYMENT",
        "UPI_PIN_SUBMISSION",
        "OTP_SUBMISSION",
        "PASSWORD_SUBMISSION",
        "AADHAAR_PAN_SUBMISSION",
        "BANKING_CREDENTIALS",
    }

    def __init__(self, mode: str = "Adult"):
        self.mode = mode
        self.policy_delegate = UserPolicyEngine(mode=mode)

    def set_mode(self, mode: str):
        self.mode = mode
        self.policy_delegate.set_mode(mode)

    def evaluate_permission(
        self,
        intent: str,
        risk_level: str,
        signals: List[str] = None,
        tool_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate permission for intent / tool_name.
        Returns action gate: AUTO_ACT | RESPOND | ASK_CONFIRMATION | BLOCK
        """
        signals = signals or []

        # 1. High risk or blocked intent / signals -> BLOCK
        if (
            intent in self.BLOCKED_INTENTS
            or risk_level == "HIGH"
            or any(s in signals for s in ["OTP_EXPOSURE", "CREDENTIAL_EXPOSURE", "FINANCIAL_ACTION_REQUEST"])
        ):
            return {
                "action": "BLOCK",
                "requires_confirmation": False,
                "reason": "Execution blocked automatically to protect financial & credential security.",
                "user_mode": self.mode,
            }

        # 2. Medium risk or ASK USER intents -> ASK_CONFIRMATION
        if intent in self.ASK_USER_INTENTS or risk_level == "MEDIUM":
            return {
                "action": "ASK_CONFIRMATION",
                "requires_confirmation": True,
                "reason": "External digital communication action requires explicit user confirmation.",
                "user_mode": self.mode,
            }

        # 3. Low risk & AUTO-ALLOWED intents -> AUTO_ACT / RESPOND
        if intent in self.AUTO_ALLOWED_INTENTS or risk_level == "LOW":
            return {
                "action": "AUTO_ACT" if tool_name else "RESPOND",
                "requires_confirmation": False,
                "reason": "Routine low-risk knowledge or safety request allowed by policy.",
                "user_mode": self.mode,
            }

        # Default fallback
        return {
            "action": "ASK_CONFIRMATION",
            "requires_confirmation": True,
            "reason": "Unrecognized action requires user confirmation.",
            "user_mode": self.mode,
        }


permission_engine_instance = PermissionEngine()
