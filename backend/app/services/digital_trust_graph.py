"""
VeristasOS Digital Trust Graph Engine

Architectural core connecting interaction inputs, language/intent, extracted signals,
Scam DNA fingerprints, composite risk engine, and recommended actions.
"""

from __future__ import annotations

from typing import Any


def build_digital_trust_graph(
    text: str,
    language_info: dict[str, Any],
    scam_dna: dict[str, Any],
    privacy_info: dict[str, Any],
    risk_level: str,
    recommended_actions: list[str],
) -> dict[str, Any]:
    """
    Construct nodes and edges representing the Digital Trust Graph for visual inspection.
    """
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    # 1. Root Interaction Node
    nodes.append({
        "id": "node_input",
        "type": "Interaction",
        "label": "Digital Interaction Input",
        "properties": {"snippet": (text[:40] + "...") if len(text) > 40 else text}
    })

    # 2. Language & Intent Node
    nodes.append({
        "id": "node_lang",
        "type": "LanguageIntent",
        "label": f"Language: {language_info.get('language', 'English')}",
        "properties": {"intent": language_info.get("intent", "General Query")}
    })
    edges.append({
        "source": "node_input",
        "target": "node_lang",
        "relationship": "EXTRACTED_INTENT"
    })

    # 3. Scam DNA Profile Node
    nodes.append({
        "id": "node_dna",
        "type": "ScamDNA",
        "label": f"Scam DNA Profile ({scam_dna.get('primary_pattern', 'Standard')})",
        "properties": {"urgency": scam_dna.get("urgency_score", 0), "credential_request": scam_dna.get("credential_request_score", 0)}
    })
    edges.append({
        "source": "node_input",
        "target": "node_dna",
        "relationship": "DNA_FINGERPRINT"
    })

    # 4. Sensitive Data Node (if privacy signals exist)
    if privacy_info.get("sensitive_data_detected", 0) > 0:
        nodes.append({
            "id": "node_privacy",
            "type": "PrivacyShield",
            "label": f"Sensitive Data ({privacy_info['sensitive_data_detected']} Items)",
            "properties": {"types": privacy_info.get("detected_types", [])}
        })
        edges.append({
            "source": "node_input",
            "target": "node_privacy",
            "relationship": "EXPOSES_DATA"
        })

    # 5. Unified Risk Node
    nodes.append({
        "id": "node_risk",
        "type": "UnifiedRisk",
        "label": f"Risk Level: {risk_level}",
        "properties": {"risk_level": risk_level}
    })
    edges.append({"source": "node_dna", "target": "node_risk", "relationship": "EVALUATES_RISK"})
    edges.append({"source": "node_lang", "target": "node_risk", "relationship": "INFORMS_RISK"})

    # 6. Recommended Action Node
    first_action = recommended_actions[0] if recommended_actions else "Verify through official application"
    nodes.append({
        "id": "node_action",
        "type": "RecommendedAction",
        "label": f"Action: {first_action[:30]}...",
        "properties": {"action": first_action}
    })
    edges.append({
        "source": "node_risk",
        "target": "node_action",
        "relationship": "RECOMMENDS_ACTION"
    })

    return {
        "graph_type": "Digital Trust Graph",
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
    }
