"""
VeristasOS Local AI Analysis Service

Integrates LocalAIRouter to interpret text signals using the local Qwen2.5 3B model.
Gracefully handles server offline states and timeouts without crashing the application.
"""

from __future__ import annotations

import re
from typing import Any
from app.ai.router import LocalAIRouter


router = LocalAIRouter()


def analyze_with_ai(
    text: str,
    text_analysis: dict[str, Any],
) -> dict[str, Any]:
    """
    Local AI interpretation layer for VeristasOS.
    """
    prompt = f"""
You are the VeristasOS Truth Intelligence Engine.

Analyze linguistic misinformation risk for the text below.

RULES:
1. Do NOT claim that the content is definitively true or false.
2. Focus on sensationalism, emotional manipulation, repetition, exaggerated claims, and unsupported certainty.
3. Be concise and practical.

CONTENT:
{text[:4000]}

DETERMINISTIC LINGUISTIC SIGNALS:
- Sensationalism score: {text_analysis.get('sensationalism_score')}
- Word count: {text_analysis.get('word_count')}
- Exclamation count: {text_analysis.get('exclamation_count')}
- Uppercase word count: {text_analysis.get('uppercase_word_count')}
- Sensational words: {text_analysis.get('sensational_words')}

Return exactly:

VERDICT:
LOW RISK (or MODERATE RISK or HIGH RISK)

CONFIDENCE:
85

SUMMARY:
<concise overall interpretation>

RISK FACTORS:
- <factor 1>
- <factor 2>
- <factor 3>

VERIFICATION STEPS:
- <step 1>
- <step 2>
""".strip()

    try:
        if not router.is_available():
            return {
                "available": False,
                "message": "Local AI analysis temporarily unavailable",
                "verdict": "UNAVAILABLE",
                "confidence": 0,
                "summary": "Local Qwen AI server is offline. Deterministic linguistic analysis is active.",
                "risk_factors": [],
                "verification_steps": [
                    "Verify the publisher and author identity.",
                    "Check independent news sources for confirmation.",
                ],
                "error": "Local AI server unreachable at http://127.0.0.1:8080",
            }

        result = router.generate(prompt, max_tokens=220, temperature=0.2)

        if not result.success:
            return {
                "available": False,
                "message": "Local AI analysis temporarily unavailable",
                "verdict": "UNAVAILABLE",
                "confidence": 0,
                "summary": "Local AI engine did not return a result.",
                "risk_factors": [],
                "verification_steps": [
                    "Review deterministic linguistic metrics.",
                    "Cross-check key assertions independently.",
                ],
                "error": result.error,
            }

        content = result.content.strip()

        verdict = extract_verdict(content)
        confidence = extract_confidence(content)
        summary = extract_section(content, "SUMMARY:", "Linguistic analysis complete.")
        if summary == "Linguistic analysis complete." and "WHY:" in content:
            summary = extract_section(content, "WHY:", "Linguistic analysis complete.")

        risk_factors = extract_list_section(content, "RISK FACTORS:")
        if not risk_factors and "SIGNALS:" in content:
            risk_factors = extract_list_section(content, "SIGNALS:")

        verification_steps = extract_list_section(content, "VERIFICATION STEPS:")
        if not verification_steps and "ACTION:" in content:
            action_text = extract_section(content, "ACTION:", "")
            if action_text:
                verification_steps = [action_text]

        if not verification_steps:
            verification_steps = [
                "Locate original source reporting.",
                "Verify publication date and background context.",
            ]

        return {
            "available": True,
            "message": "Local Qwen AI analysis complete",
            "verdict": verdict,
            "confidence": confidence,
            "summary": summary,
            "risk_factors": risk_factors[:5],
            "verification_steps": verification_steps[:5],
            "raw": content,
        }

    except Exception as exc:
        return {
            "available": False,
            "message": "Local AI analysis temporarily unavailable",
            "verdict": "UNAVAILABLE",
            "confidence": 0,
            "summary": "The local AI engine encountered an error.",
            "risk_factors": [],
            "verification_steps": ["Verify claims independently using primary sources."],
            "error": str(exc),
        }


def extract_verdict(content: str) -> str:
    match = re.search(
        r"VERDICT:\s*(LOW RISK|MODERATE RISK|HIGH RISK|VERY HIGH RISK)",
        content,
        re.IGNORECASE,
    )
    if not match:
        return "MODERATE RISK"
    return match.group(1).upper()


def extract_confidence(content: str) -> int:
    match = re.search(
        r"CONFIDENCE:\s*(\d{1,3})",
        content,
        re.IGNORECASE,
    )
    if not match:
        return 75
    return min(100, int(match.group(1)))


def extract_section(content: str, heading: str, default: str) -> str:
    if heading not in content:
        return default
    value = content.split(heading, 1)[1]
    headings = ["VERDICT:", "CONFIDENCE:", "SUMMARY:", "WHY:", "RISK FACTORS:", "SIGNALS:", "VERIFICATION STEPS:", "ACTION:"]
    for h in headings:
        if h != heading and h in value:
            value = value.split(h, 1)[0]
    return value.strip() or default


def extract_list_section(content: str, heading: str) -> list[str]:
    if heading not in content:
        return []
    value = content.split(heading, 1)[1]
    headings = ["VERDICT:", "CONFIDENCE:", "SUMMARY:", "WHY:", "RISK FACTORS:", "SIGNALS:", "VERIFICATION STEPS:", "ACTION:"]
    for h in headings:
        if h != heading and h in value:
            value = value.split(h, 1)[0]

    lines = value.splitlines()
    items = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^[\-\*\•\d\.\)\s]+", "", line).strip()
        if line:
            items.append(line)
    return items