# VeristasOS — Intelligent Fake News & Deepfake Detection

> **"Your truth. Your data. Your device."**
> **Multimodal Dual-Layer Privacy Shield & Truth Intelligence Platform**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

VeristasOS is a privacy-first, local-first AI verification and digital-integrity platform designed to evaluate textual news claims, inspect media metadata, calculate sensationalism risk, protect sensitive personal data, and detect scam coercion tactics.

---

## 🌟 Why VeristasOS is Different

Unlike standard fake-news classifiers that return an ungrounded black-box percentage score, VeristasOS operates a **Dual-Layer Verification Architecture**:

1. **Combines Truth Verification with Privacy Protection**: VeristasOS answers both *"Is this content trustworthy?"* and *"What is this content attempting to do with my data?"*
2. **India-First Sensitive Data Guard**: Automatically scans and masks Aadhaar numbers (`XXXX XXXX 1234`), PAN cards (`XXXXX1234X`), UPI handles (`user@upi`), OTP security PINs, and mobile numbers without storing sensitive information.
3. **Rule-Assisted Scam Radar**: Identifies financial coercion, KYC threat warnings, bank account block threats, and high-pressure urgency tactics.
4. **Explainable AI (LIME/SHAP Inspired)**: Provides transparent signal impact tables showing exactly why a verdict was generated (Sensational wording, ALL-CAPS density, Exclamation ratio).
5. **Local-First Privacy Architecture**: Designed to run linguistic heuristics and local AI inference (`llama.cpp` + `Qwen2.5-3B`) directly on-device to prevent data leakage.
6. **Multimodal Media Authenticity**: Evaluates SHA-256 cryptographic hashes, 64-bit perceptual `dHash`, EXIF camera tags, and OCR text consistency without heavy GPU requirements.

---

## 1. Project Overview & Dual-Layer Architecture

```
                                [ User Input ]
                                      │
                                      ▼
                        [ Master Verification Engine ]
                                      │
          ┌───────────────────────────┴───────────────────────────┐
          ▼                                                       ▼
[ LAYER 1 — PRIVACY SHIELD ]                      [ LAYER 2 — TRUTH ENGINE ]
  • Aadhaar / PAN / UPI / OTP Masking               • Truth Meter Status
  • Sensitive Data Exposure                         • Sensationalism Highlighter
  • Scam Radar Coercion Detection                   • LIME/SHAP Signal Impact Matrix
  • Privacy Grade (A / B / C / F)                   • Source Provenance Score
          │                                                       │
          └───────────────────────────┬───────────────────────────┘
                                      │
                                      ▼
                    [ Cyberpunk & ChatGPT Assistant UI ]
```

---

## 2. Key Features

- **Truth Meter**: Evaluates content reliability (`LIKELY RELIABLE`, `NEEDS VERIFICATION`, `SUSPICIOUS`, `CRITICAL WARNING`).
- **Sensationalism Highlighter**: Visually highlights trigger words directly in the prose using `<mark>` tags.
- **Privacy Shield (India-First Protection)**: Identifies and masks Aadhaar, PAN, UPI IDs, OTPs, and phone numbers (`XXXX XXXX 1234`).
- **Scam Radar**: Flags financial threats, bank suspension warnings, and KYC scam coercion.
- **Forward Checker Mode**: Specialized interface for WhatsApp and social media forwarded message verification.
- **Deepfake Lens (Prototype)**: Media metadata inspection, SHA-256 hashing, perceptual `dHash`, EXIF tag analysis, and OCR text overlay.
- **Local-First AI Status**: Live indicator showing whether local LLM (`llama.cpp`) or deterministic CPU fallback is active.

---

## 3. Technology Stack

- **Backend**: Python 3.12, FastAPI, Uvicorn, Pydantic v2
- **NLP & Stylometrics**: NLTK (Tokenization & Stylometric Analysis), Regex Pattern Matchers
- **Vector Search**: Scikit-learn (TF-IDF Vectorizer), NumPy
- **Image Processing**: Pillow (PIL), PyTesseract (Optional OCR), Hashlib
- **Local Generative AI**: `llama.cpp` HTTP server + `Qwen2.5-3B-Instruct`
- **Frontend**: Vanilla HTML5, CSS3 Custom Properties, ES6+ JavaScript, SVG
- **Testing**: Pytest, FastAPI TestClient

---

## 4. Repository Structure

```
VeristasOS/
├── app/
│   ├── main.py                     # FastAPI main application & routes
│   ├── models/
│   │   └── schemas.py              # Pydantic request/response data contracts
│   ├── services/
│   │   ├── ai_analyzer.py          # Generative AI prompt construction
│   │   ├── claim_analyzer.py       # Factual claim extraction
│   │   ├── deepfake_detector.py    # Modular deepfake risk detector
│   │   ├── explainability.py       # LIME/SHAP signal impact matrix
│   │   ├── image_analyzer.py       # Image hashing, OCR, EXIF & dHash
│   │   ├── media_authenticity.py   # CPU authenticity analyzer
│   │   ├── privacy_scanner.py      # India-First Aadhaar/PAN/UPI/OTP scanner
│   │   ├── provenance.py           # Publisher & source trust score
│   │   ├── risk_engine.py          # Weighted composite risk calculator
│   │   ├── scam_detector.py        # Rule-assisted Scam Radar
│   │   ├── semantic_search.py      # TF-IDF vector search & pagination
│   │   ├── text_analyzer.py        # Stylometric sensationalism scoring
│   │   └── verification_engine.py  # Master Dual-Layer Aggregator
│   └── tests/                      # Automated Pytest suite
├── frontend/
│   ├── app.js
│   ├── style.css
│   └── index.html                  # Dual-Layer ChatGPT-Style UI
├── .env.example                    # Environment variable template
├── .gitignore                      # Git exclusion rules
├── pytest.ini                      # Pytest runner configuration
├── render.yaml                     # Render Cloud deployment specification
└── README.md                       # Complete technical documentation
```

---

## 5. Local Setup & Installation

### Prerequisites
- **Python**: Version 3.12+ installed.
- **Git**: Installed and available on PATH.

### 1. Clone & Setup
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

### 4. Run Application
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend --reload
```

Access local endpoints:
- **Web App**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 6. API Endpoint Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | System health check (`{"status": "ok"}`). |
| `GET` | `/api/status` | Real-time system health and local AI status. |
| `POST` | `/api/verify` | Primary endpoint for Master Dual-Layer Verification. |
| `POST` | `/api/forward-check` | Dedicated Forward Checker endpoint for WhatsApp messages. |
| `POST` | `/analyze` | Unified text analysis pipeline. |
| `POST` | `/api/analyze-image` | Media forensics, perceptual hash, EXIF, & OCR endpoint. |
| `GET` | `/api/search` | Paginated vector search endpoint (`q`, `limit`, `offset`). |

---

## 7. Automated Testing

Run the automated Pytest suite:

```bash
pytest -v
```

---

## 8. Render Cloud Deployment

Render deploys directly from GitHub repository `main` branch using `render.yaml`:
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --app-dir backend`
- **Live URL**: [https://veristasos.onrender.com/](https://veristasos.onrender.com/)

---

## 9. Academic Project Credits & Team

- **Institution**: Dronacharya College of Engineering, Gurugram
- **Department**: CSE – Artificial Intelligence & Machine Learning
- **Team Members**:
  - Sankalp Sharma
  - Ishan Sharma
  - Rishabh
- **License**: MIT License
