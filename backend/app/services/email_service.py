"""
Email Service Abstraction Layer for VeristasOS — Your AI Saathi.
Manages mock email inbox, runs Trust Firewall evaluations for incoming emails,
and executes allowed/approved actions.
"""

import json
import os
from typing import Dict, Any, List
from .trust_firewall import TrustFirewall


class EmailService:
    def __init__(self, data_path: str = None, user_mode: str = "Adult"):
        if data_path is None:
            curr = os.path.dirname(os.path.abspath(__file__))
            for _ in range(4):
                candidate = os.path.join(curr, "data", "demo_emails.json")
                if os.path.exists(candidate):
                    data_path = candidate
                    break
                curr = os.path.dirname(curr)
            if not data_path:
                data_path = os.path.join(os.getcwd(), "data", "demo_emails.json")
        self.data_path = data_path
        self.firewall = TrustFirewall(user_mode=user_mode)
        self.emails = self._load_emails()


    def set_user_mode(self, mode: str):
        self.firewall.set_user_mode(mode)

    def _load_emails(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def get_inbox(self) -> List[Dict[str, Any]]:
        """
        Returns all inbox items with updated Trust Firewall risk evaluations.
        """
        processed_emails = []
        for email in self.emails:
            content_to_eval = f"Subject: {email.get('subject')}\nFrom: {email.get('sender_name')} ({email.get('sender')})\nBody: {email.get('body')}"
            action_name = email.get("proposed_action", "summarize_email")
            
            firewall_res = self.firewall.evaluate_proposed_action(
                action_name=action_name,
                content=content_to_eval
            )
            
            processed_item = dict(email)
            processed_item["firewall_evaluation"] = firewall_res
            processed_item["computed_decision"] = firewall_res.get("decision")
            processed_item["computed_risk"] = firewall_res.get("risk_level")
            processed_emails.append(processed_item)
            
        return processed_emails

    def get_email_by_id(self, email_id: str) -> Dict[str, Any]:
        for item in self.get_inbox():
            if item.get("id") == email_id:
                return item
        return {}

    def execute_email_action(self, email_id: str, user_approved: bool = False) -> Dict[str, Any]:
        """
        Executes a proposed email action subject to Trust Firewall decision gate.
        """
        email = self.get_email_by_id(email_id)
        if not email:
            return {"status": "ERROR", "message": "Email not found"}

        eval_res = email.get("firewall_evaluation", {})
        decision = eval_res.get("decision")
        action_name = email.get("proposed_action")

        if decision == "BLOCK":
            return {
                "status": "BLOCKED",
                "message": f"Action '{action_name}' is BLOCKED by Trust Firewall.",
                "reason": eval_res.get("decision_reason"),
                "why": eval_res.get("why"),
                "recommended_action": eval_res.get("recommended_action")
            }
        elif decision == "ASK_USER" and not user_approved:
            return {
                "status": "REQUIRES_APPROVAL",
                "message": f"Action '{action_name}' requires explicit user confirmation.",
                "reason": eval_res.get("decision_reason"),
                "recommended_action": eval_res.get("recommended_action")
            }
        else:
            return {
                "status": "SUCCESS",
                "message": f"Action '{action_name}' executed successfully for email '{email.get('subject')}'.",
                "action_type": action_name,
                "execution_mode": "AUTO_ACT" if decision == "ALLOW" else "USER_APPROVED"
            }
