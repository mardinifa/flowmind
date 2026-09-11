# FlowMind Integration & Orchestration Guide

**Target Audience:** n8n Workflow Engineers, Backend Developers, and DevOps  
**Client:** ClearPath Capital (Lagos, Nigeria)

---

## 1. End-to-End Orchestration Architecture

```mermaid
sequenceDiagram
    autonumber
    participant Form as Application Portal / Typeform
    participant n8n as n8n Orchestrator (Docker)
    participant API as FastAPI Backend (host.docker.internal:8000)
    participant Guard as Anti-Hallucination Guardrail
    participant DB as Supabase / SQLite
    participant Dash as Streamlit Review Queue

    Form->>n8n: Webhook Trigger (Form payload + PDF)
    n8n->>API: POST /api/v1/applications/process
    API->>API: Stage 1: Document Intake (PyMuPDF)
    API->>API: Stage 2: Eligibility Rules (4 Criteria)
    API->>API: Stage 3: Risk & Fraud Classifier
    alt Clearly Eligible or Ineligible
        API->>Guard: validate_letter(generated_letter, record)
        alt Guardrail Passed
            Guard-->>API: Safe to send -> Status: auto_approved / auto_declined
        else Hallucination Detected
            Guard-->>API: BLOCKED -> Escalate to human review
        end
    else Ambiguous Case
        API->>API: Generate Loan Officer Briefing -> Status: escalated
    end
    API->>DB: Persist Application Record & Status
    API-->>n8n: 200 OK (Workflow Result & Routing Details)
    alt Status == escalated
        Dash->>DB: Load escalated queue & briefings
        Dash-->>Dash: Loan Officer approves/declines/requests info
        Dash->>DB: Save decision & audit trail
    end
```

---

## 2. Docker & Network Configuration for n8n

When hosting n8n in Docker while FastAPI runs locally on host:

### Issue:
`localhost:8000` inside an n8n Docker container attempts to connect to the container's own loopback interface, resulting in `ECONNREFUSED`.

### Solution:
In n8n **HTTP Request** node:
- **URL:** `http://host.docker.internal:8000/api/v1/applications/process`
- **Method:** `POST`
- **Send Body:** JSON (Expression: `{{ $json }}`)
- **Header:** `Content-Type: application/json`

---

## 3. Running Backend Services

### 1. Start FastAPI Webhook Server:
```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive OpenAPI Docs: `http://localhost:8000/docs`

### 2. Start Streamlit Review Dashboard:
```bash
python -m streamlit run dashboard/app.py --server.port 8501
```
Dashboard UI: `http://localhost:8501`

### 3. Run Automated Integration Suite:
```bash
python -m pytest tests/test_full_integration.py -v
```
