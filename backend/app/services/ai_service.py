"""
VeristasOS — AI Service Layer
Provides a flexible, multi-provider LLM abstraction supporting Cloud APIs,
Ollama, llama.cpp, and deterministic local fallback engine.
"""

import json
import os
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional


SAATHI_SYSTEM_PROMPT = """You are VeristasOS AI Saathi, a safety-first personal AI agent.
Your primary role is to help users understand, verify, and safely navigate digital information.

System Behavior Rules:
1. Answer naturally, helpfully, and concisely in English, Hindi, or Hinglish as preferred by the user.
2. Remember conversation context when relevant.
3. Identify digital threats (KYC scams, fake UPI requests, OTP phishing, malicious links, Aadhaar/PAN leaks).
4. Clearly explain security risks without technical jargon.
5. If content looks suspicious or asks for money/OTP/passwords, advise caution clearly.
6. Never claim certainty when evidence is insufficient.
7. Distinguish raw model signals from verified digital evidence.
"""


class AIService:
    """Multi-provider LLM integration with fallback capability."""

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "auto").lower()
        self.api_key = os.getenv("LLM_API_KEY", "").strip()
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
        self.llamacpp_host = os.getenv("LLAMA_CPP_HOST", "http://127.0.0.1:8080").rstrip("/")

    def generate_response(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate response using configured LLM provider with fallback."""
        history = conversation_history or []
        user_name = (user_context or {}).get("user_name", "User")
        user_mode = (user_context or {}).get("user_mode", "Adult")

        # 1. Try Cloud LLM Provider if configured
        if self.provider in ("cloud", "openai", "auto") and self.api_key:
            res = self._call_cloud_llm(message, history, user_name, user_mode)
            if res.get("success"):
                return res

        # 2. Try Ollama if requested or auto
        if self.provider in ("ollama", "auto"):
            res = self._call_ollama(message, history, user_name)
            if res.get("success"):
                return res

        # 3. Try Llama.cpp if requested or auto
        if self.provider in ("llamacpp", "llama", "auto"):
            res = self._call_llamacpp(message, history, user_name)
            if res.get("success"):
                return res

        # 4. Fallback to Local Deterministic Reasoning Engine
        return self._deterministic_fallback(message, history, user_name, user_mode)

    def _call_cloud_llm(
        self,
        message: str,
        history: List[Dict[str, str]],
        user_name: str,
        user_mode: str,
    ) -> Dict[str, Any]:
        """Call OpenAI-compatible chat completions API."""
        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        messages = [{"role": "system", "content": SAATHI_SYSTEM_PROMPT + f"\nUser Name: {user_name}\nMode: {user_mode}"}]
        for turn in history[-6:]:
            messages.append({"role": turn.get("role", "user"), "content": turn.get("message", "")})
        messages.append({"role": "user", "content": message})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.5,
            "max_tokens": 500,
        }

        try:
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    text = data["choices"][0]["message"]["content"].strip()
                    return {"success": True, "text": text, "provider": f"Cloud ({self.model})"}
        except Exception as exc:
            pass

        return {"success": False, "error": "Cloud LLM unreachable"}

    def _call_ollama(
        self,
        message: str,
        history: List[Dict[str, str]],
        user_name: str,
    ) -> Dict[str, Any]:
        """Call local Ollama server."""
        endpoint = f"{self.ollama_host}/api/chat"
        messages = [{"role": "system", "content": SAATHI_SYSTEM_PROMPT}]
        for turn in history[-6:]:
            messages.append({"role": turn.get("role", "user"), "content": turn.get("message", "")})
        messages.append({"role": "user", "content": message})

        payload = {
            "model": "llama3",
            "messages": messages,
            "stream": False,
        }

        try:
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    text = data.get("message", {}).get("content", "").strip()
                    if text:
                        return {"success": True, "text": text, "provider": "Ollama"}
        except Exception:
            pass

        return {"success": False, "error": "Ollama unreachable"}

    def _call_llamacpp(
        self,
        message: str,
        history: List[Dict[str, str]],
        user_name: str,
    ) -> Dict[str, Any]:
        """Call local llama.cpp server."""
        endpoint = f"{self.llamacpp_host}/completion"
        prompt = f"<|im_start|>system\n{SAATHI_SYSTEM_PROMPT}\nUser Name: {user_name}<|im_end|>\n"
        for turn in history[-4:]:
            role = turn.get("role", "user")
            prompt += f"<|im_start|>{role}\n{turn.get('message', '')}<|im_end|>\n"
        prompt += f"<|im_start|>user\n{message}<|im_end|>\n<|im_start|>assistant\n"

        payload = {
            "prompt": prompt,
            "n_predict": 256,
            "temperature": 0.4,
            "stop": ["<|im_end|>", "User:"],
        }

        try:
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    text = data.get("content", "").strip()
                    if text:
                        return {"success": True, "text": text, "provider": "llama.cpp"}
        except Exception:
            pass

        return {"success": False, "error": "llama.cpp unreachable"}

    def _deterministic_fallback(
        self,
        message: str,
        history: List[Dict[str, str]],
        user_name: str,
        user_mode: str,
    ) -> Dict[str, Any]:
        """Fallback intelligent heuristic response generator."""
        msg_lower = message.lower().strip()
        
        # Greeting
        if msg_lower in ("hi", "hello", "hey", "namaste", "halo") or "who are you" in msg_lower:
            return {
                "success": True,
                "text": f"Namaste {user_name}! I am your VeristasOS AI Saathi 🙏. How can I help protect and verify your digital information today?",
                "provider": "VeristasOS Local Safety Engine",
            }

        # Phishing inquiry
        if "what is phishing" in msg_lower or "phishing kya hota" in msg_lower:
            return {
                "success": True,
                "text": "Phishing ek online scam hai jahan fraudsters fake emails, SMS ya websites ka use karke aapki personal detail (jaise passwords, OTP, bank PIN) churane ki koshish karte hain.\n\nKey Rule: Kabhi bhi unexpected links par click na karein aur apna OTP kisi se share na karein.",
                "provider": "VeristasOS Local Safety Engine",
            }

        # Scam / KYC query
        if any(w in msg_lower for w in ["kyc", "sbi", "bank", "otp", "upi", "suspend", "block"]):
            return {
                "success": True,
                "text": "⚠️ Ye message suspicious lag raha hai!\n\nSignals:\n• Bank / KYC urgency pressure\n• Unverified external link\n• Risks of account compromise\n\n❌ Link mat kholo.\n❌ OTP / UPI PIN kabhi share mat karo.",
                "provider": "VeristasOS Local Safety Engine",
            }

        # General helpful fallback
        return {
            "success": True,
            "text": f"Main aapka request understand kar raha hoon. VeristasOS Digital Trust Engine aapki safety verify kar raha hai. (User: {user_name})",
            "provider": "VeristasOS Local Safety Engine",
        }


ai_service_instance = AIService()
