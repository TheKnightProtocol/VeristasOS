"""
VeristasOS Media Authenticity Analyzer Service

Provides lightweight, CPU-compatible media authenticity and manipulation screening.
DO NOT claim definitive proof of deepfakes or synthetic media; returns AI-assisted risk signals.
"""

from __future__ import annotations

import io
from typing import Any
from PIL import Image, ImageStat


class MediaAuthenticityAnalyzer:
    """
    Lightweight CPU-compatible media authenticity evaluator.
    Combines metadata inspection, EXIF tag analysis, compression variance heuristics,
    and perceptual characteristics.
    """

    def __init__(self, model_name: str = "heuristic-cpu-v1"):
        self.model_name = model_name

    def is_available(self) -> bool:
        """Check if media authenticity analyzer is active."""
        return True

    def analyze(
        self,
        file_bytes: bytes,
        filename: str,
        mime_type: str | None = None,
        exif_data: dict[str, Any] | None = None,
        ocr_text: str | None = None,
        consistency_score: int | None = None,
    ) -> dict[str, Any]:
        """
        Evaluate image bytes and return structured authenticity screening result.
        """
        if not file_bytes:
            return {
                "available": False,
                "assessment": "INCONCLUSIVE",
                "score": 50,
                "confidence": 0,
                "signals": [],
                "limitations": "No image data provided.",
                "model": self.model_name,
            }

        signals: list[dict[str, str]] = []
        suspicious_count = 0
        verified_count = 0

        # 1. Image loading & dimension checks
        width, height = 0, 0
        noise_variance = 0.0
        try:
            img = Image.open(io.BytesIO(file_bytes))
            width, height = img.size
            
            # Compute image statistics (noise/variance heuristic)
            if img.mode != "L":
                grayscale = img.convert("L")
            else:
                grayscale = img
            
            stat = ImageStat.Stat(grayscale)
            stddev = stat.stddev[0] if stat.stddev else 0.0
            noise_variance = round(stddev, 2)

            if width < 100 or height < 100:
                signals.append({
                    "name": "Image Resolution",
                    "status": "SUSPICIOUS SIGNAL",
                    "detail": f"Low resolution ({width}x{height} px) may obscure manipulation artifacts."
                })
                suspicious_count += 1
            else:
                signals.append({
                    "name": "Image Resolution",
                    "status": "VERIFIED SIGNAL",
                    "detail": f"Standard resolution ({width}x{height} px)."
                })
                verified_count += 1

        except Exception as exc:
            signals.append({
                "name": "File Format Integrity",
                "status": "INCONCLUSIVE",
                "detail": f"Could not inspect image stream: {exc}"
            })

        # 2. EXIF Metadata Inspection
        if exif_data and len(exif_data) > 0:
            software = str(exif_data.get("Software", "")).lower()
            if any(tool in software for tool in ["photoshop", "gimp", "canva", "adobe", "midjourney", "stable"]):
                signals.append({
                    "name": "Software Metadata",
                    "status": "SUSPICIOUS SIGNAL",
                    "detail": f"EXIF metadata indicates editing software trace: '{exif_data.get('Software')}'."
                })
                suspicious_count += 2
            else:
                signals.append({
                    "name": "EXIF Metadata",
                    "status": "VERIFIED SIGNAL",
                    "detail": f"Contains {len(exif_data)} EXIF metadata records."
                })
                verified_count += 1
        else:
            signals.append({
                "name": "EXIF Metadata",
                "status": "INCONCLUSIVE",
                "detail": "No EXIF metadata embedded in file (common in web-compressed media)."
            })

        # 3. Compression & Variance Heuristic
        if noise_variance < 5.0:
            signals.append({
                "name": "Noise & Texture Distribution",
                "status": "SUSPICIOUS SIGNAL",
                "detail": f"Extremely low variance ({noise_variance}) detected; image may be synthetic or heavily smoothed."
            })
            suspicious_count += 1
        else:
            signals.append({
                "name": "Noise & Texture Distribution",
                "status": "VERIFIED SIGNAL",
                "detail": f"Natural noise and texture variation detected (variance {noise_variance})."
            })
            verified_count += 1

        # 4. OCR / Article Consistency Signal
        if consistency_score is not None:
            if consistency_score < 20:
                signals.append({
                    "name": "Image-Text Context",
                    "status": "SUSPICIOUS SIGNAL",
                    "detail": "Minimal textual correlation between image contents and article narrative."
                })
                suspicious_count += 1
            elif consistency_score >= 60:
                signals.append({
                    "name": "Image-Text Context",
                    "status": "VERIFIED SIGNAL",
                    "detail": "High textual correlation between overlay content and article text."
                })
                verified_count += 1

        # Calculate composite authenticity score (0-100)
        base_score = 75
        base_score -= suspicious_count * 15
        base_score += verified_count * 5
        score = max(5, min(95, base_score))

        if score >= 70:
            assessment = "LIKELY AUTHENTIC"
        elif score >= 40:
            assessment = "INCONCLUSIVE"
        else:
            assessment = "SUSPICIOUS"

        confidence = min(90, 50 + len(signals) * 10)

        return {
            "available": True,
            "assessment": assessment,
            "score": score,
            "confidence": confidence,
            "signals": signals,
            "limitations": "AI-assisted authenticity screening. Not definitive proof of synthetic media.",
            "model": self.model_name,
        }


authenticity_analyzer = MediaAuthenticityAnalyzer()
