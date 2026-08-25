from typing import Any


def _risk_level(score: float) -> str:
    if score < 25:
        return "Low"
    if score < 55:
        return "Moderate"
    return "High"


def _verdict(score: float) -> str:
    if score < 25:
        return "Likely Reliable"
    if score < 55:
        return "Needs Verification"
    return "High Risk"


def _credibility(score: float) -> float:
    return round(max(0.0, min(100.0, 100.0 - score)), 2)


def _build_signals(analysis: dict[str, Any]) -> list[str]:
    signals: list[str] = []

    if analysis["exclamation_count"] > 0:
        signals.append(
            f"{analysis['exclamation_count']} exclamation mark(s) detected"
        )

    if analysis["question_count"] > 0:
        signals.append(
            f"{analysis['question_count']} question mark(s) detected"
        )

    if analysis["uppercase_word_count"] > 0:
        signals.append(
            f"{analysis['uppercase_word_count']} uppercase word(s) detected"
        )

    if analysis["sensational_word_count"] > 0:
        words = ", ".join(
            analysis["sensational_words"][:5]
        )
        signals.append(
            f"Sensational vocabulary detected: {words}"
        )

    if analysis["repeated_word_ratio"] > 0:
        signals.append(
            "Repeated-word pattern detected"
        )

    if not signals:
        signals.append(
            "No major sensationalism indicators detected"
        )

    return signals


def analyze_content(
    analysis: dict[str, Any],
) -> dict[str, Any]:

    score = float(
        analysis.get(
            "sensationalism_score",
            0.0,
        )
    )

    return {
        "verdict": _verdict(score),
        "risk_level": _risk_level(score),
        "credibility_score": _credibility(score),
        "sensationalism_score": score,
        "signals": _build_signals(analysis),
        "disclaimer": (
            "This is a linguistic risk assessment, not a factual "
            "verification of the claims in the content."
        ),
    }
