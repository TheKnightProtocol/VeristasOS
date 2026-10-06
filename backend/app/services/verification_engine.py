"""
VeristasOS Master Verification Engine — Dual-Layer Aggregator

Combines Layer 1 (PRIVACY SHIELD) and Layer 2 (TRUTH & INTEGRITY ENGINE) signals
into a single, structured, transparent assessment payload for UI and API consumption.
"""

from __future__ import annotations

import os
from typing import Any

from app.services.text_analyzer import analyze_text
from app.services.privacy_scanner import scan_privacy_signals
from app.services.scam_detector import detect_scam_signals
from app.services.explainability import generate_explainability_matrix
from app.services.provenance import analyze_provenance


def run_dual_layer_verification(
    text: str,
    source_url: str | None = None,
    source_name: str | None = None,
    author: str | None = None,
    publication_date: str | None = None,
    image_analysis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Execute complete VeristasOS dual-layer verification pipeline.
    """
    clean_text = (text or "").strip()

    # 1. Layer 1: Privacy Shield Analysis
    privacy_res = scan_privacy_signals(clean_text)
    scam_res = detect_scam_signals(clean_text)

    # 2. Layer 2: Truth & Integrity Analysis
    linguistic_res = analyze_text(clean_text) if clean_text else {
        "sensationalism_score": 0, "sensational_words": [], "uppercase_word_count": 0, "exclamation_count": 0
    }

    provenance_res = analyze_provenance(
        source_url=source_url,
        source_name=source_name,
        author=author,
        publication_date=publication_date,
    )

    explainability_res = generate_explainability_matrix(
        text_analysis=linguistic_res,
        privacy_analysis=privacy_res,
        scam_analysis=scam_res,
        provenance_analysis=provenance_res,
    )

    # 3. Composite Risk Calculation & Truth Meter State
    sensational_score = linguistic_res.get("sensationalism_score", 0)
    scam_score = scam_res.get("scam_score", 0)
    sensitive_count = privacy_res.get("sensitive_data_detected", 0)

    composite_score = int(0.4 * sensational_score + 0.4 * scam_score + min(100, sensitive_count * 25) * 0.2)

    reasons: list[str] = []

    if sensitive_count > 0:
        reasons.append(f"Sensitive information request detected ({', '.join(privacy_res['detected_types'])})")
    if scam_score >= 40:
        reasons.append(f"Scam Radar Trigger: {scam_res['explanation']}")
    if sensational_score > 35:
        reasons.append(f"Elevated sensationalism detected ({sensational_score:.1f}/100)")
    if not source_name and not source_url:
        reasons.append("Source verification pending (No publisher/URL provided)")

    if not reasons:
        reasons.append("Linguistic and privacy signals align with standard neutral content.")

    # Determine Truth Meter Status
    if composite_score >= 75 or sensitive_count >= 3:
        truth_status = "CRITICAL WARNING"
        risk_level = "CRITICAL"
    elif composite_score >= 50 or scam_score >= 40:
        truth_status = "SUSPICIOUS"
        risk_level = "HIGH"
    elif composite_score >= 25 or sensational_score > 30 or sensitive_count >= 1:
        truth_status = "NEEDS VERIFICATION"
        risk_level = "MODERATE"
    else:
        truth_status = "LIKELY RELIABLE"
        risk_level = "LOW"

    # Check Local AI Engine availability
    local_ai_active = False
    try:
        from app.ai.router import LocalAIRouter
        local_ai_active = LocalAIRouter().is_available()
    except Exception:
        local_ai_active = False

    return {
        "truth_status": truth_status,
        "risk_level": risk_level,
        "composite_risk_score": composite_score,
        "reasons": reasons,
        "explanation": (
            f"Based on available signals: {truth_status}. "
            f"{'Sensitive data patterns identified. ' if sensitive_count > 0 else ''}"
            f"Source verification recommended."
        ),
        "local_ai_status": {
            "available": local_ai_active,
            "label": "● Local model available" if local_ai_active else "○ Local model not configured",
            "provider": "llama.cpp (Qwen2.5-3B)" if local_ai_active else "Deterministic Heuristics Engine",
        },

        # LAYER 2 — TRUTH & INTEGRITY ENGINE
        "truth_and_integrity": {
            "truth_meter_status": truth_status,
            "linguistic_risk": "HIGH" if sensational_score > 60 else ("MODERATE" if sensational_score > 30 else "LOW"),
            "sensationalism_score": sensational_score,
            "sensational_words": linguistic_res.get("sensational_words", []),
            "linguistic_metrics": linguistic_res,
            "explainability": explainability_res,
            "provenance": provenance_res,
            "media_consistency": image_analysis.get("authenticity_screening") if image_analysis else "NOT ANALYZED",
        },

        # LAYER 1 — PRIVACY SHIELD
        "privacy_shield": {
            "privacy_grade": privacy_res["privacy_grade"],
            "privacy_risk": privacy_res["privacy_risk"],
            "sensitive_data_detected": sensitive_count,
            "detected_types": privacy_res["detected_types"],
            "detected_items": privacy_res["detected_items"],
            "masked_text": privacy_res["masked_text"],
            "scam_radar": scam_res,
            "tracker_protection": "Prototype — Requires browser extension integration for live network analysis",
        },
    }
