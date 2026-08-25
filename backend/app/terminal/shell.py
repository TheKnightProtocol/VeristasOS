"""
VeristasOS Self-Healing Terminal.

Executes shell commands and automatically sends failures
to the local AI router for diagnosis. Also supports interactive built-in commands.
"""

from __future__ import annotations

import os
import sys
import subprocess

from app.ai.router import LocalAIRouter
from app.services.text_analyzer import analyze_text


class VeristasTerminal:
    """AI-assisted interactive terminal for VeristasOS."""

    def __init__(self):
        self.ai = LocalAIRouter()

    def execute(self, command: str) -> int:
        """Execute a command or handle interactive built-in commands."""
        raw_cmd = command.strip()
        if not raw_cmd:
            return 0

        cmd_lower = raw_cmd.lower()
        parts = raw_cmd.split(maxsplit=1)
        action = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        # Built-in command: help
        if action == "help":
            print("\n" + "=" * 60)
            print("             VERISTASOS TERMINAL COMMANDS")
            print("=" * 60)
            print("  help         : Display this help menu")
            print("  status       : Show backend and local AI router status")
            print("  health       : Check system health")
            print("  analyze <txt>: Run text analysis on provided content")
            print("  ai <prompt>  : Query the local Qwen AI model directly")
            print("  clear        : Clear terminal output")
            print("  exit / quit  : Exit the terminal session")
            print("  <cmd>        : Execute system command (with AI failure diagnosis)")
            print("=" * 60 + "\n")
            return 0

        # Built-in command: status
        if action == "status":
            print("\n[VeristasOS System Status]")
            print(f" Backend    : ONLINE (v1.0.0)")
            ai_online = self.ai.is_available()
            print(f" Local AI   : {'CONNECTED' if ai_online else 'OFFLINE'}")
            print(f" Provider   : llama.cpp (Qwen2.5-3B)")
            print(f" Endpoint   : {self.ai.base_url}\n")
            return 0

        # Built-in command: health
        if action == "health":
            print("\n[VeristasOS Health Check]")
            print(" Status  : healthy")
            print(" Service : VeristasOS")
            print(" Version : 1.0.0\n")
            return 0

        # Built-in command: clear
        if action == "clear":
            os.system("cls" if os.name == "nt" else "clear")
            return 0

        # Built-in command: analyze
        if action == "analyze":
            if not arg:
                print("\n[VeristasOS] Usage: analyze <text content to analyze>\n")
                return 0
            print(f"\n[VeristasOS Analysis for: '{arg[:40]}...']")
            res = analyze_text(arg)
            print(f" Word Count        : {res.get('word_count')}")
            print(f" Sensationalism    : {res.get('sensationalism_score')}/100")
            print(f" Sensational Words : {', '.join(res.get('sensational_words', [])) or 'None'}\n")
            return 0

        # Built-in command: ai
        if action == "ai":
            if not arg:
                print("\n[VeristasOS] Usage: ai <prompt or error query>\n")
                return 0
            print(f"\n[VeristasOS Local AI Querying...]")
            ai_res = self.ai.generate(arg)
            if ai_res.success:
                print("\n" + ai_res.content + "\n")
            else:
                print(f"\n[AI Error] {ai_res.error}\n")
            return 0

        # External Command Execution with AI Diagnostic on Failure
        print()
        print(f"[VeristasOS] $ {raw_cmd}")
        print()

        try:
            result = subprocess.run(
                raw_cmd,
                shell=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

        except Exception as exc:
            print("[VeristasOS] Execution error:")
            print(exc)
            return 1

        if result.stdout:
            print(result.stdout, end="")

        if result.returncode == 0:
            return 0

        print()
        print("=" * 60)
        print("VERISTASOS AI DIAGNOSTIC")
        print("=" * 60)

        stderr = result.stderr.strip()

        if stderr:
            print("\nERROR:")
            print(stderr)

        print("\nAnalyzing with local AI...")

        diagnosis = self.ai.diagnose_command(
            command=raw_cmd,
            stderr=stderr or result.stdout,
            exit_code=result.returncode,
        )

        if diagnosis.success:
            print()
            print(diagnosis.content)
        else:
            print()
            print("AI diagnostic unavailable:")
            print(diagnosis.error)

        print("=" * 60)
        return result.returncode


def run_terminal():
    """Start the interactive VeristasOS terminal."""
    terminal = VeristasTerminal()

    print()
    print("=" * 60)
    print("             VERISTASOS TERMINAL")
    print("=" * 60)
    print("Local AI: ", end="")

    if terminal.ai.is_available():
        print("CONNECTED")
    else:
        print("OFFLINE")

    print()
    print("Type a command or 'help' for built-in tools.")
    print("Type 'exit' to leave.")
    print("=" * 60)

    while True:
        try:
            command = input("\nveristasOS> ")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting VeristasOS terminal.")
            break

        if command.strip().lower() in {"exit", "quit"}:
            print("Exiting VeristasOS terminal.")
            break

        if command.strip():
            terminal.execute(command)


if __name__ == "__main__":
    run_terminal()