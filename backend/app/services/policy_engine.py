"""
User Policy / Permission Engine for VeristasOS — Your AI Saathi.
Manages user permission tiers:
- LOW-RISK: Auto-executable (summarize, categorize, spam filter, create reminder)
- MEDIUM-RISK: Requires user confirmation by default (draft reply, schedule meeting)
- HIGH-RISK: Strictly BLOCKED for autonomous execution in prototype (financial transactions, UPI, OTP, PAN/Aadhaar)
Supports Adult Mode and Senior Mode.
"""

from typing import Dict, Any, List


class UserPolicyEngine:
    # Categories definition
    LOW_RISK_ACTIONS = {
        "summarize_email",
        "categorize_email",
        "filter_spam",
        "create_reminder",
        "organize_notifications",
        "summarize_document"
    }

    MEDIUM_RISK_ACTIONS = {
        "draft_email_reply",
        "schedule_meeting",
        "send_routine_message",
        "archive_email"
    }

    HIGH_RISK_ACTIONS = {
        "financial_transaction",
        "upi_payment",
        "share_otp",
        "share_password",
        "share_aadhaar",
        "share_pan",
        "bank_credentials",
        "send_sensitive_document",
        "change_security_settings",
        "delete_important_data"
    }

    def __init__(self, mode: str = "Adult"):
        self.mode = mode  # "Adult" or "Senior"
        self.user_custom_allow_medium: bool = False

    def set_mode(self, mode: str):
        if mode in ["Adult", "Senior"]:
            self.mode = mode

    def evaluate_action_permission(
        self,
        action_name: str,
        risk_level: str,
        signals: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Evaluates whether a proposed AI action can auto-execute, requires user approval,
        or must be strictly blocked.
        """
        signals = signals or {}
        
        # Check for explicit high risk triggers (OTP, UPI, Aadhaar, PAN requests)
        has_high_risk_signal = (
            signals.get("privacy_leak_detected", False) or
            signals.get("scam_dna", {}).get("threat_detected", False) or
            action_name in self.HIGH_RISK_ACTIONS or
            risk_level in ["HIGH", "CRITICAL"]
        )

        if has_high_risk_signal or action_name in self.HIGH_RISK_ACTIONS:
            permission = "BLOCKED"
            category = "HIGH_RISK"
            execution_mode = "NEVER_AUTO"
            reason = "Financial, identity, or credential safety risk detected. Autonomous execution is strictly forbidden."
        elif action_name in self.LOW_RISK_ACTIONS and risk_level == "LOW":
            permission = "ALLOWED"
            category = "LOW_RISK"
            execution_mode = "AUTO_ACT"
            reason = "Routine low-risk digital assistant task allowed by policy."
        elif action_name in self.MEDIUM_RISK_ACTIONS or risk_level == "CAUTION":
            if self.user_custom_allow_medium and self.mode == "Adult":
                permission = "ALLOWED"
                category = "MEDIUM_RISK"
                execution_mode = "AUTO_ACT_USER_OVERRIDE"
                reason = "Medium-risk action auto-executed per custom user policy preference."
            else:
                permission = "REQUIRES_USER_APPROVAL"
                category = "MEDIUM_RISK"
                execution_mode = "ASK_USER"
                reason = "Action has digital footprint implications. User confirmation required."
        else:
            # Default fallback for unknown actions
            permission = "REQUIRES_USER_APPROVAL"
            category = "MEDIUM_RISK"
            execution_mode = "ASK_USER"
            reason = "Unrecognized action category requires user verification."

        # Senior Mode Enhancements
        senior_notice = None
        if self.mode == "Senior":
            if permission == "BLOCKED":
                senior_notice = "🔴 YE MESSAGE DANGEROUS HO SAKTA HAI. Bank details ya OTP mat share kijiye. Family member ko dikhayen."
            elif permission == "REQUIRES_USER_APPROVAL":
                senior_notice = "🟡 Kripya isey confirm karein aage badhne se pehle."

        return {
            "action_name": action_name,
            "permission": permission,
            "category": category,
            "execution_mode": execution_mode,
            "user_mode": self.mode,
            "reason": reason,
            "senior_notice": senior_notice
        }
