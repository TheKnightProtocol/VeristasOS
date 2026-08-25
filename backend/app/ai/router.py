"""
VeristasOS Local AI Router

Connects VeristasOS to a local llama.cpp HTTP server.
No cloud API is required.

Default server:
    http://127.0.0.1:8080
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
import socket
import urllib.error
import urllib.request


@dataclass
class AIResponse:
    """Standard response returned by the local AI router."""

    success: bool
    content: str = ""
    error: str = ""
    raw: dict | None = None


class LocalAIRouter:
    """
    Local AI gateway for VeristasOS.

    Expected backend:
        llama.cpp llama-server

    Endpoint:
        POST /completion
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: int | None = None,
    ):
        self.base_url = (
            base_url
            or os.getenv(
                "VERISTAS_AI_URL",
                "http://127.0.0.1:8080",
            )
        ).rstrip("/")

        # Fast timeout (default 5s) so application never hangs if local LLM is slow or offline
        self.timeout = timeout or int(
            os.getenv("VERISTAS_AI_TIMEOUT", "5")
        )

    def is_available(self) -> bool:
        """Check whether the local llama.cpp server is reachable via fast TCP probe."""
        try:
            host = "127.0.0.1"
            port = 8080
            if "://" in self.base_url:
                url_part = self.base_url.split("://", 1)[1]
                parts = url_part.split(":", 1)
                host = parts[0]
                if len(parts) > 1:
                    port = int(parts[1].split("/")[0])

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.3)
                s.connect((host, port))

            request = urllib.request.Request(
                f"{self.base_url}/health",
                method="GET",
            )
            with urllib.request.urlopen(request, timeout=1.0) as response:
                return response.status == 200

        except Exception:
            return False

    def _post(
        self,
        endpoint: str,
        payload: dict,
    ) -> dict:
        """Send JSON POST request to the local AI server."""
        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            f"{self.base_url}{endpoint}",
            data=data,
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urllib.request.urlopen(
            request,
            timeout=self.timeout,
        ) as response:
            raw = response.read().decode("utf-8")

        return json.loads(raw)

    def generate(
        self,
        prompt: str,
        max_tokens: int = 160,
        temperature: float = 0.2,
    ) -> AIResponse:
        """Generate a response from the local model."""
        if not prompt.strip():
            return AIResponse(
                success=False,
                error="Prompt cannot be empty.",
            )

        payload = {
            "prompt": prompt,
            "n_predict": max_tokens,
            "temperature": temperature,
            "stream": False,
        }

        try:
            response = self._post(
                "/completion",
                payload,
            )

            content = response.get("content", "")

            if not content:
                return AIResponse(
                    success=False,
                    error="Local AI returned an empty response.",
                    raw=response,
                )

            return AIResponse(
                success=True,
                content=content.strip(),
                raw=response,
            )

        except urllib.error.URLError as exc:
            return AIResponse(
                success=False,
                error=f"Local AI server unavailable: {exc}",
            )

        except TimeoutError:
            return AIResponse(
                success=False,
                error=(
                    "Local AI generation timed out. "
                    "The model may need more time on this machine."
                ),
            )

        except Exception as exc:
            return AIResponse(
                success=False,
                error=f"Local AI error: {exc}",
            )

    def diagnose_command(
        self,
        command: str,
        stderr: str,
        exit_code: int,
    ) -> AIResponse:
        """Analyze a failed terminal command and suggest a safe fix."""
        prompt = f"""
You are VeristasOS, a local developer troubleshooting assistant.

A terminal command failed.

COMMAND:
{command}

EXIT CODE:
{exit_code}

ERROR:
{stderr[:5000]}

Give a concise answer using exactly these sections:

WHY:
Explain the likely cause in one or two sentences.

FIX:
Give the safest practical fix as a copy-pasteable command.

NOTE:
Mention one important caution only if necessary.
""".strip()

        return self.generate(
            prompt,
            max_tokens=180,
            temperature=0.15,
        )

    def explain_error(
        self,
        error: str,
    ) -> AIResponse:
        """Explain a generic system error."""
        prompt = f"""
You are the VeristasOS local troubleshooting assistant.

Explain this error briefly:

{error[:5000]}

Return:
WHY:
FIX:
""".strip()

        return self.generate(
            prompt,
            max_tokens=120,
            temperature=0.15,
        )