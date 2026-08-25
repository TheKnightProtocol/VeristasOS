# VeristasOS — Truth Intelligence Platform

> **Multimodal AI-Assisted Misinformation Analysis, Provenance Verification, & Media Forensics Engine**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

VeristasOS is a production-grade, multimodal truth intelligence platform designed to evaluate textual claims, analyze image media metadata, calculate stylometric sensationalism risk, and inspect source provenance. It combines deterministic NLP heuristics with optional local generative AI interpretation (Qwen2.5-3B via `llama.cpp`) to deliver structured risk assessments without making ungrounded truth claims.

---

## 1. Project Overview & Mission

In modern digital information ecosystems, sensationalism, synthetic content, and context distortion degrade public trust. VeristasOS provides developers, intelligence analysts, and researchers with an extensible framework for content verification.

The platform executes multi-stage risk evaluation:
- **Stylometric & Linguistic Analysis**: Quantifies sensationalism, exclamation density, repetition, and capital letter usage.
- **Factual Assertion Extraction**: Extracts verifiable claims from unstructured prose.
- **Source Provenance Evaluation**: Assesses domain legitimacy, author attribution, and publication metadata.
- **Media Forensics & OCR**: Computes SHA-256 cryptographic hashes, 64-bit perceptual difference hashes (`dHash`), and extracts text via OCR.
- **Generative AI Interpretation**: Passes structured signals to a local offline LLM (`Qwen2.5-3B`) for nuanced contextual reasoning.

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
                    [ Neon Cyberpunk Frontend ]
```

---

## 3. Key Features

- **Neon Cyberpunk HUD**: Sleek, high-contrast dark console UI with reactive SVG radial risk gauges, risk metric progress bars, terminal emulator, and printable HTML report export.
- **Offline-First Deterministic Fallback**: Operates at 100% functionality using linguistic heuristics even when local LLMs are unreachable.
- **Cryptographic & Perceptual Media Inspection**: Computes SHA-256 and `dHash` perceptual difference signatures to identify modified or duplicate media.
- **Safe File Upload Security**: Strict MIME-type checking, extension validation, path traversal defense, and file size caps (max 20MB).
- **Modern FastAPI Lifespan Architecture**: Uses modern `asynccontextmanager` startup/shutdown handlers with zero deprecation warnings.
- **Comprehensive API Suite**: Fully documented endpoints with interactive OpenAPI Swagger UI (`/docs`).

---

## 4. Technology Stack

- **Backend**: FastAPI, Uvicorn, Pydantic v2, Python 3.12
- **Linguistic Analysis**: NLTK (Tokenization & Stylometrics), Regex
- **Image Processing**: Pillow (PIL), PyTesseract (Optional OCR), Hashlib
- **Local Generative AI**: `llama.cpp` HTTP server + `Qwen2.5-3B-Instruct`
- **Frontend**: Vanilla HTML5, CSS3 Custom Properties (Variables), ES6+ JavaScript, SVG Graphics
- **Testing & Quality Assurance**: Pytest, FastAPI TestClient

---

## 5. Repository Structure

```
VeristasOS/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   └── router.py          # Local llama.cpp AI gateway
│   │   ├── services/
│   │   │   ├── ai_analyzer.py      # Generative AI prompt construction
│   │   │   ├── claim_analyzer.py   # Factual claim extraction
│   │   │   ├── image_analyzer.py   # Image hashing, OCR, & dHash
│   │   │   ├── provenance.py       # Publisher & source trust score
│   │   │   ├── risk_engine.py      # Weighted composite scoring engine
│   │   │   └── text_analyzer.py    # Stylometric sensationalism scoring
│   │   └── main.py                 # FastAPI application entry point
│   ├── tests/
│   │   ├── conftest.py             # Pytest fixtures
│   │   ├── test_api.py             # API endpoint integration tests
│   │   ├── test_risk_engine.py     # Risk engine & claim extraction tests
│   │   └── test_text_analyzer.py   # Stylometric unit tests
│   └── requirements.txt            # Backend Python dependencies
├── frontend/
│   ├── app.js                      # Secondary JS fallback module
│   └── index.html                  # Cyberpunk UI Console (HTML/CSS/JS)
├── .github/
│   └── workflows/
│       └── tests.yml               # GitHub Actions CI workflow
├── Dockerfile                      # Production multi-stage Dockerfile
├── .dockerignore                   # Docker build exclusion patterns
├── .env.example                    # Environment variable configuration template
├── .gitignore                      # Git exclusion rules
├── pytest.ini                      # Pytest runner configuration
├── render.yaml                     # Render Cloud deployment specification
└── run_veristasos.ps1              # One-click Windows PowerShell launcher
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

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

---

## 7. Running the Application

### Option A: Using PowerShell Launcher (Windows)
```powershell
.\run_veristasos.ps1
```

### Option B: Using Uvicorn CLI
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
| `GET` | `/health` | Basic system health indicator. |
| `GET` | `/api/version` | Returns service name and version. |
| `GET` | `/api` | Capability manifest and endpoint index. |
| `GET` | `/api/status` | System health and local AI connectivity status. |
| `GET` | `/api/ai/status` | Real-time status probe for local `llama.cpp` server. |
| `POST` | `/analyze` | Primary unified text analysis pipeline. |
| `POST` | `/api/analyze` | Consistent alias for `/analyze`. |
| `POST` | `/api/ai/analyze` | Dedicated endpoint for generative AI reasoning. |
| `POST` | `/api/analyze-image` | Media forensics, perceptual hash, & OCR endpoint. |

### Example Request: Text Analysis (`POST /api/analyze`)

```json
{
  "text": "BREAKING! Secret government program exposed overnight by unverified sources! Officials are in shock!",
  "source_url": "https://unverified-buzz.example/breaking-news",
  "source_name": "Viral Buzz Times",
  "author": "Anonymous Reporter"
}
```

---

## 9. Local AI Setup (Optional Qwen2.5 3B)

VeristasOS natively integrates with a local `llama.cpp` server.

1. Download `Qwen2.5-3B-Instruct-GGUF` model file.
2. Launch `llama-server`:
```bash
llama-server -m models/qwen2.5-3b-instruct-q4_k_m.gguf --port 8080 -c 2048
```
3. VeristasOS will automatically detect the server at `http://127.0.0.1:8080`.

*Note: If the local AI server is offline, VeristasOS automatically falls back to deterministic linguistic analysis without interruption.*

---

## 10. Security Considerations

- **Strict File Upload Validation**: Rejects unsupported file extensions (`.exe`, `.sh`, `.py`) and unallowed MIME types.
- **Path Traversal Protection**: Upload filenames are sanitized using `Path(filename).name`.
- **Payload Limits**: Text inputs capped at 50,000 characters; file uploads capped at 20MB.
- **CORS Hardening**: Supports environment-driven origin filtering via `ALLOWED_ORIGINS`.
- **Zero Internal Traceback Leaks**: All raw exceptions are safely logged internally while returning standard HTTP error payloads.

---

## 11. Automated Testing & Verification

Run the full automated test suite using `pytest`:

```bash
pytest -v
```

The test suite validates:
- Endpoint health and version responses
- Unified text analysis pipeline
- Claim extraction logic
- Image hashing and perceptual dHash calculations
- Security rejection of malformed uploads and empty payloads
- Offline AI fallback behavior

---

## 12. Production Deployment

### Deployment Architecture & Cloud AI Strategy

When deploying to cloud platforms (e.g. **Render**, **Railway**, or **Hugging Face Spaces**):
- **Web App & Deterministic Engine**: Light footprint, deploys easily on free/low-cost container tiers (512MB RAM).
- **Local AI Model**: Heavy memory requirement (2GB+ RAM). In cloud environments, the application seamlessly runs in deterministic mode unless connected to an external OpenAI-compatible API endpoint via `VERISTAS_AI_URL`.

### Docker Deployment

Build and run using Docker:

```bash
# Build production Docker image
docker build -t veristasos:latest .

# Run container
docker run -d -p 8000:8000 --name veristasos veristasos:latest
```

---

## 13. Environment Variables Reference

| Variable | Default | Description |
| :--- | :--- | :--- |
| `VERISTAS_AI_URL` | `http://127.0.0.1:8080` | URL of the local or remote AI server. |
| `VERISTAS_AI_TIMEOUT` | `5` | AI response timeout in seconds. |
| `ENVIRONMENT` | `development` | Runtime mode (`development` or `production`). |
| `ALLOWED_ORIGINS` | `*` | Comma-separated list of allowed CORS origins. |
| `PORT` | `8000` | HTTP server port for Uvicorn. |

---

## 14. Analytical Disclaimer

VeristasOS provides AI-assisted risk indicators and analytical signals based on stylometrics, provenance metadata, and heuristic claim extraction. **It does not independently establish whether a statement is factual truth or falsehood.** Users must independently verify critical assertions using authoritative primary sources.

---

## 15. License & Credits

Developed by **TheKnightProtocol**. Released under the [MIT License](LICENSE).
