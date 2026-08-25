"""
VeristasOS Claim Extraction Service

Extracts key factual claims and assertions from submitted text.
Does not claim to perform automated truth verification; marks claims as UNVERIFIED.
"""

from __future__ import annotations

import re
from typing import Any
import nltk
from nltk.tokenize import sent_tokenize


def ensure_nltk_sent_tokenize():
    """Ensure sentence tokenizer resources are available."""
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        try:
            nltk.download("punkt", quiet=True)
            nltk.download("punkt_tab", quiet=True)
        except Exception:
            pass


def extract_claims(text: str) -> list[dict[str, Any]]:
    """
    Extract factual claims from text using linguistic heuristics.

    Returns a list of structured claim dictionaries:
    [
        {
            "claim": "...",
            "type": "factual",
            "verification_status": "unverified"
        }
    ]
    """
    if not isinstance(text, str) or not text.strip():
        return []

    ensure_nltk_sent_tokenize()

    try:
        sentences = sent_tokenize(text.strip())
    except Exception:
        # Fallback to regex sentence splitting if NLTK fails
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]

    extracted_claims = []

    # Indicators of factual assertion: numbers, dates, named entity patterns, key verbs
    factual_keywords = re.compile(
        r"\b(\d+|percent|%|million|billion|trillion|dollars|\$|proved|announced|confirmed|reported|stated|discovered|caused|found|according|officials|scientists|study|data|government|court|hospital|police|death|killed|stolen|secret|leaked)\b",
        re.IGNORECASE,
    )

    for sentence in sentences:
        sentence_clean = sentence.strip().replace("\n", " ")
        if len(sentence_clean) < 15 or len(sentence_clean) > 300:
            continue

        # Skip obvious questions or exclamatory pure banter if desired, but keep strong declarative statements
        is_factual = bool(factual_keywords.search(sentence_clean)) or (
            len(sentence_clean.split()) >= 5 and not sentence_clean.endswith("?")
        )

        if is_factual:
            extracted_claims.append(
                {
                    "claim": sentence_clean,
                    "type": "factual",
                    "verification_status": "unverified",
                }
            )

        if len(extracted_claims) >= 6:
            break

    # If no claims matched criteria, pick up to 3 sentences as candidate claims
    if not extracted_claims and sentences:
        for s in sentences[:3]:
            if len(s.strip()) >= 10:
                extracted_claims.append(
                    {
                        "claim": s.strip(),
                        "type": "declarative",
                        "verification_status": "unverified",
                    }
                )

    return extracted_claims
