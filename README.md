# FlowMind: Intelligent Credit Workflow Automation with Human-in-the-Loop

**Expadox Lab · AI Automation · Project 3**  
**Client:** ClearPath Capital (Lagos, Nigeria)

FlowMind is a production-grade credit underwriting and workflow automation system designed for microfinance institutions. It processes incoming small-business loan applications, autonomously approves or declines straightforward high-confidence cases, enforces deterministic anti-hallucination guardrails on all outgoing letters, and generates structured briefings for human loan officers on complex edge cases.

---

## 🚀 Key Features

1. **Intake & Resilient Extraction**: PyMuPDF-based intake handling standard PDFs, flat-scanned image-only PDFs, and truncated byte streams without crashing.
2. **Four Independent Eligibility Rules**:
   - Business Registration (`>= 12 months`)
   - Applicant Age (`21 to 65 years`)
   - Turnover Ratio (`Loan <= 10x monthly turnover`)
   - Productive Loan Purpose Check
3. **Qualitative Risk & Fraud Anomaly Detection**:
   - Two-factor confidence scoring (Self-consistency + Explanation quality)
   - Identity and bank statement name mismatch detection
4. **Anti-Hallucination Letter Guardrail (`validate_letter`) [Deliverable D4]**:
   - Verifies every monetary number, operating duration, and date claim before sending.
   - Blocks automated dispatch and flags letters for human review if any claim cannot be verified.
5. **Streamlit Human-in-the-Loop Dashboard [Deliverable D6]**:
   - **Loan Officer Review Queue**: Real-time queue of escalated applications with structured briefings and 1-click decisions (`Approve`, `Decline`, `Request More Info`).
   - **Admin Intelligence & Calibration**: Automated tracking of `% Handled Autonomously`, `% Escalated`, and **`Human Override Rate`**.
   - **Guardrails & Simulation Sandbox**: Interactive testing suite for deliberate failure injection, PDF edge cases, and fraud detection.

---

## 🛠️ Project Structure

```
Flowmind/
├── config/
│   ├── __init__.py
│   └── thresholds.py              # Operational limits & calibration telemetry
├── db/
│   ├── __init__.py
│   ├── database.py                # Supabase client + SQLite fallback
│   └── seed_data.py               # Sample SME applications
├── src/
│   ├── models.py                  # Pydantic schemas
│   ├── intake/
│   │   └── pdf_extractor.py       # Resilient PyMuPDF parser
│   ├── eligibility/
│   │   └── rules.py               # 4 testable eligibility criteria
│   ├── risk/
│   │   ├── classifier.py          # Risk & 2-factor confidence
│   │   └── fraud_detector.py      # Identity mismatch detector
│   ├── actions/
│   │   ├── letter_generator.py    # Approval & decline notices
│   │   └── letter_validator.py    # Anti-hallucination guardrail (validate_letter)
│   ├── briefing/
│   │   └── briefing_generator.py  # Structured loan officer briefings
│   └── pipeline.py                # End-to-end orchestrator
├── dashboard/
│   ├── app.py                     # Streamlit application
│   └── styles.css                 # Custom theme styling
├── docs/
│   ├── decision_logic.md          # D1 Decision logic
│   ├── edge_cases.md              # Edge cases & fault tolerance report
│   └── deliverables/
│       ├── D4_autonomous_action_outputs.md
│       └── D6_streamlit_dashboard.md
├── tests/
│   ├── test_letter_validator.py   # D4 Deliberate failure tests
│   ├── test_intake_edge_cases.py  # Scanned & truncated PDF tests
│   ├── test_fraud_detection.py    # Fraud & name mismatch tests
│   ├── test_eligibility.py        # 4 criteria tests
│   └── test_calibration.py        # Calibration telemetry tests
├── requirements.txt
└── README.md
```

---

## 🧪 Running Automated Tests

Run the complete test suite:
```bash
python -m pytest tests/ -v
```

All 18 tests execute in `< 0.5s` and validate:
- Anti-hallucination letter guardrail and deliberate failure injection (`test_deliberate_failure_injected_operating_tenure`)
- Scanned and truncated PDF intake edge cases (`test_scanned_image_only_pdf_fails_gracefully`, `test_truncated_corrupt_pdf_fails_gracefully`)
- Name mismatch fraud detection (`test_fraudulent_name_mismatch_application`)
- Eligibility boundary conditions and calibration telemetry.

---

## 🖥️ Launching the Streamlit Dashboard

Run the Streamlit application:
```bash
streamlit run dashboard/app.py
```

Open `http://localhost:8501` in your browser to interact with:
1. **Loan Officer Queue**: Review briefings and decide on escalated applications.
2. **Admin & Metrics**: Track autonomous rate, escalation rate, and human override telemetry.
3. **Guardrails & Simulation Lab**: Test edge cases and injected hallucinations in real time.
