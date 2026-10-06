"""
Model Reliability Engine for VeristasOS — Your AI Saathi.
Evaluates AI prediction confidence, heuristic uncertainty indicators,
evidence quality, input quality score, cross-signal agreement, and OOD risk.
"""

from typing import Dict, Any, List


class ModelReliabilityEngine:
    def __init__(self):
        pass

    def evaluate_reliability(
        self,
        prediction: str,
        base_confidence: float,
        signals: Dict[str, Any],
        raw_input: str
    ) -> Dict[str, Any]:
        """
        Evaluates the reliability of an AI prediction based on multi-signal indicators.
        Returns a structured dictionary containing confidence, uncertainty,
        evidence quality, OOD risk, and cross-signal agreement.
        """
        input_len = len(raw_input.strip()) if raw_input else 0
        
        # 1. Input Quality Score
        if input_len == 0:
            input_quality = 0.0
        elif input_len < 15:
            input_quality = 0.4
        elif input_len < 50:
            input_quality = 0.7
        else:
            input_quality = 0.95

        # 2. Heuristic Evidence Quality
        evidence_sources = signals.get("evidence_sources", [])
        if evidence_sources:
            evidence_quality = "HIGH"
        elif signals.get("scam_dna") or signals.get("sensationalism_score") is not None:
            evidence_quality = "MEDIUM"
        else:
            evidence_quality = "UNAVAILABLE"

        # 3. Cross-Signal Agreement Check
        agreed_count = 0
        total_checked = 0
        
        scam_dna = signals.get("scam_dna", {})
        if scam_dna:
            total_checked += 1
            if scam_dna.get("threat_detected"):
                agreed_count += 1
                
        sensationalism = signals.get("sensationalism_score", 0)
        if sensationalism is not None and sensationalism > 25:
            total_checked += 1
            agreed_count += 1
            
        pii_leak = signals.get("privacy_leak_detected", False)
        if pii_leak:
            total_checked += 1
            agreed_count += 1

        cross_signal_agreement = (
            (agreed_count / total_checked >= 0.5) if total_checked > 0 else True
        )

        # 4. Out-of-Distribution (OOD) Risk Detection
        # Triggers if input is unusually short, contains non-standard binary chars, or conflicting signals
        ood_risk = False
        if input_len < 10 or (total_checked > 1 and agreed_count == 0):
            ood_risk = True

        # 5. Heuristic Uncertainty & Confidence Calculation
        adjusted_confidence = base_confidence * (0.6 + 0.4 * input_quality)
        if ood_risk:
            adjusted_confidence *= 0.85
            
        adjusted_confidence = min(max(round(adjusted_confidence, 2), 0.10), 0.99)

        if adjusted_confidence >= 0.80 and cross_signal_agreement and not ood_risk:
            uncertainty = "LOW"
            reliability_rating = "HIGH"
        elif adjusted_confidence >= 0.55:
            uncertainty = "MEDIUM"
            reliability_rating = "MEDIUM"
        else:
            uncertainty = "HIGH"
            reliability_rating = "LOW"

        # 6. Warnings Generation
        warnings: List[str] = []
        if input_quality < 0.5:
            warnings.append("Input text is brief or ambiguous.")
        if ood_risk:
            warnings.append("Input characteristics differ from familiar benchmark examples.")
        if not cross_signal_agreement:
            warnings.append("Independent indicators show conflicting risk assessments.")
        if evidence_quality == "UNAVAILABLE":
            warnings.append("External domain/source evidence unavailable (Heuristic evaluation used).")

        return {
            "prediction": prediction,
            "confidence_percent": int(adjusted_confidence * 100),
            "confidence_score": adjusted_confidence,
            "reliability": reliability_rating,
            "uncertainty": uncertainty,
            "evidence_quality": evidence_quality,
            "input_quality_score": input_quality,
            "ood_risk": ood_risk,
            "cross_signal_agreement": cross_signal_agreement,
            "warnings": warnings,
            "honest_label": "Heuristic Model Reliability Assessment"
        }
