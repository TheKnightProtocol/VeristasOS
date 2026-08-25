# VeristasOS

### Truth Intelligence & Multimodal Misinformation Analysis Platform

VeristasOS is an AI-assisted truth intelligence platform designed to analyze digital content for linguistic, media, provenance, and contextual indicators associated with misinformation.

It combines deterministic analysis, explainable risk scoring, multimodal analysis services, provenance tracking, and an optional local AI reasoning layer into a single FastAPI-based system with a cyberpunk-inspired web interface.

> **VeristasOS does not claim to determine absolute truth.**
> It produces evidence-based indicators and risk assessments that help users investigate potentially misleading content.

---

## Overview

Modern misinformation can spread through multiple channels:

* sensational headlines
* emotionally manipulative language
* misleading claims
* altered or suspicious media
* weak provenance
* repeated narratives
* questionable source context

VeristasOS approaches the problem as a **multi-signal intelligence system** rather than relying on a single machine-learning classifier.

The platform analyzes available evidence and produces structured results that can be inspected by users and integrated into other applications.

---

## Core Capabilities

### 1. Text Intelligence

The text analysis engine examines submitted content for linguistic patterns including:

* word count
* sentence count
* average sentence length
* question frequency
* exclamation frequency
* uppercase-word usage
* repeated-word ratio
* sensational vocabulary
* sensationalism scoring
* stylistic indicators

These signals can be combined into a broader content-risk assessment.

---

### 2. Claim Analysis

VeristasOS can extract and analyze claims from submitted content.

The claim analysis layer is designed to provide:

* claim identification
* claim structure
* claim risk indicators
* supporting analysis
* structured claim results

This allows the system to move beyond simply classifying an entire article.

---

### 3. Multimodal Media Analysis

The architecture includes media-analysis services for visual content.

Supported analysis pathways include:

* image inspection
* image metadata
* visual feature analysis
* media risk indicators
* optional computer-vision models

The platform is designed to be extensible with additional multimodal models.

> Deepfake detection is intentionally outside the current project scope.

---

### 4. Provenance & Source Intelligence

VeristasOS includes provenance-oriented components designed to investigate where information came from and how trustworthy its supporting context appears.

The system can work with:

* source metadata
* provenance records
* content hashes
* reverse-image-search integrations
* structured source information
* provenance events

---

### 5. Integrity Ledger

The project includes a JSON-based blockchain-style integrity ledger.

The ledger provides a lightweight demonstration of:

* content hashing
* chained records
* integrity verification
* provenance events
* tamper-evident history

This is intended as an educational and demonstrative integrity layer rather than a replacement for a production blockchain network.

---

### 6. Explainability

VeristasOS is designed around explainable analysis.

Instead of returning only:

```text
FAKE
```

the platform aims to expose the signals contributing to its assessment.

Example signals include:

```text
High sensational vocabulary
Frequent exclamation usage
Unusual uppercase usage
High repetition ratio
Weak provenance indicators
```

This makes the system more useful for investigation and demonstration.

---

### 7. Local AI Reasoning

VeristasOS can connect to a locally hosted GGUF language model through `llama.cpp`.

The local AI architecture uses:

```text
VeristasOS
     │
     ▼
LocalAIRouter
     │
     ▼
llama-server
     │
     ▼
Qwen2.5 3B GGUF
```

The local AI layer can assist with:

* diagnostic explanations
* terminal error analysis
* command troubleshooting
* reasoning over analysis results
* structured explanations

Because the model runs locally, the system can operate without sending these prompts to a commercial cloud LLM.

---

## VeristasOS Terminal

The project also contains a diagnostic terminal interface.

Example:

```text
VERISTASOS TERMINAL

Local AI: CONNECTED

veristasOS> python nonexistent.py
```

When a command fails, VeristasOS can inspect the resulting error and generate an explanation and suggested remediation.

Example output:

```text
VERISTASOS AI DIAGNOSTIC

ERROR:
python: can't open file 'nonexistent.py'

WHY:
The specified Python script does not exist at the requested path.

FIX:
Verify the filename or provide the correct script path.
```

The terminal is intended to demonstrate how local AI reasoning can be integrated directly into an operating-environment-style interface.

---

# Architecture

```text
                         VERISTASOS
                              │
                ┌─────────────┴─────────────┐
                │                           │
             Frontend                    FastAPI
                │                           │
                │              ┌────────────┼────────────┐
                │              │            │            │
                ▼              ▼            ▼            ▼
          Web Dashboard      Text        Claims       Media
                              │            │            │
                              ▼            ▼            ▼
                         Analysis      Analysis     Analysis
                              │            │            │
                              └────────────┼────────────┘
                                           │
                                           ▼
                                     Risk Engine
                                           │
                              ┌────────────┴────────────┐
                              │                         │
                              ▼                         ▼
                       Explainability              Provenance
                              │                         │
                              └────────────┬────────────┘
                                           │
                                           ▼
                                      Final Result
                                           │
                              ┌────────────┴────────────┐
                              │                         │
                              ▼                         ▼
                       Web Interface             Local AI Router
                                                        │
                                                        ▼
                                                   llama-server
                                                        │
                                                        ▼
                                                Qwen2.5 GGUF
```

---

# Technology Stack

## Backend

* Python
* FastAPI
* Pydantic
* Uvicorn

## Artificial Intelligence

* Local GGUF language models
* Qwen2.5 3B Instruct
* llama.cpp / llama-server
* Optional computer-vision models
* Explainability-oriented analysis

## NLP

* NLTK
* Python text-processing utilities
* Stylometric analysis

## Computer Vision

* Hugging Face ecosystem
* CLIP-compatible models
* Image-analysis services

## Data & Integrity

* JSON
* SHA-based content hashing
* Provenance records
* Blockchain-style chained ledger

## Frontend

* HTML5
* CSS3
* JavaScript
* Responsive UI
* Cyberpunk-inspired interface

## Development

* Git
* GitHub
* Pytest
* VS Code
* PowerShell

## Deployment

Designed for deployment using:

* Render
* GitHub
* other Python-compatible hosting platforms

---

# Project Structure

```text
VeristasOS/
│
├── app/
│   ├── api/
│   │   ├── routes_analysis.py
│   │   ├── routes_media.py
│   │   ├── routes_source.py
│   │   └── routes_text.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── services/
│   │   ├── analysis_engine.py
│   │   ├── audio_analyzer.py
│   │   ├── blockchain.py
│   │   ├── explainability.py
│   │   ├── image_analyzer.py
│   │   ├── reverse_image.py
│   │   ├── stylometry.py
│   │   └── hashing.py
│   │
│   └── utils/
│       └── logging.py
│
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   ├── router.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── services/
│   │   │   ├── ai_analyzer.py
│   │   │   ├── claim_analyzer.py
│   │   │   ├── image_analyzer.py
│   │   │   ├── provenance.py
│   │   │   ├── risk_engine.py
│   │   │   └── text_analyzer.py
│   │   │
│   │   ├── terminal/
│   │   │   ├── shell.py
│   │   │   └── __init__.py
│   │   │
│   │   └── main.py
│   │
│   ├── tests/
│   └── requirements.txt
│
├── data/
│   └── ledger/
│       └── blockchain.json
│
├── frontend/
│   └── index.html
│
├── tests/
│   └── test_text_analyzer.py
│
├── .env.example
├── .gitignore
├── README.md
├── pytest.ini
├── render.yaml
├── requirements.txt
└── run_veristasos.ps1
```

---

# Running Locally

## 1. Clone the repository

```powershell
git clone https://github.com/TheKnightProtocol/VeristasOS.git
cd VeristasOS
```

---

## 2. Create a virtual environment

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

---

## 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If using the backend-specific environment:

```powershell
pip install -r backend\requirements.txt
```

---

## 4. Start the FastAPI backend

From the project root:

```powershell
python -m uvicorn backend.app.main:app --reload
```

If the application is configured with the root `app` package instead:

```powershell
python -m uvicorn app.main:app --reload
```

The terminal should show:

```text
Uvicorn running on http://127.0.0.1:8000
```

Open the following in a browser:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

---

# API

## Health

```http
GET /health
```

Example:

```json
{
  "status": "healthy",
  "service": "VeristasOS",
  "version": "1.0.0"
}
```

---

## API Information

```http
GET /api
```

Returns available service information and endpoint metadata.

---

## Text Analysis

```http
POST /analyze
```

Request:

```json
{
  "text": "Your article or claim goes here."
}
```

The response contains the available text-analysis signals.

---

# Example Analysis

Input:

```text
BREAKING!!! THIS SHOCKING NEWS WILL CHANGE EVERYTHING!!!
Experts say this incredible discovery is absolutely unbelievable!
```

Potential indicators:

```text
Sensationalism Score
High

Exclamation Count
4

Uppercase Word Count
High

Sensational Word Count
High
```

The platform should interpret these signals as **indicators**, not definitive proof that the content is false.

---

# Local AI Setup

The local AI layer can use `llama-server` with a GGUF model.

Example:

```powershell
D:\VeristasAI\runtime\llama-server.exe `
    -m "D:\VeristasAI\models\<model>.gguf" `
    --host 127.0.0.1 `
    --port 8080
```

Verify the server:

```powershell
Invoke-RestMethod http://127.0.0.1:8080/health
```

The VeristasOS router then communicates with the local model through HTTP.

---

# Security

VeristasOS follows a local-first architecture wherever practical.

Recommended production configuration:

* restrict CORS origins
* use environment variables for secrets
* never commit API keys
* keep `.env` out of Git
* validate uploaded media
* limit request sizes
* sanitize user-provided content
* use HTTPS in production
* authenticate sensitive administrative endpoints

The `.env.example` file documents configuration without exposing secrets.

---

# Testing

Run the test suite with:

```powershell
pytest
```

Or:

```powershell
python -m pytest
```

The test suite covers important components including:

* text analysis
* risk scoring
* API behavior
* analysis services

---

# Deployment

The project includes a `render.yaml` configuration intended to simplify Render deployment.

Typical deployment flow:

```text
Local Development
       │
       ▼
Git
       │
       ▼
GitHub
       │
       ▼
Render
       │
       ▼
Public VeristasOS API
```

For production deployment, configure required environment variables in the hosting provider rather than committing them to the repository.

---

# Design Philosophy

VeristasOS is built around five principles:

### 1. Evidence over labels

The system should expose why content receives a particular risk assessment.

### 2. Explainability over black-box decisions

Users should be able to inspect the signals behind the analysis.

### 3. Local-first intelligence

Local AI provides a privacy-oriented alternative for supported reasoning tasks.

### 4. Multimodal investigation

Misinformation does not exist only in text, so the architecture supports text, image, audio, and provenance pathways.

### 5. Human-in-the-loop verification

The final decision about whether information is true should remain with the investigator and supporting evidence.

---

# Current Scope

### Implemented / Core

* FastAPI backend
* Responsive web interface
* Text analysis
* Stylometric indicators
* Sensationalism scoring
* Risk-engine architecture
* Claim-analysis architecture
* Image-analysis architecture
* Audio-analysis architecture
* Provenance analysis
* Integrity ledger
* Explainability layer
* Local AI router
* Qwen GGUF integration
* llama.cpp server integration
* AI-powered diagnostic terminal
* API documentation
* Automated tests
* Git/GitHub project structure
* Render deployment configuration

### Intentionally Excluded

Deepfake detection is **not part of the current VeristasOS scope**.

Real-time context-poisoning protection and dynamic VRAM balancing were also excluded from the primary demo because they provide limited visible value compared with the core investigation features.

---

# Limitations

VeristasOS is a research/engineering project and should not be treated as an autonomous fact-checking authority.

A high risk score does not necessarily mean information is false.

Likewise, a low risk score does not prove that information is true.

The system should be used to:

```text
Detect signals
      ↓
Investigate evidence
      ↓
Inspect provenance
      ↓
Review explanations
      ↓
Make an informed decision
```

---

# Future Improvements

Potential future work includes:

* stronger source verification
* live fact-checking integrations
* additional multilingual NLP models
* improved audio analysis
* production-grade media pipelines
* browser extension integration
* Telegram bot integration
* persistent analysis history
* user authentication
* distributed provenance storage
* larger local reasoning models
* advanced retrieval-augmented verification
* real-time monitoring dashboards

---

# Project Goal

VeristasOS aims to demonstrate how modern AI engineering techniques can be combined into a practical **truth intelligence platform**.

Rather than presenting misinformation detection as a single binary classification problem, VeristasOS treats it as an investigation pipeline involving:

```text
Language
   +
Claims
   +
Media
   +
Source Context
   +
Provenance
   +
Explainability
   +
Local AI
   =
Truth Intelligence
```

---

# License

This project is provided for educational, research, and engineering purposes.

See the `LICENSE` file for licensing information.

---

# Author

**Sankalp Sharma**

GitHub:

https://github.com/TheKnightProtocol

Project:

https://github.com/TheKnightProtocol/VeristasOS

---

## VeristasOS

**Analyze. Investigate. Verify.**

> Truth is not a label. It is an evidence trail.
