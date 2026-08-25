# VeristasOS — Truth Intelligence Platform

> **Truth Intelligence Operating Environment**  
> AI-assisted misinformation analysis, source provenance scoring, image OCR inspection, and local LLM explanation.

---

## 🌟 Project Overview

**VeristasOS** is an intelligence workstation designed to analyze digital content (text, headlines, social claims, and media images) for misinformation risk signals.

Rather than claiming automated absolute truth determination, VeristasOS uses **responsible AI principles**, transparent stylometric metrics, factual claim extraction heuristics, source provenance transparency scoring, and a locally hosted LLM to provide analytical signals and actionable verification steps.

---

## 🏗️ System Architecture

```
[ User Web Dashboard / Terminal ]
               │
               ▼
[ FastAPI Application Backend ] (port 8000)
       │       │       │       │
       │       │       │       └─────► [ Image & Media Analyzer ] (Pillow, Hashing, OCR)
       │       │       └─────────────► [ Source Provenance Engine ]
       │       └─────────────────────► [ Factual Claim Extractor ]
       │
       ├─────────────────────────────► [ Deterministic Text Analyzer ]
       │
       ▼
[ LocalAIRouter Gateway ]
       │
       ▼ (HTTP POST /completion)
[ llama.cpp llama-server ] (port 8080)
       │
       ▼
[ Qwen2.5 3B Instruct GGUF Model ] (Local GPU/CPU Inference)
```

---

## ✨ Features

- **Unified Analysis Engine**: Aggregates stylometric signals, claim density, source risk, and AI reasoning into an overall risk score (0–100) and classification (`LOW RISK`, `MODERATE RISK`, `HIGH RISK`, `VERY HIGH RISK`).
- **Local AI Explanation**: Powered by `Qwen2.5 3B Instruct` via `llama.cpp` at `http://127.0.0.1:8080`. No cloud APIs or internet required for AI inference. Gracefully falls back if offline.
- **Factual Claim Extraction**: Automatically parses declarative sentences, numerical figures, and named entity patterns into structured claim cards tagged with `UNVERIFIED`.
- **Source & Provenance Evaluation**: Computes provenance transparency scores based on metadata (URL, publisher, author, date) and clearly distinguishes user-provided metadata from independent verification.
- **Media & Image OCR Analysis**: Extracts EXIF dimensions, MIME types, SHA256 hashes, perceptual difference hashes (dHash), and OCR text overlay with image-text consistency scoring.
- **Cyberpunk Operating Interface**: Glassmorphism dark terminal UI with live system status pills (`SYSTEM STATUS`, `LOCAL AI STATUS`, `ANALYSIS STATUS`), scanning effects, responsive layout (320px+).
- **Interactive VeristasOS Shell**: Embedded terminal shell supporting interactive command execution with automated AI failure diagnosis (`WHY / FIX / NOTE`).
- **Built-in Demo Cases**: 3 labeled pre-set scenarios (`High-Risk Sensational`, `Low-Risk News`, `Misleading Claim`).
- **Session History & Export**: Browser `localStorage` analysis history and downloadable/printable HTML report generation (`EXPORT ANALYSIS`).
- **Mandatory Ethical Disclaimer**: Prominently highlights analytical limits and encourages primary source verification.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12, FastAPI, Uvicorn, Pydantic, Pillow, NLTK
- **Local AI Inference**: `llama.cpp` (`llama-server.exe`) running `Qwen2.5-3B-Instruct-GGUF` (Q4_K_M)
- **Frontend**: Vanilla HTML5, CSS3 (Cyberpunk Design System), JavaScript (ES6 fetch API, LocalStorage)
- **Testing**: Pytest, FastAPI TestClient

---

## 🚀 Quick Start (Windows PowerShell)

### 1. Prerequisites
- Python 3.10+ installed on Windows.
- Local `llama.cpp` server (optional, for LLM explanations):
  - Model: `Qwen2.5 3B Instruct GGUF`
  - Host: `http://127.0.0.1:8080`

### 2. Launch using One-Terminal Script
From the project root `D:\FakeNewsDetection`:

```powershell
.\run_veristasos.ps1
```

This launcher will:
1. Verify the Python virtual environment (`.\venv`).
2. Test reachability of the local llama.cpp server.
3. Start the FastAPI server on `http://127.0.0.1:8000`.
4. Provide immediate browser access links.

---

## 📡 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves VeristasOS Cyberpunk Web Interface |
| `GET` | `/health` | Backend status check |
| `GET` | `/api` | Service capabilities & registry |
| `GET` | `/api/ai/status` | Live status of local llama.cpp Qwen model |
| `POST` | `/analyze` | Unified text & risk intelligence analysis |
| `POST` | `/api/analyze` | Unified text & risk intelligence analysis (alias) |
| `POST` | `/api/analyze-image` | Multipart image upload for EXIF, hashing, OCR & consistency |
| `GET` | `/docs` | Interactive Swagger API documentation |

### Example Unified Request (`POST /api/analyze`)

```json
{
  "text": "BREAKING NEWS! Shocking miracle discovery announced today! YOU WON'T BELIEVE THIS!",
  "source_url": "https://example.com/breaking",
  "source_name": "Daily Buzz Wire"
}
```

### Example Unified Response

```json
{
  "status": "success",
  "service": "VeristasOS",
  "version": "1.0.0",
  "analysis": {
    "overall_risk_score": 78.5,
    "classification": "HIGH RISK",
    "confidence": 85.0,
    "sensationalism_score": 84.0,
    "claims": [
      {
        "claim": "Shocking miracle discovery announced today!",
        "type": "factual",
        "verification_status": "unverified"
      }
    ],
    "indicators": [
      {
        "indicator": "Excessive sensational language",
        "severity": "HIGH",
        "reason": "Detected sensational words (breaking, shocking, miracle)."
      }
    ],
    "ai_analysis": {
      "available": true,
      "summary": "Content exhibits high stylometric sensationalism and emotional manipulation."
    },
    "provenance": {
      "source_available": true,
      "source_name": "Daily Buzz Wire",
      "provenance_score": 70,
      "status": "Source information provided"
    },
    "recommendations": [
      "Cross-verify claims with reputable primary reporting outlets.",
      "Check publication date and author background credentials."
    ]
  }
}
```

---

## 🧪 Testing

Execute the complete Pytest test suite:

```powershell
.\venv\Scripts\python.exe -m pytest backend/tests
```

All 24 automated unit and integration tests cover `/health`, `/api`, `/api/ai/status`, `/analyze`, `/api/analyze-image`, claim extraction, provenance evaluation, risk calculation, and AI fallback behavior.

---

## ⚠️ Limitations & Ethical Disclaimer

> **DISCLAIMER**: VeristasOS provides AI-assisted risk indicators and analytical signals. It does not independently establish whether a claim is true or false. Users should verify important claims using reliable primary sources.
