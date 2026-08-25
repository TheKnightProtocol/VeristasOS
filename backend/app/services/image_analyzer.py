"""
VeristasOS Image & Media Analysis Service

Performs image file inspection, metadata extraction, cryptographic hashing,
perceptual difference hashing, graceful OCR text extraction, and media-text consistency analysis.

DO NOT claim deepfake detection.
"""

from __future__ import annotations

import hashlib
import io
from typing import Any
from PIL import Image


def analyze_image_bytes(
    file_bytes: bytes,
    filename: str,
    content_type: str | None = None,
) -> dict[str, Any]:
    """
    Inspect raw image bytes and extract structural metadata, SHA256, perceptual hash,
    and OCR text if available.
    """
    size_bytes = len(file_bytes)
    sha256_hash = hashlib.sha256(file_bytes).hexdigest()

    width = 0
    height = 0
    mime_type = content_type or "image/unknown"
    perceptual_hash = "N/A"
    ocr_text = ""

    try:
        img = Image.open(io.BytesIO(file_bytes))
        width, height = img.size
        mime_type = Image.MIME.get(img.format, content_type or "image/unknown")

        # Compute a simple perceptual hash (Difference Hash / dHash)
        perceptual_hash = compute_dhash(img)

        # Attempt OCR text extraction
        ocr_text = extract_ocr(img)

    except Exception as exc:
        ocr_text = f"Image processing note: {exc}"

    return {
        "filename": filename,
        "mime_type": mime_type,
        "size_bytes": size_bytes,
        "width": width,
        "height": height,
        "sha256": sha256_hash,
        "perceptual_hash": perceptual_hash,
        "ocr_text": ocr_text,
    }


def compute_dhash(image: Image.Image, hash_size: int = 8) -> str:
    """
    Calculate a simple 64-bit difference hash (dHash) for an image.
    """
    try:
        # Convert image to grayscale and resize to (hash_size + 1, hash_size)
        resized = image.convert("L").resize(
            (hash_size + 1, hash_size),
            Image.Resampling.BILINEAR if hasattr(Image, "Resampling") else Image.BILINEAR,
        )
        pixels = list(resized.getdata())

        difference = []
        for row in range(hash_size):
            for col in range(hash_size):
                pixel_left = pixels[row * (hash_size + 1) + col]
                pixel_right = pixels[row * (hash_size + 1) + col + 1]
                difference.append(pixel_left > pixel_right)

        decimal_val = 0
        for i, val in enumerate(difference):
            if val:
                decimal_val |= 1 << i
        return f"{decimal_val:016x}"
    except Exception:
        return "0000000000000000"


def extract_ocr(image: Image.Image) -> str:
    """
    Extract text using pytesseract if available, failing gracefully if Tesseract is not installed.
    """
    try:
        import pytesseract

        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception:
        return "OCR text extraction unavailable (Tesseract binary not installed on host)."


def analyze_text_image_consistency(
    article_text: str,
    ocr_text: str,
) -> dict[str, Any]:
    """
    Compare extracted OCR text with article text to score media/text consistency.
    """
    if not ocr_text or "unavailable" in ocr_text.lower() or not article_text.strip():
        return {
            "consistency": "INCONCLUSIVE",
            "score": 50,
            "explanation": "Insufficient image OCR text to compare against article claims.",
        }

    article_words = set(re_words(article_text))
    ocr_words = set(re_words(ocr_text))

    if not ocr_words:
        return {
            "consistency": "NONE",
            "score": 0,
            "explanation": "No textual content was detected inside the provided image.",
        }

    intersection = article_words & ocr_words
    overlap_ratio = len(intersection) / float(len(ocr_words))

    if overlap_ratio >= 0.6:
        consistency = "HIGH OVERLAP"
        score = int(min(100, overlap_ratio * 100))
        explanation = "The text extracted from the image heavily aligns with terms present in the article."
    elif overlap_ratio >= 0.2:
        consistency = "PARTIAL OVERLAP"
        score = int(min(100, overlap_ratio * 100))
        explanation = "The extracted image text overlaps with some article terms but does not independently verify full narrative context."
    else:
        consistency = "LOW OVERLAP"
        score = int(overlap_ratio * 100)
        explanation = "Minimal text overlap detected between image overlay content and submitted article body."

    return {
        "consistency": consistency,
        "score": score,
        "explanation": explanation,
    }


def re_words(text: str) -> list[str]:
    import re
    return [w.lower() for w in re.findall(r"\b[a-zA-Z]{3,}\b", text)]
