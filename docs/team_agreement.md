# FlowMind Team Integration Agreement

**Project:** ClearPath Capital - FlowMind (Expadox Lab Project 3)  
**Version:** 1.0.0 (Day 6 Full Integration)

---

## 1. Team Responsibilities & Ownership

| Team Role | Core Responsibility | Primary Module(s) |
| :--- | :--- | :--- |
| **Person 1 (Intake)** | PDF Document Ingestion, PyMuPDF Extraction, Edge Cases (Scanned/Truncated PDFs) | `src/intake/pdf_extractor.py` |
| **Person 2 (Eligibility)** | 4 Independent Eligibility Criteria Rules & Threshold Enforcement | `src/eligibility/rules.py` |
| **Person 3 (Risk & LLM)** | Risk Classification, Self-Consistency, Explanation Quality & Fraud Detection | `src/risk/classifier.py`, `src/risk/fraud_detector.py` |
| **Person 4 (Orchestration & UI)**| n8n Webhooks, FastAPI, Anti-Hallucination Guardrail, Database & Streamlit Dashboard | `api/main.py`, `src/actions/`, `dashboard/app.py`, `db/database.py` |

---

## 2. Standardized Function Signatures

All components MUST adhere to these exact function signatures:

### Intake:
```python
def extract_text_from_pdf(pdf_source: Union[bytes, str, io.BytesIO]) -> DocumentIntakeResult: ...
```

### Eligibility:
```python
def check_business_registration(record: Dict[str, Any]) -> CriterionResult: ...
def check_applicant_age(record: Dict[str, Any]) -> CriterionResult: ...
def check_turnover_ratio(record: Dict[str, Any]) -> CriterionResult: ...
def check_loan_purpose(record: Dict[str, Any]) -> CriterionResult: ...
def evaluate_all_eligibility(record: Dict[str, Any]) -> EligibilityAssessment: ...
```

### Risk & Fraud:
```python
def classify_risk(record: Dict[str, Any]) -> RiskAssessment: ...
def check_identity_and_name_consistency(record: Dict[str, Any]) -> Tuple[bool, List[str], str]: ...
```

### Actions & Guardrails:
```python
def generate_conditional_approval_letter(record: Dict[str, Any]) -> str: ...
def generate_decline_letter(record: Dict[str, Any], failed_criteria_details: List[str] = None) -> str: ...
def validate_letter(letter: str, record: Dict[str, Any]) -> LetterValidationResult: ...
```

### Briefing:
```python
def generate_escalation_briefing(record: Dict[str, Any], eligibility: EligibilityAssessment, risk: RiskAssessment, ...) -> EscalationBriefing: ...
```

### Database Helpers:
```python
def load_briefing(application_id: str) -> str: ...
def save_human_decision(application_id: str, decision: str, officer_id: str = "officer_1", notes: str = "") -> Dict[str, Any]: ...
def update_status(application_id: str, status: str) -> Dict[str, Any]: ...
def get_dashboard_metrics() -> Dict[str, Any]: ...
```

---

## 3. Database Schema Agreement (`applications` Table)

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `id` | `TEXT PRIMARY KEY` | Unique application identifier (`APP-YYYYMMDD-XXXXXX`) |
| `applicant_name` | `TEXT NOT NULL` | Full legal name of applicant |
| `applicant_age` | `INTEGER NOT NULL` | Age in years (21-65) |
| `business_name` | `TEXT NOT NULL` | Registered trading name |
| `business_registration_number` | `TEXT` | CAC RC or BN registration number |
| `operating_months` | `INTEGER NOT NULL` | Verified duration of operations |
| `loan_amount` | `REAL NOT NULL` | Requested loan principal in NGN (₦) |
| `monthly_turnover` | `REAL NOT NULL` | Average monthly turnover in NGN (₦) |
| `purpose` | `TEXT NOT NULL` | Description of loan utilization |
| `purpose_category` | `TEXT NOT NULL` | Categorized purpose (e.g. `inventory_purchase`) |
| `bank_statement_account_name`| `TEXT` | Name on financial bank statement |
| `status` | `TEXT NOT NULL` | `submitted`, `auto_approved`, `auto_declined`, `escalated`, `human_approved`, `human_declined`, `human_info_requested` |
| `ai_recommendation` | `TEXT` | Decision recommendation produced by AI pipeline |
| `briefing_text` | `TEXT` | Markdown briefing generated for loan officers |
| `generated_letter` | `TEXT` | Full letter text (approval or decline) |
| `letter_validation_status` | `TEXT` | `passed`, `flagged_hallucination`, `not_generated` |
| `human_decision` | `TEXT` | Decision recorded by human loan officer |
| `officer_id` | `TEXT` | ID of reviewing officer |
| `human_notes` | `TEXT` | Justification or verification notes |
| `is_override` | `INTEGER` | `1` if human reversed AI recommendation, `0` otherwise |
| `created_at` | `TEXT NOT NULL` | ISO 8601 timestamp |
| `updated_at` | `TEXT NOT NULL` | ISO 8601 timestamp |

---

## 4. Integration Gotchas & Troubleshooting Guide

1. **n8n Container Network Call to FastAPI:**
   - When n8n runs inside Docker, calling `http://localhost:8000` refers to the container itself.
   - **Fix:** Always use `http://host.docker.internal:8000/api/v1/applications/process` in n8n HTTP Request nodes.

2. **Application ID Uniqueness:**
   - Submissions must never overwrite existing IDs.
   - **Fix:** Pipeline generates `APP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}` if no unique ID is passed.

3. **Ollama LLM Latency & Availability:**
   - In offline/demo environments, Ollama may take seconds or be unavailable.
   - **Fix:** FlowMind incorporates deterministic self-consistency and semantic explanation analyzers with zero external dependency requirements.
