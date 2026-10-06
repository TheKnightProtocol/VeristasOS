"""
VeristasOS Trust Lens Engine — Unified Master Engine

Synthesizes Text Core, Privacy Shield, Scam DNA, Bharat Language Safety,
and Digital Trust Graph into the unified WHY → RISK → ACTION decision schema.
"""

from __future__ import annotations

from typing import Any

from app.services.text_analyzer import analyze_text
from app.services.privacy_scanner import scan_privacy_signals
from app.services.scam_detector import detect_scam_signals
from app.services.scam_dna import generate_scam_dna
from app.services.bharat_language_engine import analyze_bharat_language
from app.services.digital_trust_graph import build_digital_trust_graph
from app.services.explainability import generate_explainability_matrix
from app.services.provenance import analyze_provenance


def analyze_trust_lens(
    text: str,
    source_url: str | None = None,
    source_name: str | None = None,
    image_analysis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Execute complete Trust Lens pipeline and generate WHY → RISK → ACTION output.
    """
    clean_text = (text or "").strip()

    # 1. Component Extractors
    lang_info = analyze_bharat_language(clean_text)
    scam_dna = generate_scam_dna(clean_text)
    privacy_info = scan_privacy_signals(clean_text)
    scam_info = detect_scam_signals(clean_text)
    text_info = analyze_text(clean_text) if clean_text else {
        "sensationalism_score": 0, "sensational_words": [], "uppercase_word_count": 0, "exclamation_count": 0
    }

    prov_info = analyze_provenance(source_url=source_url, source_name=source_name)
    explain_info = generate_explainability_matrix(
        text_analysis=text_info,
        privacy_analysis=privacy_info,
        scam_analysis=scam_info,
        provenance_analysis=prov_info,
    )

    # 2. Risk Level Determination (LOW, CAUTION, HIGH, CRITICAL)
    scam_score = scam_dna["urgency_score"] + scam_dna["credential_request_score"]
    sensitive_count = privacy_info["sensitive_data_detected"]
    sensational_score = text_info.get("sensationalism_score", 0)

    if sensitive_count >= 3 or scam_dna["credential_request_score"] >= 80:
        risk_level = "CRITICAL"
    elif scam_dna["urgency_score"] >= 60 or scam_info["scam_score"] >= 50:
        risk_level = "HIGH"
    elif sensational_score >= 35 or sensitive_count >= 1:
        risk_level = "CAUTION"
    else:
        risk_level = "LOW"

    # 3. WHY (Signals) Construct
    why_signals: list[str] = []
    if scam_dna["urgency_score"] >= 50:
        why_signals.append(f"High urgency manipulation ({scam_dna['urgency_score']}% intensity)")
    if scam_dna["impersonation_score"] >= 50:
        why_signals.append(f"Authority / Bank impersonation pattern ({scam_dna['impersonation_score']}%)")
    if sensitive_count > 0:
        why_signals.append(f"Sensitive credential request ({', '.join(privacy_info['detected_types'])})")
    if scam_dna["suspicious_url_score"] > 0:
        why_signals.append("Unverified external URL link embedded")
    if sensational_score > 35:
        why_signals.append(f"Sensational wording signals ({sensational_score:.1f}/100 score)")

    if not why_signals:
        why_signals.append("No high-risk manipulation or privacy threat indicators identified.")

    # 4. RECOMMENDED ACTION Construct
    recommended_actions: list[str] = []
    if sensitive_count > 0 or scam_dna["credential_request_score"] >= 60:
        recommended_actions.append("Do not enter OTP or UPI PIN on unverified web links")
        recommended_actions.append("Do not share Aadhaar or PAN details over unencrypted messages")
    if scam_dna["impersonation_score"] >= 50:
        recommended_actions.append("Verify account status through your official banking app")
    if scam_dna["suspicious_url_score"] > 0:
        recommended_actions.append("Do not click or open unverified external links")
    if not recommended_actions:
        recommended_actions.append("Verify claims against official news sources before forwarding")

    # 5. Build Digital Trust Graph
    graph_data = build_digital_trust_graph(
        text=clean_text,
        language_info=lang_info,
        scam_dna=scam_dna,
        privacy_info=privacy_info,
        risk_level=risk_level,
        recommended_actions=recommended_actions,
    )

    return {
        "tagline": "Your truth. Your data. Your device.",
        "risk_level": risk_level,
        "why_signals": why_signals,
        "recommended_actions": recommended_actions,
        "bharat_safety": lang_info,
        "scam_dna": scam_dna,
        "privacy_shield": privacy_info,
        "text_analysis": text_info,
        "explainability": explain_info,
        "digital_trust_graph": graph_data,
        "disclaimer": "VeristasOS provides AI-assisted risk indicators based on privacy, language, and threat signals. Always verify critical requests through official channels.",
    }
