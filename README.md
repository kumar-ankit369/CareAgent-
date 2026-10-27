<div align="center">

# 🏥 CareAgent
### Agentic AI Hospital Assistant

**An enterprise-grade, clinician-safe Agentic AI Healthcare Platform**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5+-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![HL7 FHIR](https://img.shields.io/badge/HL7-FHIR%20R4-E8734A?style=for-the-badge)](https://hl7.org/fhir/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)

*Multi-agent orchestration · HL7 FHIR records · Clinician-in-the-loop safety · HIPAA audit trail*

---

</div>

## 📖 Overview

**CareAgent v2.0** is a full-stack, production-ready agentic AI platform purpose-built for hospitals and clinics. It combines **multi-agent orchestration**, **HL7 FHIR electronic health records**, **clinician-in-the-loop safety guardrails**, **vitals monitoring**, **smart notifications**, and a **real-time health dashboard** — delivered through dual portals for patients and doctors.

> **⚕️ Safety First:** Every AI decision passes through a clinical safety layer. The system can never prescribe medications, will never commit an appointment without explicit patient confirmation, and will immediately escalate acute emergencies to trained professionals.

---

## ✨ Feature Set

### Core Clinical Features
| Feature | Description |
|---|---|
| 🚨 **Emergency Short-Circuit** | Detects acute symptoms (chest pressure, stroke signs, acute dyspnea) and instantly routes to emergency triage + hotline numbers *before any LLM call* |
| 💊 **Medication Safety Invariant** | Architecturally prevented from prescribing or modifying dosages; missed-dose queries route to approved clinical guidelines only |
| 🧬 **EHR & Lab Agent (FHIR R4)** | Longitudinal delta analysis on diagnostics (e.g. HbA1c 6.8% → 7.4%), reference range evaluation, auto-generated consultation questions |
| 📅 **Appointment Agent (Human-in-the-Loop)** | 2-step booking: searches slots → stages uncommitted → requires explicit patient confirm before locking |
| 💉 **Medication Adherence Agent** | Clinician-authorized regimens, Taken/Skipped/Late event logging, longitudinal adherence rate calculation |
| 🔐 **JWT RBAC Security** | Role-Based Access Control (Patient / Doctor) with permission-aware context injection at every agent boundary |
| 📋 **HIPAA Audit Trail** | Immutable, append-only audit log of every AI action, EHR access, and clinical decision |

### New in v2.0
| Feature | Description |
|---|---|
| 📊 **Vitals Monitoring** | Patients self-log BP, heart rate, SpO2, temperature, glucose, weight. Rule-based engine auto-classifies readings as normal / elevated / critical |
| 🔔 **Smart Notifications** | In-app notification feed with medication reminders, appointment alerts, lab result pushes, and critical vital warnings. Respects patient quiet-hour preferences |
| 🏥 **Health Dashboard** | Aggregated health score (0–100) combining adherence, lab results, and vitals — with color-coded wellness status |
| 🎯 **Risk Stratification** | Doctor-facing patient risk tier (minimal / low / medium / high) with scored contributing factors (adherence, labs, vitals) |
| 📐 **Separated Pydantic Schemas** | All API request/response contracts extracted into `models/schemas_*.py` — fully typed, documented, with examples |

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        HOSPITAL WEB PLATFORM                         │
│               (Vite + React 18 + Tailwind CSS + Lucide)              │
│                                                                      │
│    ┌────────────────────────────┬─────────────────────────────┐      │
│    │      🧑 Patient Portal     │      👨‍⚕️ Doctor Portal        │      │
│    │  · AI chat & action cards  │  · Patient roster + risk     │      │
│    │  · Lab trend sparklines    │  · AI pre-visit briefings    │      │
│    │  · Vitals logger widget    │  · Prescription auth queue   │      │
│    │  · Medication checkboxes   │  · Risk stratification panel │      │
│    │  · Health score dashboard  │  · HIPAA audit trail viewer  │      │
│    │  · Notification bell       │  · Vitals alerts feed        │      │
│    └──────────────┬─────────────┴──────────────┬──────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
                   │         REST / SSE Streaming       │
                   ▼                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   FASTAPI CORE & SECURITY LAYER                      │
│   · JWT Authentication & RBAC (Patient / Doctor roles)              │
│   · Permission-Aware Context Injection per agent call               │
│   · Pydantic v2 typed request/response validation                   │
│   · HIPAA Audit Trail Logger (append-only)                          │
│   · Streaming response endpoints (Server-Sent Events)               │
└─────────────────────┬────────────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│              ORCHESTRATOR & AGENT WORKFLOW ENGINE                    │
│   Step 1 → Emergency Triage Check     (short-circuit if acute)      │
│   Step 2 → Intent Detection & Clinical Safety Filter                │
│   Step 3 → Multi-Agent Routing to specialist agent                  │
└──────┬──────────────┬──────────────┬──────────────┬─────────────────┘
       │              │              │              │
       ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
│ 🧬 EHR &    │ │ 📅 APPT      │ │ 💊 MED       │ │ 📊 VITALS &     │
│   LAB AGENT  │ │    AGENT     │ │    AGENT     │ │    NOTIF AGENT   │
│              │ │              │ │              │ │                  │
│ · FHIR R4    │ │ · Slot Finder│ │ · Regimen    │ │ · Self-log vitals│
│ · Lab Deltas │ │ · Uncommitted│ │ · Adherence  │ │ · Alert classify │
│ · Trend Anal.│ │ · Confirm    │ │ · No-Rx Guard│ │ · Push reminders │
│ · Consult Qs │ │ · Booking    │ │ · Adherence% │ │ · Quiet hours    │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘
```

---

## 📡 API Reference

All endpoints are prefixed with `/api`. Full interactive docs: **http://localhost:8000/docs**

### 🔐 Authentication — `/api/auth`
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/login` | None | Login and receive JWT token |
| `POST` | `/auth/switch-demo-role` | None | Switch between Patient / Doctor demo tokens |
| `GET` | `/auth/me` | Bearer | Get current user profile |

### 🤖 Agent Chat — `/api/chat`
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/chat/send` | Bearer | Send a natural-language message to the AI orchestrator |

### 👤 Patient Records — `/api/patients`
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/patients/profile` | Bearer | Get own FHIR patient profile |
| `GET` | `/patients/conditions` | Bearer | Get active conditions list |

### 🧬 Lab Reports — `/api/reports`
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/reports/latest` | Bearer | Get latest lab observations |
| `GET` | `/reports/trends?test_name=HbA1c` | Bearer | Longitudinal trend & delta analysis |
| `POST` | `/reports/upload` | Bearer | Ingest a new lab result (parser + FHIR store) |

### 📅 Appointments — `/api/appointments`
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/appointments/my` | Bearer | Get upcoming appointments |
| `GET` | `/appointments/slots` | Bearer | Browse available booking slots |
| `POST` | `/appointments/stage` | Bearer | Stage an uncommitted booking |
| `POST` | `/appointments/confirm` | Bearer | Confirm a staged booking (step 2) |
| `DELETE` | `/appointments/{id}` | Bearer | Cancel an appointment |

### 💊 Medications — `/api/medications`
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/medications/prescribed` | Bearer | Get authorized medication list |
| `GET` | `/medications/schedule` | Bearer | Get daily dose schedule |
| `GET` | `/medications/adherence` | Bearer | Get adherence metrics summary |
| `POST` | `/medications/adherence/log` | Bearer | Log a Taken / Skipped / Late event |

### 📊 Vitals Monitoring — `/api/vitals` *(New v2)*
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/vitals/log` | Bearer | Log a vital reading (BP, HR, SpO2, glucose, weight) |
| `GET` | `/vitals/history?vital_type=blood_pressure` | Bearer | Get history for one vital type |
| `GET` | `/vitals/summary` | Bearer | Latest reading of every vital type |
| `GET` | `/vitals/alerts` | Bearer | All elevated / critical vital flags |

### 🔔 Notifications — `/api/notifications` *(New v2)*
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/notifications/` | Bearer | Get notification feed (filter by unread) |
| `POST` | `/notifications/{id}/read` | Bearer | Mark one notification as read |
| `POST` | `/notifications/read-all` | Bearer | Mark all notifications as read |
| `GET` | `/notifications/preferences` | Bearer | Get notification preferences |
| `PUT` | `/notifications/preferences` | Bearer | Update preferences (channels, quiet hours) |

### 🏥 Health Dashboard — `/api/health` *(New v2)*
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/health/dashboard` | Bearer | Full health snapshot: score, conditions, labs, vitals, next appt |
| `GET` | `/health/risk-stratification?patient_id=...` | Bearer | Doctor: patient risk tier with scored factors |

### 👨‍⚕️ Doctor Portal — `/api/doctor`
| Method | Endpoint | Auth (Doctor) | Description |
|---|---|---|---|
| `GET` | `/doctor/patients` | Doctor JWT | Assigned patient roster with stats |
| `GET` | `/doctor/patient/{id}/ai-briefing` | Doctor JWT | AI-generated pre-visit clinical briefing |
| `POST` | `/doctor/prescriptions/authorize` | Doctor JWT | Authorize a new prescription (clinician-only) |
| `GET` | `/doctor/audit-logs` | Doctor JWT | HIPAA immutable audit trail (last 50 entries) |

---

## 🛠️ Tech Stack

### Backend
| Layer | Technology |
|---|---|
| API Framework | FastAPI 0.110+ with async support |
| AI / LLM | Google Gemini (`google-generativeai`) |
| Healthcare Standard | HL7 FHIR R4 |
| Schema Validation | Pydantic v2 (typed schemas per domain) |
| Auth | JWT (`python-jose`) + bcrypt |
| Testing | pytest + httpx async client |
| Server | Uvicorn ASGI |

### Frontend
| Layer | Technology |
|---|---|
| Framework | React 18 + Vite 5 |
| Styling | Tailwind CSS + animations |
| Icons | Lucide React |
| State | React hooks (useState / useEffect) |
| API Client | Native fetch + EventSource (SSE) |

---

## ⚙️ Configuration & API Key Setup

CareAgent operates in **dual-mode**:
- **Offline / Clinical Rules Engine (Zero API Key):** Ready out of the box with zero setup. Operates deterministically with clinical safety invariants, FHIR records, medication adherence, appointment staging, vitals alert rules, and audit logging.
- **Live Agentic AI (Google Gemini LLM):** When a `GEMINI_API_KEY` is provided, CareAgent grounds natural language queries in the patient's EHR records to generate rich, contextual clinical insights with safety guardrails.

### 🔑 Where to Put Your API Key

1. Navigate to the `backend/` folder.
2. Locate the `.env.example` file:
   ```bash
   cd backend
   cp .env.example .env
   ```
3. Open `backend/.env` in any text editor and paste your API key:
   ```env
   # --- AI & LLM Provider Keys ---
   GEMINI_API_KEY=AIzaSyYourGeminiApiKeyGoesHere
   GEMINI_MODEL=gemini-1.5-flash

   # --- Security & JWT Settings ---
   SECRET_KEY=careagent_super_secret_jwt_key_2026_healthcare_phi
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440

   # --- Database ---
   DATABASE_URL=sqlite:///./careagent.db
   ```
4. Get your free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
5. `.env` is automatically added to `.gitignore` so your secret keys are never committed to version control.

---

## 🌐 Frontend ↔ Backend Routing Architecture

CareAgent uses a clean, decoupled routing architecture:

```
[Browser / React UI: Port 3000]
        │
        ▼
   apiClient (frontend/src/services/api.js)
        │
        ▼ (proxied via Vite dev server)
[Vite Proxy: /api/* ──► http://127.0.0.1:8000/api/*]
        │
        ▼
[FastAPI Backend: Port 8000]
   ├── /api/auth/*             (Authentication & JWT tokens)
   ├── /api/chat/*             (Agentic AI Orchestrator)
   ├── /api/patients/*         (FHIR Patient Profile & Conditions)
   ├── /api/reports/*          (Diagnostic Labs & Trend Deltas)
   ├── /api/appointments/*     (2-Step Stage & Confirm Booking)
   ├── /api/medications/*      (Prescriptions & Adherence Tracking)
   ├── /api/doctor/*           (Physician Roster, AI Briefing, Rx Authorize)
   ├── /api/vitals/*           (Biometrics Logging & Alert Evaluation)
   ├── /api/notifications/*    (In-App Push Feed & Preferences)
   └── /api/health/*           (Health Score Dashboard & Risk Stratification)
```

- **Frontend API Service:** `frontend/src/services/api.js` encapsulates all fetch calls, automatically injecting the Bearer JWT token and handling error states.
- **Vite Proxy:** `frontend/vite.config.js` forwards all `/api` requests to `http://127.0.0.1:8000` with WebSocket support and CORS compatibility.
- **Backend CORS:** `backend/main.py` allows origins `*`, `http://localhost:3000`, `http://localhost:5173`.

---

## 🚀 Quickstart

### Prerequisites
- Python 3.11+
- Node.js 18+
- (Optional) A valid **Google Gemini API key**

### 1. Configure Environment
```bash
# In backend/ folder
cd backend
cp .env.example .env
# Edit .env and paste your GEMINI_API_KEY
```

### 2. Backend — FastAPI
```bash
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --port 8000 --reload
```
> 📖 Interactive Swagger docs: **http://localhost:8000/docs**

### 3. Frontend — React + Vite
```bash
cd frontend
npm install
npm run dev
```
> 🌐 App: **http://localhost:3000**

### 4. One-Shot (Both Servers)
```bash
python run_servers.py
```


---

## 🧪 Testing

```bash
python -m pytest backend/tests/test_backend.py -v
```

| Test Case | Description |
|---|---|
| 🚨 Emergency Triage | Validates short-circuit response for acute symptom keywords |
| 💊 Medication Safety | Confirms non-prescription guardrail is architecturally enforced |
| 📅 Appointment Gating | Validates 2-step uncommitted → confirmed booking flow |
| 🧬 Lab Delta Analysis | Checks longitudinal trend calculations against reference ranges |
| 📊 Adherence Logging | Verifies Taken/Skipped/Late logging and adherence % computation |
| 🔐 RBAC Enforcement | Tests that patient endpoints reject doctor tokens and vice versa |

---

## 📁 Project Structure

```
careagent/
│
├── backend/
│   ├── main.py                          # FastAPI app, router registration, health endpoint
│   ├── requirements.txt                 # Python dependencies
│   │
│   └── app/
│       ├── __init__.py
│       │
│       ├── api/                         # ── FastAPI Routers (one file per domain) ──
│       │   ├── __init__.py
│       │   ├── auth.py                  # POST /login, POST /switch-demo-role, GET /me
│       │   ├── chat.py                  # POST /chat/send → Orchestrator
│       │   ├── patients.py              # GET /profile, GET /conditions
│       │   ├── reports.py               # GET /latest, GET /trends, POST /upload
│       │   ├── appointments.py          # GET /slots, POST /stage, POST /confirm, DELETE /{id}
│       │   ├── medications.py           # GET /prescribed, GET /schedule, POST /adherence/log
│       │   ├── doctor.py                # GET /patients, GET /ai-briefing, POST /prescriptions/authorize
│       │   ├── vitals.py                # ★ NEW: POST /log, GET /history, GET /summary, GET /alerts
│       │   ├── notifications.py         # ★ NEW: GET /, POST /read-all, GET|PUT /preferences
│       │   └── health_summary.py        # ★ NEW: GET /dashboard, GET /risk-stratification
│       │
│       ├── agents/                      # ── Clinical AI Agents ──
│       │   ├── __init__.py
│       │   ├── orchestrator.py          # Master intent router + emergency short-circuit
│       │   ├── safety_guard.py          # Emergency triage & medication safety invariant
│       │   ├── ehr_agent.py             # FHIR EHR records, lab value extraction, trend deltas
│       │   ├── appointment_agent.py     # Slot search, stage/confirm two-step booking
│       │   ├── medication_agent.py      # Regimen management, adherence logging
│       │   ├── vitals_agent.py          # ★ NEW: Vital trend analysis, anomaly detection
│       │   └── notification_agent.py   # ★ NEW: Template-driven push notifications
│       │
│       ├── models/                      # ── Pydantic Schemas (typed API contracts) ──
│       │   ├── __init__.py
│       │   ├── fhir_models.py           # Core HL7 FHIR resource models
│       │   ├── schemas_auth.py          # LoginRequest, TokenResponse, UserProfile
│       │   ├── schemas_chat.py          # ChatMessageRequest, AgentChatResponse
│       │   ├── schemas_appointments.py  # StageBookingRequest, AppointmentRecord, etc.
│       │   ├── schemas_medications.py   # MedicationRecord, LogAdherenceRequest (enum status)
│       │   ├── schemas_doctor.py        # NewPrescriptionRequest, AIBriefingResponse, AuditLogEntry
│       │   ├── schemas_reports.py       # LabObservation, LabTrendAnalysis, LabUploadResponse
│       │   ├── schemas_vitals.py        # ★ NEW: LogVitalRequest, VitalReading, VitalsTrendResponse
│       │   └── schemas_notifications.py # ★ NEW: NotificationRecord, NotificationPreferenceRequest
│       │
│       ├── core/                        # ── App Configuration & Security ──
│       │   ├── __init__.py
│       │   ├── config.py                # Pydantic Settings (env vars, JWT config)
│       │   └── security.py              # JWT creation/validation, RBAC guards, DEMO_USERS
│       │
│       └── db/                          # ── In-Memory FHIR Datastore ──
│           ├── __init__.py
│           └── database.py              # HospitalDatabase: patients, labs, meds, vitals, notifs
│
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── src/
│       ├── App.jsx                      # Main app with Patient + Doctor portal tabs
│       ├── main.jsx                     # React entry point
│       ├── index.css                    # Global styles
│       └── services/
│           └── api.js                   # ★ Centralized API client service (JWT, endpoints, error handling)

│
├── backend/tests/
│   └── test_backend.py                  # Full pytest test suite
│
├── run_servers.py                       # Concurrent backend + frontend launcher
└── README.md
```

---

## 🔒 Safety & Compliance Design

CareAgent follows **safety-by-architecture**, not safety-by-prompt:

| Guarantee | Implementation |
|---|---|
| 🚨 Emergency escalation | Hard-coded short-circuit rule runs *before any LLM call* in the orchestrator |
| 💊 No medication prescribing | Invariant check at agent boundary — LLM output is validated and overridden if it contains prescriptions |
| 📅 No blind appointment commits | Staging and confirming are separate API calls; the patient must explicitly hit `POST /confirm` |
| 🔐 RBAC per route | `require_role("doctor")` dependency guard on all clinician endpoints |
| 📋 HIPAA audit log | Append-only list in-memory (production: encrypted, tamper-evident DB); no agent can delete entries |
| 📊 Vital critical alerts | Rule-based classification runs server-side independent of any AI model |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built with ❤️ for safer, smarter healthcare · **CareAgent v2.0** © 2026

</div>

