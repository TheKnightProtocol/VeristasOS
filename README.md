# VERISTASOS — YOUR AI SAATHI

> **"An AI agent that doesn't just act for you — it verifies whether it should act before it does."**
> 
> **Academic Description**: A Safety-First Personal AI Agent with an Explainable Digital Trust & Permission Engine.
> **Taglines**: *"Protect. Understand. Act."* | *"Aap busy ho. Saathi sambhal lega."*

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/tests-55%2F55%20passing-brightgreen.svg)]()

---

## 🌟 The Central Novelty

VeristasOS is NOT just another chatbot, email writer, or fake-news classifier.

The central innovation is the **TRUST FIREWALL**: Every potentially autonomous AI action must pass through a multi-stage safety decision layer before execution.

```text
                                USER
                                  │
                              AI SAATHI
                                  │
                        INTENT UNDERSTANDING
                                  │
                     ┌────────────────────────┐
                     │     DIGITAL TRUST      │
                     │        ENGINE          │
                     └────────────────────────┘
                                  │
                     ┌────────────────────────┐
                     │   MODEL RELIABILITY    │
                     │        ENGINE          │
                     └────────────────────────┘
                                  │
                     ┌────────────────────────┐
                     │    USER PERMISSION     │
                     │        ENGINE          │
                     └────────────────────────┘
                                  │
                         TRUST FIREWALL
                                  │
                     ┌────────────┼────────────┐
                     ▼            ▼            ▼
                  AUTO-ACT       ASK         BLOCK
                     │            │            │
                     └────────────┼────────────┘
                                  │
                         EXPLAINABLE RESULT
```

### Decision Framework:
- **🟢 LOW RISK** → `AUTO-ACT` (e.g. Summarize routine email, categorize message, create reminder)
- **🟡 MEDIUM RISK** → `ASK USER` (e.g. Draft email reply, schedule project review meeting)
- **🔴 HIGH RISK** → `BLOCK & PROTECT` (e.g. Bank KYC scam, UPI payment request, OTP/Password share, Aadhaar/PAN upload)

---

## 🚀 Key Engines & Architecture

### 1. Trust Firewall (`backend/app/services/trust_firewall.py`)
Central decision gatekeeper evaluating proposed actions against Content Risk, Privacy Risk, Financial Risk, Prompt Injection Defense, Model Reliability, and User Policy rules.

### 2. Model Reliability Engine (`backend/app/services/reliability_engine.py`)
Evaluates prediction confidence, heuristic uncertainty indicators (LOW, MEDIUM, HIGH), evidence quality, input quality, and Out-of-Distribution (OOD) risk.

### 3. User Policy / Permission Engine (`backend/app/services/policy_engine.py`)
Configurable permission tiers (`ALWAYS_ALLOW`, `ASK_FIRST`, `NEVER_ALLOW`) with Senior Citizen Mode support for enlarged alerts and strict safety rules.

### 4. Scam DNA Engine (`backend/app/services/scam_dna.py`)
Generates 5-part threat feature profiles (Urgency %, Impersonation %, Financial Pressure %, Sensitive Data %, Suspicious URL %) and identifies attack vectors (Bank KYC, OTP Scam, UPI Scam, Investment Fraud).

### 5. Prompt Injection Defense (`backend/app/services/prompt_defense.py`)
Structural boundary separation isolating untrusted external content from system/user safety policies, preventing adversarial prompt overrides.

### 6. India-First Privacy Shield (`backend/app/services/privacy_scanner.py`)
Automatically scans and redacts Aadhaar numbers (`XXXX XXXX 1234`), PAN cards (`XXXXX1234X`), UPI handles (`user@upi`), OTP PINs, and Indian mobile numbers.

---

## 🛠️ Technology Stack

- **Backend Framework**: Python 3.12, FastAPI, Uvicorn, Pydantic v2
- **NLP & Text Core**: NLTK (Stylometrics & Sensationalism Scoring), Regex Heuristics
- **Similarity & Forensics**: Scikit-learn (TF-IDF Vectorizer), NumPy, Pillow, dHash Perceptual Hashing
- **Frontend**: Vanilla HTML5, CSS3 Custom Properties (Dark/Light themes), ES6 JavaScript
- **Testing**: Pytest (55 Unit Tests, 100% Pass Rate)

---

## 🏃 Running the Application

### 1. Install Dependencies
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start Local Server
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```
Open your browser at: **`http://127.0.0.1:8000/`**

### 3. Run Automated Tests
```bash
pytest -v
```

---

## 🎯 5 End-to-End Demonstration Scenarios

### DEMO 1 — High-Risk Scam (Blocked)
- **Input**: *"URGENT: Your SBI account will be blocked today! Complete KYC immediately: http://sbi-kyc-update-login.com"*
- **Result**: `🔴 HIGH RISK` → **ACTION BLOCKED**
- **WHY**: Urgency detected, Bank impersonation, Suspicious URL.

### DEMO 2 — Safe Routine Content (Auto-Acted)
- **Input**: *"Tomorrow's project evaluation meeting is scheduled for 2:00 PM."*
- **Result**: `🟢 LOW RISK` → **AUTO-ACTED** (Calendar reminder created).

### DEMO 3 — Medium Risk Action (Human Approval Required)
- **Input**: *"Reply to recruiter regarding interview invitation."*
- **Result**: `🟡 MEDIUM RISK` → **ASK USER** (Draft response prepared, awaiting approval).

### DEMO 4 — Dangerous Financial/OTP Request (Blocked)
- **Input**: *"Use the OTP 4589 and complete payment of Rs 999 via UPI."*
- **Result**: `🔴 CRITICAL RISK` → **STRICTLY BLOCKED** (Financial/OTP actions cannot be performed automatically).

### DEMO 5 — Hinglish Intent Understanding
- **Input**: *"Bhai ye KYC wala link safe hai kya?"*
- **Result**: *"⚠️ Ye suspicious lag raha hai. KYC impersonation aur urgency signals detect hue hain. Link mat kholo aur OTP/UPI PIN share mat karo."*

---

## 📜 Team & License

- **Team**: **Sankalp Sharma**, **Ishan Sharma**, and **Rishabh**
- **Institution**: Dronacharya College of Engineering, Gurugram (CSE - AI & ML)
- **License**: MIT License
