"""
VeristasOS Provenance & Source Analysis Service

Evaluates provided source metadata (URL, publisher, author, date)
and generates transparency scoring.

IMPORTANT:
Clearly distinguishes user-provided source metadata from independent verification.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse


def analyze_provenance(
    source_url: str | None = None,
    source_name: str | None = None,
    author: str | None = None,
    publication_date: str | None = None,
) -> dict[str, Any]:
    """
    Analyze source provenance metadata and compute a transparency score.
    """
    has_url = bool(source_url and source_url.strip())
    has_name = bool(source_name and source_name.strip())
    has_author = bool(author and author.strip())
    has_date = bool(publication_date and publication_date.strip())

    source_available = has_url or has_name or has_author or has_date

    if not source_available:
        return {
            "source_available": False,
            "source_url": None,
            "source_name": None,
            "author": None,
            "publication_date": None,
            "provenance_score": 0,
            "status": "Not provided",
            "verification_status": "Unverified - No source specified",
            "domain": None,
            "details": "No source origin metadata was supplied with this analysis request.",
        }

    # Calculate transparency score based on metadata availability
    score = 0
    if has_name:
        score += 35
    if has_url:
        score += 35
    if has_author:
        score += 15
    if has_date:
        score += 15

    domain = None
    if has_url:
        try:
            parsed = urlparse(source_url.strip())
            domain = parsed.netloc or parsed.path.split("/")[0]
        except Exception:
            domain = None

    return {
        "source_available": True,
        "source_url": source_url.strip() if source_url else None,
        "source_name": source_name.strip() if source_name else (domain or "Unknown Publisher"),
        "author": author.strip() if author else None,
        "publication_date": publication_date.strip() if publication_date else None,
        "provenance_score": min(100, score),
        "status": "Source information provided",
        "verification_status": "Requires independent verification",
        "domain": domain,
        "details": (
            "Source origin metadata was supplied by the user. "
            "Note: Metadata provided by submission has not been independently cross-checked against live web registries."
        ),
    }
