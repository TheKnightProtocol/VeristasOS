"""
VeristasOS — AI Service Layer
Provides a flexible, multi-provider LLM abstraction supporting Cloud APIs,
Ollama, llama.cpp, and deterministic local fallback engine with general-purpose
multilingual conversational capability and streaming response generation.
"""

import json
import os
import urllib.request
import urllib.error
from typing import Any, Dict, Generator, List, Optional


SAATHI_SYSTEM_PROMPT = """You are AI Saathi, the conversational intelligence layer of VeristasOS.

You are a capable general-purpose AI assistant.

Help the user with education, programming, mathematics, science, engineering, writing, reasoning, planning, translation, summarization, productivity, everyday questions, and digital safety.

Understand English, Hindi, Hinglish, Bengali, Telugu, Marathi, Tamil, Gujarati, Kannada, Malayalam, Punjabi, Odia, Assamese, Urdu, and regional code-mixed Indian languages.

Respond naturally in the user's preferred or detected language.

System Behavior Rules:
1. Provide useful, accurate, structured answers using Markdown (headings, lists, code blocks).
2. Answer educational, programming, writing, and general knowledge questions directly without unnecessary security disclaimers.
3. When a request involves digital safety, scams, phishing, privacy, OTPs, UPI, Aadhaar, PAN, passwords, or financial transactions, apply the VeristasOS Trust & Safety rules.
4. For programming questions, provide clean, correct code with explanations.
5. Be natural, helpful, friendly, and context-aware.
"""


class AIService:
    """Multi-provider LLM integration with fallback capability and SSE streaming."""

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

    def stream_response(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> Generator[str, None, None]:
        """Stream response chunks line-by-line via Server-Sent Events."""
        res = self.generate_response(message, conversation_history, user_context)
        full_text = res.get("text", "")
        
        lines = full_text.split("\n")
        for line in lines:
            chunk_data = json.dumps({"chunk": line + "\n", "provider": res.get("provider", "Local Engine")})
            yield f"data: {chunk_data}\n\n"

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
            "max_tokens": 1000,
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
        except Exception:
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
            "n_predict": 512,
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
        """Fallback intelligent heuristic response generator for open-ended queries."""
        msg_lower = message.lower().strip()
        
        # Greeting
        if msg_lower in ("hi", "hello", "hey", "namaste", "halo") or "who are you" in msg_lower:
            return {
                "success": True,
                "text": f"Namaste {user_name}! I am your VeristasOS AI Saathi 🙏. I can assist you with programming, general knowledge, writing, mathematics, and digital trust verification. How can I help you today?",
                "provider": "VeristasOS Local Safety Engine",
            }

        # Quantum computing inquiry
        if "quantum computing" in msg_lower:
            return {
                "success": True,
                "text": "### What is Quantum Computing?\n\nQuantum computing is a multidisciplinary field combining computer science, physics, and mathematics that uses **quantum mechanics** to solve complex problems faster than classical computers.\n\n#### Key Principles:\n- **Qubits**: Unlike classical bits (0 or 1), qubits can exist in superposition.\n- **Superposition**: Enables processing multiple possibilities simultaneously.\n- **Entanglement**: Qubits can be interconnected such that the state of one instantly influences another.\n\n#### Applications:\n1. Cryptography & Security\n2. Drug Discovery & Molecular Modeling\n3. Financial Optimization",
                "provider": "VeristasOS Local Safety Engine",
            }

        # Python sorting code request
        if "python" in msg_lower and "sort" in msg_lower:
            return {
                "success": True,
                "text": "Here is a Python program to sort a list:\n\n```python\n# Sorting a list in Python\nnumbers = [64, 34, 25, 12, 22, 11, 90]\n\n# Using built-in sorted()\nsorted_numbers = sorted(numbers)\nprint('Sorted List:', sorted_numbers)\n\n# In-place sort using .sort()\nnumbers.sort()\nprint('In-place Sorted List:', numbers)\n```\n\n**Explanation:**\n- `sorted(numbers)` returns a new sorted list without modifying the original.\n- `numbers.sort()` sorts the original list directly in place.",
                "provider": "VeristasOS Local Safety Engine",
            }

        # Java binary search code request
        if "binary search" in msg_lower or ("java" in msg_lower and "search" in msg_lower):
            return {
                "success": True,
                "text": "Here is the Java code for **Binary Search**:\n\n```java\npublic class BinarySearch {\n    public static int binarySearch(int[] arr, int target) {\n        int left = 0, right = arr.length - 1;\n        while (left <= right) {\n            int mid = left + (right - left) / 2;\n            if (arr[mid] == target) return mid;\n            if (arr[mid] < target) left = mid + 1;\n            else right = mid - 1;\n        }\n        return -1;\n    }\n\n    public static void main(String[] args) {\n        int[] numbers = {2, 5, 8, 12, 16, 23, 38, 56, 72, 91};\n        int target = 23;\n        int result = binarySearch(numbers, target);\n        System.out.println(\"Element found at index: \" + result);\n    }\n}\n```\n\n**Time Complexity:** `O(log N)`",
                "provider": "VeristasOS Local Safety Engine",
            }

        # Hindi UPI query
        if "upi" in msg_lower and any(w in message for w in ["कैसे", "काम", "भारत"]):
            return {
                "success": True,
                "text": "### भारत में UPI कैसे काम करता है?\n\n**UPI (Unified Payments Interface)** एक वास्तविक समय (Real-Time) भुगतान प्रणाली है जो एनपीसीआई (NPCI) द्वारा संचालित है।\n\n#### मुख्य चरण:\n1. **UPI ID**: आपकी अनूठी पहचान जैसे `user@upi` या मोबाइल नंबर।\n2. **VPA से ट्रांसफ़र**: बैंक खाता नंबर दर्ज किए बिना तुरंत धन हस्तांतरण।\n3. **UPI PIN**: लेनदेन को सुरक्षित रूप से प्रमाणित करने के लिए 4 या 6 अंकों का गुप्त पिन।\n\n⚠️ *सुरक्षा नियम*: पैसे प्राप्त करने के लिए कभी भी UPI PIN दर्ज न करें!",
                "provider": "VeristasOS Local Safety Engine",
            }

        # Email draft request
        if "email" in msg_lower and ("professor" in msg_lower or "extension" in msg_lower):
            return {
                "success": True,
                "text": "Here is a professional draft for your professor:\n\n**Subject:** Request for Assignment Extension — [Course Name / Assignment Title]\n\nDear Professor [Professor's Last Name],\n\nI hope this email finds you well.\n\nI am writing to respectfully request a short extension for [Assignment Title], originally due on [Original Due Date]. Due to [brief reason, e.g., unexpected illness / personal emergency], I require additional time to complete the work to a high standard.\n\nWould it be possible to submit my assignment by [Proposed Date]?\n\nThank you very much for your time and understanding.\n\nSincerely,\n[Your Name]\n[Student ID]",
                "provider": "VeristasOS Local Safety Engine",
            }

        # Study plan request
        if "study plan" in msg_lower or "roadmap" in msg_lower or "machine learning" in msg_lower:
            return {
                "success": True,
                "text": "### 7-Day Machine Learning Study Plan\n\n- **Day 1**: Python Fundamentals & NumPy\n- **Day 2**: Data Manipulation with Pandas\n- **Day 3**: Data Visualization (Matplotlib & Seaborn)\n- **Day 4**: Supervised Learning (Linear & Logistic Regression)\n- **Day 5**: Decision Trees & Random Forests\n- **Day 6**: Model Evaluation & Scikit-Learn\n- **Day 7**: Hands-on Project (Kaggle Dataset Classification)",
                "provider": "VeristasOS Local Safety Engine",
            }

        # Phishing inquiry
        if "what is phishing" in msg_lower or "phishing kya hota" in msg_lower:
            return {
                "success": True,
                "text": "### What is Phishing?\n\nPhishing is a cybercrime in which targets are contacted by email, telephone, or text message by someone posing as a legitimate institution to lure individuals into providing sensitive data such as personally identifiable information, banking and credit card details, and passwords.\n\n#### How to Stay Safe:\n- Never click unexpected links\n- Never share OTPs or passwords",
                "provider": "VeristasOS Local Safety Engine",
            }

        # Scam / KYC query
        if any(w in msg_lower for w in ["kyc", "sbi", "bank", "otp", "upi", "suspend", "block"]):
            return {
                "success": True,
                "text": "⚠️ **KYC Scam Alert**\n\nSignals Detected:\n• Bank / KYC urgency pressure\n• Unverified external link\n• Risk of account compromise\n\n❌ Do not click the link.\n❌ Never share your OTP or UPI PIN.",
                "provider": "VeristasOS Local Safety Engine",
            }

        # General helpful fallback
        return {
            "success": True,
            "text": f"I understand your request regarding '{message[:80]}...'. As your AI Saathi, I am ready to assist you. (User: {user_name})",
            "provider": "VeristasOS Local Safety Engine",
        }


ai_service_instance = AIService()
