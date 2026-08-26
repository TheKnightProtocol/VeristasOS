# VeristasOS — Truth Intelligence Platform

> **Multimodal AI-Assisted Misinformation Analysis, Provenance Verification, & Media Forensics Engine**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

VeristasOS is a production-grade, multimodal truth intelligence platform designed to evaluate textual claims, analyze image media metadata, calculate stylometric sensationalism risk, inspect source provenance, and perform lightweight CPU-compatible media manipulation screening. It combines deterministic NLP heuristics with optional local generative AI interpretation (Qwen2.5-3B via `llama.cpp`) to deliver structured risk assessments without making ungrounded truth claims.

---

## 1. Project Overview & Mission

In modern digital information ecosystems, sensationalism, synthetic content, and context distortion degrade public trust. VeristasOS provides developers, intelligence analysts, and researchers with an extensible framework for content verification.

The platform executes multi-stage risk evaluation:
- **Stylometric & Linguistic Analysis**: Quantifies sensationalism, exclamation density, repetition, and capital letter usage.
- **Factual Assertion Extraction**: Extracts verifiable claims from unstructured prose.
- **Source Provenance Evaluation**: Assesses domain legitimacy, author attribution, and publication metadata.
- **Media Forensics & OCR**: Computes SHA-256 cryptographic hashes, 64-bit perceptual difference hashes (`dHash`), EXIF metadata, and extracts text via OCR.
- **Media Authenticity & Deepfake Risk**: Modular CPU-compatible screening evaluating noise distribution variance, metadata anomalies, and resampling artifacts.
- **Generative AI Interpretation**: Passes structured signals to an offline LLM (`Qwen2.5-3B`) for nuanced contextual reasoning.

---

## 2. Architecture & Pipeline

```
                     [ User Input: Text / Image ]
                                  │
                                  ▼
                     [ FastAPI Unified Endpoint ]
                                  │
      ┌───────────────────────────┼───────────────────────────┐
      ▼                           ▼                           ▼
[ Text Analyzer ]         [ Claim Extraction ]     [ Provenance Engine ]
  • Sensationalism          • Factual assertions     • Publisher metadata
  • Stylometrics            • Declarative claims     • Domain verification
      │                           │                           │
      └───────────────────────────┼───────────────────────────┘
                                  │
                                  ▼
                   [ Local AI Router (Qwen 3B) ]
                     • Offline-first fallback
                     • Structured risk breakdown
                                  │
                                  ▼
                    [ Composite Risk Engine ]
                     • Weighted score (0-100)
                     • Risk classification
                     • Actionable recommendations
                                  │
                                  ▼
                    [ Cyberpunk & Light HUD UI ]
```

---

## 3. Key Features

- **Cyberpunk Dark / Light Theme System**: High-contrast cyberpunk console UI with reactive SVG radial risk gauges, horizontal neon meters, Evidence Map graph, System Console health monitor, and UTF-8 clean report export.
- **Offline-First Deterministic Fallback**: Operates at 100% functionality using linguistic heuristics even when local LLMs are unreachable.
- **Cryptographic & Perceptual Media Inspection**: Computes SHA-256 and `dHash` perceptual difference signatures to identify modified or duplicate media.
- **Lightweight CPU Deepfake Screening**: Modular architecture analyzing compression artifacts, texture noise variance, and metadata inconsistencies without requiring GPU infrastructure.
- **Full Corpus Semantic Vector Search**: Paginated TF-IDF cosine similarity search over indexed evidence repositories.
- **Safe File Upload Security**: Strict MIME-type checking, extension validation, path traversal defense, and file size caps (max 20MB).

---

## 4. Technology Stack

- **Backend**: FastAPI, Uvicorn, Pydantic v2, Python 3.12
- **Linguistic Analysis**: NLTK (Tokenization & Stylometrics), Regex
- **Vector Search & ML**: Scikit-learn (TF-IDF Vectorizer), NumPy
- **Image Processing**: Pillow (PIL), PyTesseract (Optional OCR), Hashlib
- **Local Generative AI**: `llama.cpp` HTTP server + `Qwen2.5-3B-Instruct`
- **Frontend**: Vanilla HTML5, CSS3 Custom Properties (Variables), ES6+ JavaScript, SVG Graphics
- **Testing**: Pytest, FastAPI TestClient

---

## 5. Repository Structure

```
VeristasOS/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   └── router.py              # Local llama.cpp AI gateway
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py             # Pydantic data contracts
│   │   ├── services/
│   │   │   ├── ai_analyzer.py          # Generative AI prompt construction
│   │   │   ├── claim_analyzer.py       # Factual claim extraction
│   │   │   ├── deepfake_detector.py    # Modular deepfake risk detector
│   │   │   ├── image_analyzer.py       # Image hashing, OCR, EXIF & dHash
│   │   │   ├── media_authenticity.py   # CPU authenticity analyzer
│   │   │   ├── provenance.py           # Publisher & source trust score
│   │   │   ├── risk_engine.py          # Weighted composite scoring engine
│   │   │   ├── semantic_search.py      # TF-IDF vector search & pagination
│   │   │   └── text_analyzer.py        # Stylometric sensationalism scoring
│   │   └── main.py                     # FastAPI application entry point
│   ├── tests/
│   │   ├── conftest.py                 # Pytest fixtures
│   │   └── test_api.py                 # API endpoint integration tests
│   ├── requirements.txt                # Production backend dependencies
│   └── requirements-dev.txt            # Development & testing dependencies
├── frontend/
│   ├── app.js                          # Secondary JS fallback module
│   └── index.html                      # Cyberpunk & Light UI Console
├── .dockerignore                       # Docker build exclusion patterns
├── .env.example                        # Environment variable template
├── .gitignore                          # Git exclusion rules
├── Dockerfile                          # Production multi-stage Dockerfile
├── pytest.ini                          # Pytest runner configuration
└── render.yaml                         # Render Cloud deployment specification
```

---

## 6. Local Setup & Installation

### Prerequisites
- **Python**: Version 3.12+ installed.
- **Git**: Installed and available on system PATH.

### 1. Clone the Repository
```bash
git clone https://github.com/TheKnightProtocol/VeristasOS.git
cd VeristasOS
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Production Dependencies
```bash
pip install -r backend/requirements.txt
```

---

## 7. Running the Application

### Using Uvicorn CLI
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend --reload
```

Once running, access the web platform at:
- **Frontend Console**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 8. API Endpoint Specification

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | System health check (`{"status": "ok"}`). |
| `GET` | `/api/version` | Returns service name and version. |
| `GET` | `/api` | Capability manifest and endpoint index. |
| `GET` | `/api/status` | System health and local AI connectivity status. |
| `GET` | `/api/ai/status` | Status probe for local `llama.cpp` server. |
| `GET` | `/api/media/authenticity/status` | Status probe for CPU authenticity screening engine. |
| `GET` | `/api/media/deepfake/status` | Status probe for deepfake risk detector module. |
| `GET` | `/api/search` | Paginated vector search endpoint (`q`, `limit`, `offset`, `sort_by`). |
| `POST` | `/analyze` | Primary unified text analysis pipeline. |
| `POST` | `/api/analyze` | Consistent alias for `/analyze`. |
| `POST` | `/api/ai/analyze` | Dedicated endpoint for generative AI reasoning. |
| `POST` | `/api/analyze-image` | Media forensics, perceptual hash, EXIF, & OCR endpoint. |

---

## 9. Environment Variables Reference

| Variable | Default | Description |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `production` | Runtime mode (`development` or `production`). |
| `PORT` | `8000` | HTTP server port for Uvicorn. |
| `ALLOWED_ORIGINS` | `*` | Comma-separated list of allowed CORS origins. |
| `DEEPFAKE_ENABLED` | `false` | Enable/disable deepfake detector module (`true` or `false`). |
| `SEMANTIC_SEARCH_ENABLED` | `true` | Enable/disable semantic vector index. |
| `VERISTAS_AI_URL` | `http://127.0.0.1:8080` | URL of local or remote `llama.cpp` server. |
| `VERISTAS_AI_TIMEOUT` | `5` | AI response timeout in seconds. |

---

## 10. Deepfake Detector Subsystem Explanation

VeristasOS includes a modular media manipulation screening architecture in `backend/app/services/deepfake_detector.py`:
- **CPU-First Architecture**: Avoids GPU/CUDA overhead so the deployment remains lightweight on free/starter cloud tiers.
- **Forensic Signals**: Analyzes noise variance, EXIF editing tool footprints (e.g. Photoshop/GIMP), compression artifacts, and grid resampling anomalies.
- **Configuration**: Disabled by default in production (`DEEPFAKE_ENABLED=false`) and returns structured analytical signals when enabled.
- **Disclaimer**: Clearly labelled as an AI-assisted forensic risk estimate, not definitive proof of synthetic media.

---

## 11. Automated Testing

Run the automated test suite using `pytest`:

```bash
pytest -v
```

---

## 12. Render Cloud Deployment

Render uses the exact specifications defined in `render.yaml`:

- **Build Command**:
  ```bash
  pip install -r backend/requirements.txt
  ```
- **Start Command**:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT --app-dir backend
  ```

---

## 13. License & Credits

Developed by **TheKnightProtocol**. Released under the [MIT License](LICENSE).
