"""
VeristasOS Semantic Search Engine

Provides lightweight, dependency-safe semantic search and vector representation using
TF-IDF vectorization and Cosine Similarity over local evidence repositories.
Supports full corpus searching, pagination, and sorting by relevance, date, or reliability.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.schemas import EvidenceItem, EvidenceMatch


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_EVIDENCE_PATH = PROJECT_ROOT / "data" / "evidence" / "evidence.json"


class SemanticSearchEngine:
    """
    Semantic search and similarity engine over local evidence index.
    """

    def __init__(self, evidence_file: Optional[Path] = None):
        self.evidence_file = evidence_file or DEFAULT_EVIDENCE_PATH
        self.evidence_list: list[EvidenceItem] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix: Optional[Any] = None
        self.load_index()

    def load_index(self) -> None:
        """Load evidence records from disk and fit TF-IDF vector space."""
        raw_items = []
        if self.evidence_file.exists():
            try:
                content = self.evidence_file.read_text(encoding="utf-8")
                raw_items = json.loads(content)
            except Exception:
                raw_items = []

        if not raw_items:
            # Fallback embedded demo evidence records
            raw_items = [
                {
                    "id": "EV-101",
                    "title": "Municipal Public Transit Infrastructure Budget Review 2026",
                    "text": "The city municipal council approved a budget allocation increase of 4.2 percent for public transit infrastructure during the open session on Tuesday. Official records indicate the decision followed a thorough three-month review of commuter transit data.",
                    "source": "Municipal Gazette",
                    "source_url": "https://cityjournal.org/transit-update-2026",
                    "publication_date": "2026-02-10",
                    "category": "infrastructure",
                    "reliability_score": 95.0,
                    "evidence_type": "DEMO EVIDENCE",
                },
                {
                    "id": "EV-102",
                    "title": "Clinical Trial Meta-Analysis on Universal Therapeutics Claims",
                    "text": "Peer-reviewed medical trials published in leading oncology journals confirm that no universal instant single-day cure exists for all human cancers. Standard targeted immunotherapies require months of protocol treatment and individual genetic profiling.",
                    "source": "Global Medical Journal",
                    "source_url": "https://medicaljournal.org/trials/oncology-2026",
                    "publication_date": "2026-01-20",
                    "category": "health",
                    "reliability_score": 98.0,
                    "evidence_type": "DEMO EVIDENCE",
                },
                {
                    "id": "EV-103",
                    "title": "Global Energy Outlook & Renewable Transition Statistics",
                    "text": "International energy regulatory agencies published empirical data indicating solar and wind power generation grew by 18 percent globally year-over-year.",
                    "source": "Energy Regulatory Bureau",
                    "source_url": "https://energybureau.org/reports/transition-2026",
                    "publication_date": "2026-03-01",
                    "category": "energy",
                    "reliability_score": 92.0,
                    "evidence_type": "DEMO EVIDENCE",
                },
                {
                    "id": "EV-104",
                    "title": "Central Bank Policy Statement on Inflationary Pressure",
                    "text": "Official central banking monetary committee reports confirm benchmark interest rates were held steady following quarterly inflation statistics review.",
                    "source": "Central Financial Journal",
                    "source_url": "https://financialjournal.org/rates-2026",
                    "publication_date": "2026-02-28",
                    "category": "finance",
                    "reliability_score": 96.0,
                    "evidence_type": "DEMO EVIDENCE",
                },
                {
                    "id": "EV-105",
                    "title": "Cybersecurity Vulnerability Audit of Critical Power Grids",
                    "text": "National cybersecurity agency released an infrastructure warning regarding patch deployment for industrial control systems across regional power distribution facilities.",
                    "source": "Cyber Defense Authority",
                    "source_url": "https://cyberauthority.gov/alerts/grid-2026",
                    "publication_date": "2026-01-15",
                    "category": "security",
                    "reliability_score": 99.0,
                    "evidence_type": "DEMO EVIDENCE",
                },
            ]

        self.evidence_list = [EvidenceItem(**item) for item in raw_items]

        corpus = [
            f"{item.title} {item.text} {item.category} {item.source}"
            for item in self.evidence_list
        ]

        if corpus:
            self.vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                sublinear_tf=True,
            )
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def search_similar_claims(
        self,
        query: str,
        top_k: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
        category: Optional[str] = None,
        sort_by: str = "relevance",
    ) -> list[EvidenceMatch]:
        """
        Query vector space for semantically related evidence with full corpus pagination.
        """
        if not query.strip() or not self.vectorizer or self.tfidf_matrix is None or not self.evidence_list:
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        matches: list[EvidenceMatch] = []

        for idx, sim_score in enumerate(similarities):
            item = self.evidence_list[idx]

            if category and item.category.lower() != category.lower():
                continue

            score_percent = round(float(sim_score) * 100, 2)

            relationship = "INSUFFICIENT"
            explanation = "Low semantic similarity to indexed evidence."

            query_lower = query.lower()
            text_lower = item.text.lower()

            if score_percent >= 45:
                contradiction_terms = {"no", "not", "refuses", "myth", "debunked", "false", "warned", "fake"}
                if any(w in text_lower for w in contradiction_terms) and ("cure" in query_lower or "100%" in query_lower or "secret" in query_lower):
                    relationship = "CONTRADICTING"
                    explanation = "Indexed evidence directly disputes or debunks assertions in the claim."
                else:
                    relationship = "SUPPORTING"
                    explanation = "High semantic and topical similarity with indexed authoritative reporting."
            elif score_percent >= 15:
                relationship = "RELATED"
                explanation = "Related subject area context found in evidence database."

            matches.append(
                EvidenceMatch(
                    evidence=item,
                    similarity_score=score_percent,
                    relationship=relationship,
                    explanation=explanation,
                )
            )

        # Sorting logic
        if sort_by == "newest":
            matches.sort(key=lambda m: m.evidence.publication_date or "", reverse=True)
        elif sort_by == "reliability":
            matches.sort(key=lambda m: m.evidence.reliability_score, reverse=True)
        else:  # default "relevance"
            matches.sort(key=lambda m: m.similarity_score, reverse=True)

        # Pagination slice
        if top_k is not None:
            return matches[:top_k]

        return matches[offset : offset + limit]

    def count_matches(self, query: str, category: Optional[str] = None) -> int:
        """Count total matching evidence records for query."""
        all_matches = self.search_similar_claims(query=query, top_k=None, limit=10000, offset=0, category=category)
        return len(all_matches)

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Calculate pairwise cosine similarity score (0.0 to 100.0) between two text strings."""
        if not text1.strip() or not text2.strip():
            return 0.0

        vec = TfidfVectorizer(stop_words="english")
        try:
            mat = vec.fit_transform([text1, text2])
            sim = cosine_similarity(mat[0:1], mat[1:2])[0][0]
            return round(float(sim) * 100, 2)
        except Exception:
            return 0.0


search_engine = SemanticSearchEngine()
