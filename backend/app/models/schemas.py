"""
VeristasOS Structured Data Schemas & Models
"""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


class UnifiedAnalyzeRequest(BaseModel):
    """Request payload for unified truth intelligence analysis."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Article or claim text content to analyze.",
    )
    source_url: Optional[str] = Field(None, description="Optional source URL.")
    source_name: Optional[str] = Field(None, description="Optional publisher or source name.")
    author: Optional[str] = Field(None, description="Optional author name.")
    publication_date: Optional[str] = Field(None, description="Optional publication date.")


class SimpleTextRequest(BaseModel):
    """Simple text request for AI analysis."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Text content for AI interpretation.",
    )


class SemanticSearchRequest(BaseModel):
    """Request payload for semantic evidence search."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Claim or topic search query.",
    )
    top_k: Optional[int] = Field(None, description="Legacy top_k filter.")
    limit: int = Field(20, ge=1, le=100, description="Max items per page.")
    offset: int = Field(0, ge=0, description="Pagination offset index.")
    category: Optional[str] = Field(None, description="Optional category filter.")
    sort_by: str = Field("relevance", description="Sort criteria: relevance | newest | reliability")


class InvestigationRequest(BaseModel):
    """Master request payload for full truth-intelligence investigation."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Article or text body to investigate.",
    )
    source_url: Optional[str] = Field(None, description="Optional source URL.")
    source_name: Optional[str] = Field(None, description="Optional source name.")
    author: Optional[str] = Field(None, description="Optional author name.")
    publication_date: Optional[str] = Field(None, description="Optional publication date.")


class AuthenticitySignal(BaseModel):
    """Signal item for media authenticity evaluation."""

    name: str
    status: str  # VERIFIED SIGNAL | SUSPICIOUS SIGNAL | INCONCLUSIVE | NOT AVAILABLE
    detail: str


class MediaAuthenticityResponse(BaseModel):
    """Structured media authenticity evaluation response model."""

    available: bool
    assessment: str  # LIKELY AUTHENTIC | SUSPICIOUS | INCONCLUSIVE
    score: int
    confidence: int
    signals: list[AuthenticitySignal]
    limitations: str
    model: str


class EvidenceItem(BaseModel):
    """Individual evidence record model."""

    id: str
    title: str
    text: str
    source: str
    source_url: Optional[str] = None
    publication_date: Optional[str] = None
    category: str = "general"
    reliability_score: float = 80.0
    evidence_type: str = "DEMO EVIDENCE"


class EvidenceMatch(BaseModel):
    """Matched evidence entry with similarity score and relationship classification."""

    evidence: EvidenceItem
    similarity_score: float
    relationship: str  # SUPPORTING | CONTRADICTING | RELATED | INSUFFICIENT
    explanation: str


class GraphNode(BaseModel):
    """Node representation in investigation relationship graph."""

    id: str
    label: str
    type: str  # Article | Claim | Source | Author | Evidence | Media
    properties: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    """Edge representation in investigation relationship graph."""

    source: str
    target: str
    relationship: str  # CONTAINS | PUBLISHED_BY | WRITTEN_BY | SUPPORTS | CONTRADICTING | REFERENCES | SIMILAR_TO | MATCHES
    weight: float = 1.0


class InvestigationGraph(BaseModel):
    """Complete investigation evidence graph representation."""

    nodes: list[GraphNode]
    edges: list[GraphEdge]
