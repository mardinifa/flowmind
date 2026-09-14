# FlowMind: Intelligent Credit Workflow Automation

**Human-in-the-Loop Loan Processing Prototype**

**Expadox Lab - AI Automation - Project 3**

**Fictional client: ClearPath Capital, Lagos, Nigeria**

## Overview

FlowMind processes small-business loan applications, handles straightforward
high-confidence cases autonomously and escalates uncertain or complex cases to
human loan officers.

The system combines deterministic eligibility rules, qualitative risk
classification, document checks, factual letter validation and a Streamlit
human-review dashboard.

FlowMind is an educational prototype, not a production credit-scoring system.

## Main Features

- PDF intake using PyMuPDF
- Detection of scanned and corrupted documents
- Operating-duration cross-validation
- Four independent eligibility rules
- Low, Medium and High qualitative risk classification
- Identity and bank-account name consistency checking
- Confidence-based decision routing
- Conditional approval and decline-letter generation
- Anti-hallucination letter validation
- Human escalation briefings
- Streamlit loan-officer dashboard
- FastAPI application endpoints
- SQLite development database with Supabase-compatible access
- Calibration and human-override metrics
- 36 automated tests
- 20-application Day 8 stress test

## Decision Outcomes

FlowMind routes each application to one of three primary outcomes:

- `auto_approved`
- `auto_declined`
- `escalated`

Escalated applications can later become:

- `human_approved`
- `human_declined`
- `human_info_requested`

## Project Structure

```text
flowmind/
|-- api/
|   `-- main.py
|-- config/
|   `-- thresholds.py
|-- dashboard/
|   |-- app.py
|   `-- styles.css
|-- db/
|   |-- database.py
|   |-- flowmind.db
|   `-- seed_data.py
|-- docs/
|   |-- architecture.md
|   |-- decision_logic.md
|   |-- eligibility_and_letters.md
|   |-- intake_pipeline.md
|   |-- risk_and_confidence.md
|   |-- user_guide.md
|   `-- deliverables/
|       |-- D4_autonomous_action_outputs.md
|       |-- D6_streamlit_dashboard.md
|       |-- D7_integration_loop.md
|       `-- D7_stress_test_results.md
|-- src/
|   |-- actions/
|   |-- briefing/
|   |-- eligibility/
|   |-- intake/
|   |-- risk/
|   |-- models.py
|   `-- pipeline.py
|-- tests/
|   |-- stress_test_day8.py
|   |-- test_api_endpoints.py
|   |-- test_calibration.py
|   |-- test_day7_challenges.py
|   |-- test_eligibility.py
|   |-- test_fraud_detection.py
|   |-- test_full_integration.py
|   |-- test_intake_edge_cases.py
|   |-- test_letter_validator.py
|-- scripts/
|   `-- manual_letters_demo.py
|-- requirements.txt
`-- README.md
```
