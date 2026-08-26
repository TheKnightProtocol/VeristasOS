"""
VeristasOS Deepfake & Media Manipulation Detector Service

Provides a lightweight, CPU-compatible forensic risk estimation interface for image media.
Can be toggled via environment variable DEEPFAKE_ENABLED (default: false).

DO NOT claim definitive proof of synthetic media; returns AI-assisted risk signals.
"""

from __future__ import annotations

import io
import os
from typing import Any
from PIL import Image, ImageStat


class DeepfakeDetector:
    """
    Modular, pluggable media manipulation and deepfake risk analyzer.
    Executes lightweight CPU-compatible forensic heuristics.
    """

    def __init__(self, default_model: str = "lightweight-forensic-analysis"):
        self.default_model = default_model

    def is_enabled(self) -> bool:
        """Return True if deepfake detection is enabled via DEEPFAKE_ENABLED env var."""
        env_val = os.getenv("DEEPFAKE_ENABLED", "false").lower()
        return env_val in ("true", "1", "yes", "on")

    def analyze_media(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str | None = None,
        exif_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze image bytes for manipulation and synthetic media indicators.
        """
        enabled = self.is_enabled()

        if not enabled:
            return {
                "available": False,
                "media_type": "image",
                "deepfake_risk": 0,
                "manipulation_risk": 0,
                "confidence": 0,
                "signals": [],
                "explanation": "Deepfake analysis module is disabled by default in current production config.",
                "model": self.default_model,
            }

        if not file_bytes:
            return {
                "available": True,
                "media_type": "image",
                "deepfake_risk": 0,
                "manipulation_risk": 0,
                "confidence": 0,
                "signals": [],
                "explanation": "Empty image payload submitted.",
                "model": self.default_model,
            }

        signals: list[dict[str, Any]] = []
        manipulation_score = 15
        deepfake_score = 10

        # 1. Inspection of pixel texture & stddev noise
        try:
            img = Image.open(io.BytesIO(file_bytes))
            grayscale = img.convert("L") if img.mode != "L" else img
            stat = ImageStat.Stat(grayscale)
            stddev = stat.stddev[0] if stat.stddev else 0.0

            if stddev < 5.0:
                manipulation_score += 30
                deepfake_score += 25
                signals.append({
                    "signal": "Texture Uniformity",
                    "score": 80,
                    "detail": f"Unusually smooth variance ({stddev:.2f}) detected, typical of synthetic image generation or heavy smoothing filters."
                })
            else:
                signals.append({
                    "signal": "Texture Variance",
                    "score": 15,
                    "detail": f"Natural noise and texture variation detected (variance {stddev:.2f})."
                })

            # 2. Resampling & Resolution Artifacts
            w, h = img.size
            if w < 120 or h < 120:
                manipulation_score += 15
                signals.append({
                    "signal": "Resolution Artifacts",
                    "score": 60,
                    "detail": "Low resolution image limits sub-pixel forgery detection accuracy."
                })
            elif w % 16 != 0 or h % 16 != 0:
                signals.append({
                    "signal": "Compression Grid",
                    "score": 20,
                    "detail": "Non-standard grid dimensions detected."
                })

        except Exception as exc:
            signals.append({
                "signal": "Stream Integrity",
                "score": 50,
                "detail": f"Forensic stream inspection note: {exc}"
            })

        # 3. EXIF Software Header Tags
        if exif_data:
            software = str(exif_data.get("Software", "")).lower()
            if any(tool in software for tool in ["photoshop", "gimp", "canva", "adobe", "midjourney", "stable"]):
                manipulation_score += 35
                signals.append({
                    "signal": "Editing Software Trace",
                    "score": 85,
                    "detail": f"EXIF metadata indicates software trace: '{exif_data.get('Software')}'."
                })
            else:
                signals.append({
                    "signal": "EXIF Camera Headers",
                    "score": 10,
                    "detail": f"Standard metadata tags present ({len(exif_data)} tags)."
                })

        deepfake_risk = max(0, min(100, deepfake_score))
        manipulation_risk = max(0, min(100, manipulation_score))
        confidence = min(85, 40 + len(signals) * 10)

        return {
            "available": True,
            "media_type": "image",
            "deepfake_risk": deepfake_risk,
            "manipulation_risk": manipulation_risk,
            "confidence": confidence,
            "signals": signals,
            "explanation": "This is an AI-assisted forensic risk estimate, not definitive proof of synthetic media.",
            "model": self.default_model,
        }


deepfake_detector = DeepfakeDetector()
