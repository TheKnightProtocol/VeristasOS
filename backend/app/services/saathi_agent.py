"""
AI Saathi Agent Conversational Engine for VeristasOS — Your AI Saathi.
Processes natural language user requests:
- "Check my emails." / "Check inbox"
- "Anything important today?"
- "Is this message safe?"
- "What should I do?"
- "Why did you block this?"
Generates Daily Saathi Brief (🔴 Actions Needed, 🟡 Reviews, 🟢 Handled).
"""

from typing import Dict, Any, List
from .trust_firewall import TrustFirewall
from .email_service import EmailService


class AISaathiAgent:
    def __init__(self, user_mode: str = "Adult"):
        self.user_mode = user_mode
        self.firewall = TrustFirewall(user_mode=user_mode)
        self.email_service = EmailService(user_mode=user_mode)

    def set_user_mode(self, mode: str):
        self.user_mode = mode
        self.firewall.set_user_mode(mode)
        self.email_service.set_user_mode(mode)

    def get_daily_brief(self) -> Dict[str, Any]:
        """
        Generates Daily Saathi Brief dashboard statistics and summary buckets.
        """
        inbox = self.email_service.get_inbox()
        
        red_actions: List[Dict[str, Any]] = []
        yellow_reviews: List[Dict[str, Any]] = []
        green_handled: List[Dict[str, Any]] = []

        for item in inbox:
            decision = item.get("computed_decision")
            risk = item.get("computed_risk")
            
            if decision == "BLOCK" or risk in ["HIGH", "CRITICAL"]:
                red_actions.append({
                    "id": item.get("id"),
                    "title": item.get("subject"),
                    "sender": item.get("sender_name"),
                    "reason": item.get("firewall_evaluation", {}).get("decision_reason"),
                    "recommended_action": item.get("firewall_evaluation", {}).get("recommended_action")
                })
            elif decision == "ASK_USER" or risk == "CAUTION":
                yellow_reviews.append({
                    "id": item.get("id"),
                    "title": item.get("subject"),
                    "sender": item.get("sender_name"),
                    "reason": "Requires user confirmation before processing."
                })
            else:
                green_handled.append({
                    "id": item.get("id"),
                    "title": item.get("subject"),
                    "sender": item.get("sender_name"),
                    "action_taken": "Summarized & safe reminder set"
                })

        return {
            "greeting": "Good afternoon 👋",
            "tagline": "Your AI Saathi — Protect. Understand. Act.",
            "digital_safety_score": 87,
            "actions_needed_count": len(red_actions),
            "reviews_needed_count": len(yellow_reviews),
            "handled_count": len(green_handled),
            "red_actions": red_actions,
            "yellow_reviews": yellow_reviews,
            "green_handled": green_handled,
            "user_mode": self.user_mode
        }

    def process_chat_query(self, query: str, context_content: str = "") -> Dict[str, Any]:
        """
        Parses natural language query and returns clear, conversational assistance.
        """
        query_lower = query.lower().strip() if query else ""
        
        # 1. "Check inbox" / "Check my emails"
        if "email" in query_lower or "inbox" in query_lower:
            brief = self.get_daily_brief()
            response_text = (
                f"Aapke inbox me total {brief['actions_needed_count'] + brief['reviews_needed_count'] + brief['handled_count']} messages hain:\n"
                f"🔴 {brief['actions_needed_count']} High Risk (Blocked/Action Needed)\n"
                f"🟡 {brief['reviews_needed_count']} Items to Review\n"
                f"🟢 {brief['handled_count']} Handled Automatically."
            )
            return {
                "query": query,
                "intent": "CHECK_INBOX",
                "response": response_text,
                "brief": brief,
                "quick_actions": ["Review High Risk Items", "Show Handled Emails"]
            }

        # 2. "What's important today?" / "Anything important today?"
        if "important" in query_lower or "today" in query_lower:
            brief = self.get_daily_brief()
            important_items = brief["yellow_reviews"] + brief["red_actions"]
            if important_items:
                top_item = important_items[0]
                response_text = f"Sabse important: '{top_item['title']}' from {top_item['sender']}. {top_item['reason']}"
            else:
                response_text = "Aaj koi urgent threat nahi hai. Sabhi routine items handled hain!"
            return {
                "query": query,
                "intent": "IMPORTANT_SUMMARY",
                "response": response_text,
                "brief": brief
            }

        # 3. "Is this message safe?" / "Check this message" / Analyze text input
        if "safe" in query_lower or "check" in query_lower or context_content:
            target_text = context_content if context_content else query
            eval_res = self.firewall.evaluate_proposed_action("check_message", target_text)
            
            risk_level = eval_res.get("risk_level")
            decision = eval_res.get("decision")
            why_list = eval_res.get("why", [])
            
            if decision == "BLOCK":
                response_text = f"⚠️ Ye message SAFE NAHI HAI ({risk_level} Risk). {eval_res.get('decision_reason')}"
            elif decision == "ASK_USER":
                response_text = f"🟡 Ye message CAUTION requires karta hai. Reason: {', '.join(why_list)}"
            else:
                response_text = "🟢 Ye message safe lag raha hai. Koi sensitive PII ya scam indicator nahi mila."

            return {
                "query": query,
                "intent": "SECURITY_CHECK",
                "response": response_text,
                "firewall_evaluation": eval_res
            }

        # 4. "What should I do?"
        if "do" in query_lower or "help" in query_lower:
            return {
                "query": query,
                "intent": "ACTIONABLE_ADVICE",
                "response": "Agar koi suspicious message milta hai: 1. Official app manually kholiye. 2. OTP ya UPI PIN kabhi share mat karein. 3. Sender ki email address hamesha verify karein.",
                "dos": ["Verify sender independently", "Open official app manually"],
                "donts": ["Click unknown links", "Share OTP or UPI PIN", "Pay fees to receive prizes"]
            }

        # General Fallback Response
        eval_res = self.firewall.evaluate_proposed_action("general_query", query)
        return {
            "query": query,
            "intent": "GENERAL_ASSISTANCE",
            "response": f"Main aapka AI Saathi hoon. Aap inbox status check kar sakte hain, suspicious text verify kar sakte hain, ya digital safety advice le sakte hain.",
            "firewall_evaluation": eval_res
        }
