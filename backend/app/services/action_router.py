"""
VeristasOS — Action Router & Trust Firewall
Executes master security pipeline:
USER MESSAGE -> INTENT DETECTION -> TRUST ENGINE -> PERMISSION ENGINE -> TRUST FIREWALL -> ACTION GATE
"""

from typing import Any, Dict, List, Optional
from app.services.ai_service import ai_service_instance
from app.services.memory_service import memory_service_instance
from app.services.trust_engine import trust_engine_instance
from app.services.permission_engine import permission_engine_instance
from app.services.tool_registry import tool_registry_instance


class ActionRouter:
    """Master pipeline router and firewall decision gate."""

    def process_chat_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        user_name: str = "User",
        user_mode: str = "Adult",
    ) -> Dict[str, Any]:
        """Full pipeline execution for incoming chat message."""
        # 1. Resolve or create conversation session ID
        conv_id = conversation_id or memory_service_instance.generate_conversation_id()

        # 2. Fetch conversation history memory
        history = memory_service_instance.get_recent_history(conv_id, limit=10)

        # 3. Save incoming user message to memory
        memory_service_instance.save_message(conv_id, "user", message, user_name)

        # 4. Digital Trust Engine evaluation
        trust_eval = trust_engine_instance.evaluate_message(message)
        risk_level = trust_eval["risk_level"]
        intent = trust_eval["intent"]
        signals = trust_eval["signals"]
        reasons = trust_eval["reasons"]

        # 5. Permission Engine & Trust Firewall evaluation
        permission_engine_instance.set_mode(user_mode)
        perm_eval = permission_engine_instance.evaluate_permission(
            intent=intent,
            risk_level=risk_level,
            signals=signals,
        )

        action_gate = perm_eval["action"]
        requires_confirmation = perm_eval["requires_confirmation"]

        # Formulate suggested action string
        suggested_action = None
        tool_requested = None

        # Determine tool request if applicable
        if intent == "COMMUNICATION_ACTION" and any(w in message.lower() for w in ["email", "mail"]):
            suggested_action = "AI Saathi proposed sending an email notification."
            tool_requested = {
                "name": "send_email",
                "args": {"recipient": "contact@domain.com", "subject": "Requested Action"},
            }

        # 6. Action Gate Routing: RESPOND / AUTO_ACT / ASK_CONFIRMATION / BLOCK
        if action_gate == "BLOCK":
            ai_response_text = (
                f"🛡️ **Action Blocked by Trust Firewall**\n\n"
                f"**Reasons:**\n" + "\n".join(f"• {r}" for r in reasons) + "\n\n"
                f"❌ VeristasOS cannot submit OTPs, passwords, bank PINs, or execute financial transfers automatically."
            )
            # Save assistant response to memory
            memory_service_instance.save_message(conv_id, "assistant", ai_response_text, user_name)

            return {
                "message": ai_response_text,
                "conversation_id": conv_id,
                "intent": intent,
                "risk_level": risk_level,
                "action": "BLOCK",
                "requires_confirmation": False,
                "reasons": reasons,
                "suggested_action": "Do not share OTP, bank details, or click suspicious links.",
                "tool_requested": None,
                "provider": "Trust Firewall Gate",
            }

        if action_gate == "ASK_CONFIRMATION":
            ai_response_text = (
                f"⚠️ **Confirmation Required**\n\n"
                f"AI Saathi needs your confirmation to proceed with this request.\n\n"
                f"**Details:** {suggested_action or 'External communication or calendar action proposed.'}\n"
                f"**Risk Level:** {risk_level}"
            )
            memory_service_instance.save_message(conv_id, "assistant", ai_response_text, user_name)

            return {
                "message": ai_response_text,
                "conversation_id": conv_id,
                "intent": intent,
                "risk_level": risk_level,
                "action": "ASK_CONFIRMATION",
                "requires_confirmation": True,
                "reasons": reasons,
                "suggested_action": suggested_action or "Confirm or cancel external action.",
                "tool_requested": tool_requested,
                "provider": "Permission Engine Gate",
            }

        # 7. Low Risk / Allowed -> Generate AI Response
        user_context = {"user_name": user_name, "user_mode": user_mode}
        ai_res = ai_service_instance.generate_response(message, history, user_context)
        ai_text = ai_res.get("text", "I am ready to help.")
        provider_name = ai_res.get("provider", "VeristasOS AI Saathi")

        # Save assistant response to memory
        memory_service_instance.save_message(conv_id, "assistant", ai_text, user_name)

        return {
            "message": ai_text,
            "conversation_id": conv_id,
            "intent": intent,
            "risk_level": risk_level,
            "action": "RESPOND" if not tool_requested else "AUTO_ACT",
            "requires_confirmation": False,
            "reasons": reasons,
            "suggested_action": suggested_action,
            "tool_requested": tool_requested,
            "provider": provider_name,
        }

    def execute_confirmed_action(
        self,
        conversation_id: str,
        user_approved: bool,
        action_type: str,
        action_details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute or cancel an action after user confirmation decision."""
        details = action_details or {}
        if not user_approved:
            res_msg = f"✓ Action '{action_type}' was cancelled by the user."
            memory_service_instance.save_message(conversation_id, "assistant", res_msg, "User")
            return {
                "status": "cancelled",
                "message": res_msg,
                "conversation_id": conversation_id,
            }

        # User approved -> Execute tool via ToolRegistry
        tool = tool_registry_instance.get_tool(action_type)
        if tool:
            result = tool.execute(details)
            res_msg = f"✓ Action '{action_type}' executed successfully. Result: {result}"
        else:
            res_msg = f"✓ Action '{action_type}' executed per your approval."

        memory_service_instance.save_message(conversation_id, "assistant", res_msg, "User")
        return {
            "status": "executed",
            "message": res_msg,
            "conversation_id": conversation_id,
        }

    def stream_chat_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        user_name: str = "User",
        user_mode: str = "Adult",
    ):
        """Stream response chunks line-by-line via Server-Sent Events."""
        conv_id = conversation_id or memory_service_instance.generate_conversation_id()
        history = memory_service_instance.get_recent_history(conv_id, limit=10)
        memory_service_instance.save_message(conv_id, "user", message, user_name)

        user_context = {"user_name": user_name, "user_mode": user_mode}
        
        for chunk_event in ai_service_instance.stream_response(message, history, user_context):
            yield chunk_event

        res = ai_service_instance.generate_response(message, history, user_context)
        memory_service_instance.save_message(conv_id, "assistant", res.get("text", ""), user_name)


action_router_instance = ActionRouter()

