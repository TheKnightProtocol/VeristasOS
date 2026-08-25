"""
VeristasOS Master Investigation Engine

Orchestrates complete multimodal truth-intelligence investigation pipeline:
Claims + Semantic Evidence + Source Intelligence + Provenance + Correlation + AI Explanation + Evidence Graph.
"""

from __future__ import annotations

import uuid
from typing import Any

from app.models.schemas import UnifiedAnalyzeRequest, GraphNode, GraphEdge, InvestigationGraph
from app.services.text_analyzer import analyze_text
from app.services.claim_analyzer import extract_claims
from app.services.evidence_engine import evaluate_claim_evidence
from app.services.source_intelligence import evaluate_source_intelligence
from app.services.correlation_engine import correlate_cross_source_signals
from app.services.ai_analyzer import analyze_with_ai
from app.services.risk_engine import calculate_risk
from app.services.provenance import analyze_provenance


def run_full_investigation(request: UnifiedAnalyzeRequest) -> dict[str, Any]:
    """Execute master VeristasOS investigation pipeline."""
    investigation_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
    text = request.text.strip()

    # 1. Stylometrics & Linguistic Signals
    linguistic = analyze_text(text)

    # 2. Extract Claims & Evaluate Evidence per Claim
    extracted_claims = extract_claims(text)
    claims_analysis = []
    all_evidence_matches = []

    for c in extracted_claims:
        claim_str = c.get("claim", "")
        ev_res = evaluate_claim_evidence(claim_str)
        claims_analysis.append({
            "claim": claim_str,
            "type": c.get("type", "factual"),
            "verification_status": ev_res.get("status", "UNVERIFIED"),
            "confidence": ev_res.get("confidence", 50.0),
            "summary": ev_res.get("summary", ""),
            "supporting_evidence": [e for e in ev_res.get("evidence", []) if e.get("relationship") == "SUPPORTING"],
            "contradicting_evidence": [e for e in ev_res.get("evidence", []) if e.get("relationship") == "CONTRADICTING"],
        })
        all_evidence_matches.extend(ev_res.get("evidence", []))

    # 3. Source & Provenance Intelligence
    source_intel = evaluate_source_intelligence(
        source_url=request.source_url,
        source_name=request.source_name,
        author=request.author,
        publication_date=request.publication_date,
        article_text=text,
    )

    basic_provenance = analyze_provenance(
        source_url=request.source_url,
        source_name=request.source_name,
        author=request.author,
        publication_date=request.publication_date,
    )

    # 4. Cross-Source Signal Correlation
    correlation = correlate_cross_source_signals(
        claims=claims_analysis,
        evidence_matches=all_evidence_matches,
        source_intel=source_intel,
    )

    # 5. Local Generative AI Explanation
    ai_result = analyze_with_ai(text, linguistic)

    # 6. Composite Risk Engine
    risk_output = calculate_risk(
        text_analysis=linguistic,
        claims=extracted_claims,
        provenance=basic_provenance,
        ai_analysis=ai_result,
    )

    # 7. Generate Investigation Relationship Graph
    graph = generate_investigation_graph(
        investigation_id=investigation_id,
        request=request,
        claims=claims_analysis,
        evidence_matches=all_evidence_matches,
    )

    return {
        "investigation_id": investigation_id,
        "status": "success",
        "service": "VeristasOS",
        "version": "1.0.0",
        "investigation": {
            "overall_risk_score": risk_output["overall_risk_score"],
            "classification": risk_output["classification"],
            "confidence": risk_output["confidence"],
            "sensationalism_score": linguistic["sensationalism_score"],
            "claims_count": len(claims_analysis),
            "claims": claims_analysis,
            "source_intelligence": source_intel,
            "provenance": basic_provenance,
            "correlation": correlation,
            "risk_factors": risk_output["risk_factors"],
            "indicators": risk_output["indicators"],
            "ai_analysis": ai_result,
            "recommendations": risk_output["recommendations"],
            "disclaimer": risk_output["disclaimer"],
            "graph": graph.model_dump() if hasattr(graph, "model_dump") else graph.dict(),
        },
    }


def generate_investigation_graph(
    investigation_id: str,
    request: UnifiedAnalyzeRequest,
    claims: list[dict[str, Any]],
    evidence_matches: list[dict[str, Any]],
) -> InvestigationGraph:
    """Build nodes and edges for investigation relationship graph."""
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

    # Article Node
    article_id = "node_article_root"
    nodes.append(
        GraphNode(
            id=article_id,
            label="Submitted Article",
            type="Article",
            properties={"length": len(request.text)},
        )
    )

    # Publisher / Source Node
    if request.source_name or request.source_url:
        source_id = "node_source_pub"
        nodes.append(
            GraphNode(
                id=source_id,
                label=request.source_name or "Publisher Source",
                type="Source",
                properties={"url": request.source_url or ""},
            )
        )
        edges.append(
            GraphEdge(
                source=article_id,
                target=source_id,
                relationship="PUBLISHED_BY",
                weight=1.0,
            )
        )

    # Author Node
    if request.author:
        author_id = "node_author_person"
        nodes.append(
            GraphNode(
                id=author_id,
                label=request.author,
                type="Author",
                properties={"name": request.author},
            )
        )
        edges.append(
            GraphEdge(
                source=article_id,
                target=author_id,
                relationship="WRITTEN_BY",
                weight=1.0,
            )
        )

    # Claim & Evidence Nodes
    seen_evidence = set()
    for idx, c in enumerate(claims, 1):
        claim_id = f"node_claim_{idx}"
        claim_label = f"Claim #{idx}: {c['claim'][:30]}..."
        nodes.append(
            GraphNode(
                id=claim_id,
                label=claim_label,
                type="Claim",
                properties={"text": c["claim"], "status": c["verification_status"]},
            )
        )
        edges.append(
            GraphEdge(
                source=article_id,
                target=claim_id,
                relationship="CONTAINS",
                weight=1.0,
            )
        )

        # Attach Evidence Nodes
        for ev in c.get("supporting_evidence", []):
            ev_item = ev.get("evidence", {})
            ev_id = f"node_ev_{ev_item.get('id', 'unknown')}"
            if ev_id not in seen_evidence:
                seen_evidence.add(ev_id)
                nodes.append(
                    GraphNode(
                        id=ev_id,
                        label=f"Evidence: {ev_item.get('title', 'Record')[:30]}...",
                        type="Evidence",
                        properties={"source": ev_item.get("source", "")},
                    )
                )
            edges.append(
                GraphEdge(
                    source=claim_id,
                    target=ev_id,
                    relationship="SUPPORTS",
                    weight=ev.get("similarity_score", 50.0) / 100.0,
                )
            )

        for ev in c.get("contradicting_evidence", []):
            ev_item = ev.get("evidence", {})
            ev_id = f"node_ev_{ev_item.get('id', 'unknown')}"
            if ev_id not in seen_evidence:
                seen_evidence.add(ev_id)
                nodes.append(
                    GraphNode(
                        id=ev_id,
                        label=f"Evidence: {ev_item.get('title', 'Record')[:30]}...",
                        type="Evidence",
                        properties={"source": ev_item.get("source", "")},
                    )
                )
            edges.append(
                GraphEdge(
                    source=claim_id,
                    target=ev_id,
                    relationship="CONTRADICTING",
                    weight=ev.get("similarity_score", 50.0) / 100.0,
                )
            )

    return InvestigationGraph(nodes=nodes, edges=edges)
