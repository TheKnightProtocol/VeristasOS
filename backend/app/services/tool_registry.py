"""
VeristasOS — Safe Tool Registry
Defines safe tool abstractions and handlers.
"""

from typing import Any, Callable, Dict, List, Optional
from app.services.text_analyzer import analyze_text
from app.services.privacy_scanner import scan_privacy_signals
from app.services.scam_detector import analyze_scam_signals
from app.services.trust_lens_engine import analyze_trust_lens


def handle_analyze_text(args: Dict[str, Any]) -> Dict[str, Any]:
    text = args.get("text", "")
    return analyze_text(text)


def handle_check_scam(args: Dict[str, Any]) -> Dict[str, Any]:
    text = args.get("text", "")
    return analyze_scam_signals(text)


def handle_check_privacy(args: Dict[str, Any]) -> Dict[str, Any]:
    text = args.get("text", "")
    return scan_privacy_signals(text)


def handle_analyze_url(args: Dict[str, Any]) -> Dict[str, Any]:
    url = args.get("url", "")
    return analyze_trust_lens(text=f"Check URL: {url}", source_url=url)


def handle_summarize_text(args: Dict[str, Any]) -> Dict[str, Any]:
    text = args.get("text", "")
    lines = text.strip().split("\n")
    summary = lines[0] if lines else text[:200]
    return {"summary": summary, "character_count": len(text)}


def handle_draft_email(args: Dict[str, Any]) -> Dict[str, Any]:
    recipient = args.get("recipient", "Recipient")
    subject = args.get("subject", "No Subject")
    body = args.get("body", "")
    return {
        "status": "draft_created",
        "recipient": recipient,
        "subject": subject,
        "body": body,
    }


def handle_send_email(args: Dict[str, Any]) -> Dict[str, Any]:
    recipient = args.get("recipient", "")
    subject = args.get("subject", "")
    return {
        "status": "email_sent",
        "recipient": recipient,
        "subject": subject,
    }


def handle_create_reminder(args: Dict[str, Any]) -> Dict[str, Any]:
    title = args.get("title", "Reminder")
    time_str = args.get("time", "Today")
    return {
        "status": "reminder_created",
        "title": title,
        "time": time_str,
    }


class SafeTool:
    """Tool metadata and handler representation."""

    def __init__(
        self,
        name: str,
        description: str,
        risk_level: str,
        requires_confirmation: bool,
        handler: Callable[[Dict[str, Any]], Dict[str, Any]],
    ):
        self.name = name
        self.description = description
        self.risk_level = risk_level
        self.requires_confirmation = requires_confirmation
        self.handler = handler

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.handler(args)


class ToolRegistry:
    """Registry of safe AI Saathi tools."""

    def __init__(self):
        self.tools: Dict[str, SafeTool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        self.register_tool(
            SafeTool(
                name="analyze_text",
                description="Analyze text sensationalism and linguistic style",
                risk_level="LOW",
                requires_confirmation=False,
                handler=handle_analyze_text,
            )
        )
        self.register_tool(
            SafeTool(
                name="check_scam",
                description="Scan text for phishing, bank, KYC, and UPI scam signals",
                risk_level="LOW",
                requires_confirmation=False,
                handler=handle_check_scam,
            )
        )
        self.register_tool(
            SafeTool(
                name="check_privacy",
                description="Scan text for Aadhaar, PAN, UPI, and OTP exposure",
                risk_level="LOW",
                requires_confirmation=False,
                handler=handle_check_privacy,
            )
        )
        self.register_tool(
            SafeTool(
                name="analyze_url",
                description="Evaluate digital trust and risk for a web URL",
                risk_level="LOW",
                requires_confirmation=False,
                handler=handle_analyze_url,
            )
        )
        self.register_tool(
            SafeTool(
                name="summarize_text",
                description="Generate concise summary of text content",
                risk_level="LOW",
                requires_confirmation=False,
                handler=handle_summarize_text,
            )
        )
        self.register_tool(
            SafeTool(
                name="draft_email",
                description="Create an email draft",
                risk_level="LOW",
                requires_confirmation=False,
                handler=handle_draft_email,
            )
        )
        self.register_tool(
            SafeTool(
                name="send_email",
                description="Send an email to an external recipient",
                risk_level="MEDIUM",
                requires_confirmation=True,
                handler=handle_send_email,
            )
        )
        self.register_tool(
            SafeTool(
                name="create_reminder",
                description="Create a calendar reminder",
                risk_level="MEDIUM",
                requires_confirmation=True,
                handler=handle_create_reminder,
            )
        )

    def register_tool(self, tool: SafeTool):
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[SafeTool]:
        return self.tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "risk_level": t.risk_level,
                "requires_confirmation": t.requires_confirmation,
            }
            for t in self.tools.values()
        ]


tool_registry_instance = ToolRegistry()
