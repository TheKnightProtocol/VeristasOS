"""
VeristasOS Source & Provenance Intelligence Subsystem

Evaluates metadata completeness, domain legitimacy, author attribution, citation presence,
and protocol security to produce transparent provenance scoring.
"""

from __future__ import annotations

from typing import Any, Optional
from urllib.parse import urlparse


def evaluate_source_intelligence(
    source_url: Optional[str] = None,
    source_name: Optional[str] = None,
    author: Optional[str] = None,
    publication_date: Optional[str] = None,
    article_text: Optional[str] = None,
) -> dict[str, Any]:
    """
    Perform multi-vector transparent source and provenance intelligence scoring.
    """
    domain_transparency = 0.0
    author_transparency = 0.0
    metadata_completeness = 0.0
    citation_availability = 0.0
    https_security = 0.0

    domain = ""
    if source_url and source_url.strip():
        parsed = urlparse(source_url.strip())
        domain = parsed.netloc.lower()
        if domain:
            domain_transparency = 85.0
            if any(tld in domain for tld in [".gov", ".edu", ".org", ".ac.uk"]):
                domain_transparency = 98.0
            elif any(tld in domain for tld in [".xyz", ".top", ".info", ".click", ".buzz"]):
                domain_transparency = 35.0

        if parsed.scheme == "https":
            https_security = 100.0
        elif parsed.scheme == "http":
            https_security = 40.0

    if author and author.strip() and author.strip().lower() not in ("anonymous", "unknown", "admin", "n/a"):
        author_transparency = 90.0
    elif author and author.strip():
        author_transparency = 30.0

    metadata_count = sum(1 for val in [source_url, source_name, author, publication_date] if val and val.strip())
    metadata_completeness = min(100.0, (metadata_count / 4.0) * 100.0)

    if article_text and article_text.strip():
        text_lower = article_text.lower()
        citation_keywords = ["according to", "reported by", "study published", "officials stated", "data shows", "source:", "ref:", "citation"]
        matches = sum(1 for kw in citation_keywords if kw in text_lower)
        citation_availability = min(100.0, matches * 25.0)

    provenance_score = round(
        (domain_transparency * 0.25)
        + (author_transparency * 0.20)
        + (metadata_completeness * 0.25)
        + (citation_availability * 0.20)
        + (https_security * 0.10),
        1,
    )

    if provenance_score >= 80:
        trust_classification = "HIGH PROVENANCE TRANSPARENCY"
    elif provenance_score >= 50:
        trust_classification = "MODERATE PROVENANCE TRANSPARENCY"
    else:
        trust_classification = "LIMITED PROVENANCE TRANSPARENCY"

    return {
        "domain": domain or "Unspecified",
        "publisher": source_name or "Not provided",
        "author": author or "Not provided",
        "publication_date": publication_date or "Not provided",
        "provenance_score": provenance_score,
        "trust_classification": trust_classification,
        "metrics": {
            "domain_transparency": round(domain_transparency, 1),
            "author_transparency": round(author_transparency, 1),
            "metadata_completeness": round(metadata_completeness, 1),
            "citation_availability": round(citation_availability, 1),
            "https_security": round(https_security, 1),
        },
        "heuristics_note": "Evaluated using heuristic transparency indicators. Does not constitute manual editorial endorsement.",
    }
