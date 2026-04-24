# 🏥 TriageAI

> **AI-powered emergency department triage — Malaysian Triage Scale, multi-agent swarm, real-time nurse dashboard.**

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev)
[![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)](https://flask.palletsprojects.com)
[![Groq](https://img.shields.io/badge/LLM-Llama--3.3--70b-orange)](https://groq.com)
[![XGBoost](https://img.shields.io/badge/ML-XGBoost-red)](https://xgboost.readthedocs.io)

---

## 🚨 The Problem

Emergency departments are overwhelmed. Nurses manually assess every patient on arrival — a slow, error-prone process that is especially critical when time is measured in minutes. A single misclassification can cost a life.

**TriageAI** augments the triage nurse with a multi-agent AI swarm that analyses vitals, symptoms, and visual flags in parallel, then synthesises a clinically-reasoned zone decision in seconds — using the official **Malaysian Triage Scale (MTS)**.

---

## ✨ What It Does

| Role | Experience |
|---|---|
| 🧑‍⚕️ **Patient** | Self-checks in at a kiosk — enters symptoms, vitals, and visual flags via a guided form |
| 🖥️ **Patient Display** | Receives a plain-language explanation of their triage zone and expected wait time |
| 👩‍⚕️ **Nurse** | Sees a live dashboard with the AI's zone decision, confidence score, clinical narrative, and full agent reasoning |

---

## 🧠 How It Works — The AI Swarm

A five-agent pipeline runs on every patient submission:

```
Patient Input (vitals + symptoms + visual flags)
         │
         ▼
  [XGBoost ML]  ──→  initial zone signal
         │
         ▼
  [ORCHESTRATOR]
    ┌────┴────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐
    │ VITALS  │  │ SYMPTOM  │  │  VISUAL  │  │   RISK    │
    │  AGENT  │  │  AGENT   │  │  AGENT   │  │   AGENT   │
    └────┬────┘  └────┬─────┘  └────┬─────┘  └─────┬─────┘
         └────────────┴─────────────┴───────────────┘
                                │
                       [COORDINATOR AGENT]
                                │
                     Final triage result:
                     • Zone 1–5 + colour
                     • Confidence %
                     • Clinical narrative (nurse)
                     • Patient explanation (display screen)
                     • Flag reasons + escalation alerts
```

**Each agent is a specialist:**

- **Vitals Agent** — Analyses heart rate, BP, SpO₂, temperature, respiratory rate
- **Symptom Agent** — Interprets reported complaints and onset patterns
- **Visual Agent** — Evaluates physical appearance flags (pallor, diaphoresis, distress level, etc.)
- **Risk Agent** — Cross-signal pattern detector; flags edge cases and escalation triggers
- **Coordinator Agent** — Senior ED physician persona; synthesises all agents + XGBoost into a final authoritative decision

---

## 🗂️ Project Structure

```
triageai/
├── start.sh                        ← one command to launch everything
├── backend/
│   ├── server.py                   ← Flask REST API
│   ├── triage_engine.py            ← XGBoost inference
│   ├── models.py                   ← Pydantic schemas
│   ├── generate_training_data.py   ← synthetic training data generator
│   ├── train_model.py              ← XGBoost model trainer
│   ├── agents/
│   │   ├── orchestrator.py         ← fans out to all agents in parallel
│   │   ├── vitals_agent.py
│   │   ├── symptom_agent.py
│   │   ├── visual_agent.py
│   │   ├── risk_agent.py
│   │   └── coordinator.py          ← final decision synthesiser
│   ├── tools/
│   │   └── groq_utils.py           ← LLM API + JSON parsing
│   └── requirements.txt
└── frontend/                       ← React + Vite
    └── src/
        ├── pages/
        │   ├── LandingPage.jsx
        │   ├── KioskPage.jsx           ← patient self-check-in
        │   ├── PatientDisplayPage.jsx  ← patient-facing result screen
        │   └── NurseDashboardPage.jsx  ← live queue + AI reasoning panel
        └── components/
            ├── SwarmPanel.jsx          ← visualises all agent outputs
            ├── VitalsForm.jsx
            ├── SymptomQuestionnaire.jsx
            ├── VisualFlagsForm.jsx
            └── ZoneBadge.jsx
```

---

## ⚡ Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- A [Groq API key](https://console.groq.com) (free tier available)

### 1. Clone & configure

```bash
git clone https://github.com/adamharraz/medicaltriage.git
cd medicaltriage
```

```bash
# Set your API key (choose one)
export GROQ_API_KEY=gsk_...
# or
echo "GROQ_API_KEY=gsk_..." > backend/.env
```

### 2. (Optional) Train the XGBoost model

```bash
cd backend
pip install -r requirements.txt
python generate_training_data.py
python train_model.py
```

> If skipped, the server falls back to Zone 3 as the ML signal — the AI swarm still runs fully.

### 3. Launch

```bash
chmod +x start.sh
./start.sh
```

### 4. Open the app

| Interface | URL |
|---|---|
| 🧑‍⚕️ Patient Kiosk | http://localhost:5173/kiosk |
| 👩‍⚕️ Nurse Dashboard | http://localhost:5173/nurse |
| 🔌 API Health | http://localhost:8080/api/health |
| 🧪 Demo (no API calls) | http://localhost:8080/api/demo |

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/triage` | Submit patient data, run AI swarm |
| `GET` | `/api/patients` | List all active patients |
| `GET` | `/api/patients/<id>` | Get single patient record |
| `PATCH` | `/api/patients/<id>/override` | Nurse manual zone override |
| `DELETE` | `/api/patients/<id>` | Discharge patient |
| `GET` | `/api/queue-stats` | Zone counts + flagged count |
| `GET` | `/api/demo` | Mock result for UI testing |

---

## 🇲🇾 Malaysian Triage Scale

| Zone | Colour | Urgency | Target Time |
|---|---|---|---|
| 1 | 🔴 Red | Life-threatening — immediate resuscitation | Immediate |
| 2 | 🟠 Orange | Very urgent — may deteriorate rapidly | ≤ 10 min |
| 3 | 🟡 Yellow | Urgent — stable but requires prompt attention | ≤ 30 min |
| 4 | 🟢 Green | Semi-urgent — minor illness or injury | ≤ 60 min |
| 5 | 🔵 Blue | Non-urgent — suitable for GP or clinic | ≤ 120 min |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | Llama 3.3 70B via Groq API |
| ML Model | XGBoost (trained on synthetic MTS data) |
| Backend | Python, Flask, Pydantic |
| Frontend | React 18, Vite, Tailwind CSS |
| Agent Framework | Custom multi-agent swarm (no LangChain) |

---

## 🌱 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | Groq API key (get one free at console.groq.com) |
| `PORT` | No | Flask port (default: `8080`) |
| `FLASK_ENV` | No | Set to `development` for debug mode |
