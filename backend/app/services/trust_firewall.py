"""
Trust Firewall Service for VeristasOS — Your AI Saathi.
Evaluates proposed AI actions against:
1. Content Risk (Sensationalism, Urgency, Threats)
2. Privacy Risk (PII leakage, Aadhaar/PAN/UPI/OTP)
3. Financial / Scam Risk (Scam DNA 5-part profile)
4. Prompt Injection Defense (Adversarial override detection)
5. Model Reliability (Confidence, Uncertainty, Evidence Quality)
6. User Policy (LOW, MEDIUM, HIGH risk permission rules)

Outputs: ALLOW | ASK_USER | BLOCK with WHY → EVIDENCE → CONFIDENCE → RELIABILITY → ACTION framework.
"""

from typing import Dict, Any, List
from .text_analyzer import analyze_text
from .privacy_scanner import scan_privacy_signals
from .scam_dna import generate_scam_dna
from .bharat_language_engine import analyze_bharat_language
from .reliability_engine import ModelReliabilityEngine
from .policy_engine import UserPolicyEngine
from .prompt_defense import PromptInjectionDefense


class TrustFirewall:
    def __init__(self, user_mode: str = "Adult"):
        self.reliability_engine = ModelReliabilityEngine()
        self.policy_engine = UserPolicyEngine(mode=user_mode)
        self.prompt_defense = PromptInjectionDefense()

    def set_user_mode(self, mode: str):
        self.policy_engine.set_mode(mode)

    def evaluate_proposed_action(
        self,
        action_name: str,
        content: str,
        trusted_context: str = ""
    ) -> Dict[str, Any]:
        """
        Evaluates a proposed action and content through the complete Trust Firewall gate.
        Returns final decision (ALLOW, ASK_USER, BLOCK) along with explainability data.
        """
        content = content or ""
        
        # 1. Prompt Injection Defense Scan
        injection_res = self.prompt_defense.scan_untrusted_content(content)
        
        # 2. Layer 1 Privacy Shield Scan
        privacy_res = scan_privacy_signals(content)
        privacy_leak_detected = privacy_res.get("sensitive_data_detected", 0) > 0
        
        # 3. Content Sensationalism Scan
        text_core_res = analyze_text(content)
        
        # 4. Scam DNA Threat Fingerprinting
        scam_dna_res = generate_scam_dna(content)
        
        # 5. Bharat Language Intent Scan
        bharat_res = analyze_bharat_language(content)
        
        # Build signals container
        signals = {
            "sensationalism_score": text_core_res.get("sensationalism_score", 0),
            "privacy_leak_detected": privacy_leak_detected,
            "scam_dna": scam_dna_res,
            "bharat_intent": bharat_res,
            "injection_detected": injection_res.get("injection_detected", False)
        }

        # Determine overall Risk Level
        risk_reasons: List[str] = []
        evidence_items: List[str] = []
        
        if injection_res.get("injection_detected"):
            risk_reasons.append("Adversarial prompt injection attempt detected.")
            evidence_items.append(f"Prompt override pattern: '{injection_res.get('pattern_matched')}'")
            
        if privacy_leak_detected:
            found_types = privacy_res.get("detected_types", [])
            risk_reasons.append(f"Sensitive Indian PII requested/detected: {', '.join(found_types)}.")
            evidence_items.append(f"Redacted count: {privacy_res.get('sensitive_data_detected', 0)} item(s)")


        if scam_dna_res.get("threat_detected"):
            top_vector = scam_dna_res.get("top_attack_vector", "Suspicious Pattern")
            risk_reasons.append(f"Scam DNA threat pattern detected ({top_vector}).")
            evidence_items.append(f"Scam DNA Score: {scam_dna_res.get('composite_scam_score', 0)}/100")
            
        sensationalism = text_core_res.get("sensationalism_score", 0)
        if sensationalism > 50:
            risk_reasons.append("High sensationalism and emotional manipulation language detected.")
            evidence_items.append(f"Sensationalism Score: {sensationalism}/100")

        # Determine composite risk level
        if injection_res.get("injection_detected") or privacy_res.get("leak_detected") or scam_dna_res.get("composite_scam_score", 0) >= 65:
            composite_risk_level = "CRITICAL"
        elif scam_dna_res.get("composite_scam_score", 0) >= 40 or sensationalism > 40:
            composite_risk_level = "HIGH"
        elif sensationalism > 20 or scam_dna_res.get("composite_scam_score", 0) > 15:
            composite_risk_level = "CAUTION"
        else:
            composite_risk_level = "LOW"
            if not risk_reasons:
                risk_reasons.append("No significant threat signals detected in input content.")
                evidence_items.append("Linguistic, privacy, and scam indicators within safe thresholds.")

        # 6. Model Reliability Engine Evaluation
        base_confidence = 0.90 if composite_risk_level in ["CRITICAL", "LOW"] else 0.75
        reliability_res = self.reliability_engine.evaluate_reliability(
            prediction=composite_risk_level,
            base_confidence=base_confidence,
            signals=signals,
            raw_input=content
        )

        # 7. User Policy Engine Permission Check
        policy_res = self.policy_engine.evaluate_action_permission(
            action_name=action_name,
            risk_level=composite_risk_level,
            signals=signals
        )

        if policy_res.get("permission") == "BLOCKED":
            if not risk_reasons or risk_reasons == ["No significant threat signals detected in input content."]:
                risk_reasons = [f"High-risk action '{action_name}' violates autonomous execution safety policy."]

        # 8. Master Firewall Decision Gate
        if injection_res.get("injection_detected"):
            final_decision = "BLOCK"
            decision_reason = "Action BLOCKED due to adversarial prompt injection security threat."
        elif policy_res.get("permission") == "BLOCKED" or composite_risk_level in ["HIGH", "CRITICAL"]:
            final_decision = "BLOCK"
            decision_reason = policy_res.get("reason", "Action BLOCKED by security policy.")

        elif policy_res.get("permission") == "REQUIRES_USER_APPROVAL":
            final_decision = "ASK_USER"
            decision_reason = "Action requires explicit user confirmation before execution."
        else:
            final_decision = "ALLOW"
            decision_reason = "Action meets safety criteria and is allowed for auto-execution."

        # 9. Recommended Action Advice
        if final_decision == "BLOCK":
            recommended_action = "Do NOT open links, share OTPs, or process requests. Block and report sender."
        elif final_decision == "ASK_USER":
            recommended_action = "Review details carefully before approving this action."
        else:
            recommended_action = "Safe to proceed with automated processing."

        return {
            "decision": final_decision,
            "action_name": action_name,
            "risk_level": composite_risk_level,
            "decision_reason": decision_reason,
            "why": risk_reasons,
            "evidence": evidence_items,
            "confidence_percent": reliability_res.get("confidence_percent", 85),
            "confidence_score": reliability_res.get("confidence_score", 0.85),
            "uncertainty": reliability_res.get("uncertainty", "LOW"),
            "reliability": reliability_res.get("reliability", "HIGH"),
            "evidence_quality": reliability_res.get("evidence_quality", "MEDIUM"),
            "recommended_action": recommended_action,
            "hinglish_advice": bharat_res.get("hinglish_advice", ""),
            "senior_notice": policy_res.get("senior_notice"),
            "prompt_injection_status": injection_res,
            "privacy_status": privacy_res,
            "scam_dna": scam_dna_res,
            "policy": policy_res,
            "honest_label": "Trust Firewall Gatekeeper (Rule-assisted + Heuristic Reliability)"
        }
