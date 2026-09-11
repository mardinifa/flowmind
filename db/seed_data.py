"""
Database Seeding Script for ClearPath Capital FlowMind
Populates sample loan applications across all workflow states.
"""

from db.database import supabase
from datetime import datetime, timedelta

SAMPLE_APPLICATIONS = [
    # 1. Escalated - High loan to turnover ratio (Borderline eligibility)
    {
        "id": "APP-2026-001",
        "applicant_name": "Amina Yusuf",
        "applicant_age": 34,
        "business_name": "Yusuf Textiles & Tailoring",
        "business_registration_number": "RC-1849201",
        "operating_months": 28,
        "loan_amount": 3500000.0,
        "monthly_turnover": 380000.0,
        "purpose": "Bulk purchase of imported fabrics and two commercial embroidery machines for holiday rush season.",
        "purpose_category": "inventory_purchase",
        "bank_statement_account_name": "Yusuf Textiles & Tailoring",
        "status": "escalated",
        "ai_recommendation": "Escalate for manual debt service ratio check (Loan is 9.2x turnover, near 10x cap).",
        "briefing_text": """### FlowMind Escalation Briefing: Yusuf Textiles & Tailoring
**Applicant:** Amina Yusuf | **Loan Amount:** ₦3,500,000 | **Monthly Turnover:** ₦380,000

#### Eligibility Checklist:
- [x] **Business Registration:** PASSED (Registered 28 months, RC-1849201).
- [x] **Applicant Age:** PASSED (Age 34, valid range 21-65).
- [!] **Turnover Ratio:** AMBIGUOUS / HIGH (₦3,500,000 / ₦380,000 = 9.2x. Passes <10x ceiling but exceeds standard 6.0x safe comfort band).
- [x] **Loan Purpose:** PASSED (Inventory & Equipment acquisition).

#### Risk Assessment & Reasoning:
- **Risk Level:** Medium (Confidence: 0.72)
- **LLM Reasoning:** The business has steady cashflow but debt burden is high relative to demonstrated cash buffers. Stated vendor contracts in Lagos Island textile market appear credible.

#### Core Ambiguity:
- System cannot verify if seasonal spikes in turnover compensate for tighter monthly margins during off-peak quarters.

#### Recommended Action:
- Officer review required: Request 3 additional months of bank statements or approve with reduced principal of ₦2,500,000.""",
        "generated_letter": None,
        "letter_validation_status": None,
        "human_decision": None,
        "officer_id": None,
        "human_notes": None,
        "is_override": 0,
        "created_at": (datetime.now() - timedelta(hours=4)).isoformat(),
        "updated_at": (datetime.now() - timedelta(hours=4)).isoformat(),
    },
    # 2. Escalated - High Risk Fraud / Name Mismatch (Crucial test case from prompt)
    {
        "id": "APP-2026-002",
        "applicant_name": "Tunde Bakare",
        "applicant_age": 42,
        "business_name": "Bakare Agro Allied Ventures",
        "business_registration_number": "RC-2938102",
        "operating_months": 22,
        "loan_amount": 5000000.0,
        "monthly_turnover": 950000.0,
        "purpose": "Procurement of fertilizers and grain storage silos in Ogun state.",
        "purpose_category": "agriculture_supply",
        "bank_statement_account_name": "Apex Global Logistics Ltd",  # Mismatch!
        "status": "escalated",
        "ai_recommendation": "Decline or escalate for KYC verification (Critical identity mismatch).",
        "briefing_text": """### FlowMind Escalation Briefing: Bakare Agro Allied Ventures
**Applicant:** Tunde Bakare | **Loan Amount:** ₦5,000,000 | **Monthly Turnover:** ₦950,000

#### Eligibility Checklist:
- [x] **Business Registration:** PASSED (22 months operating).
- [x] **Applicant Age:** PASSED (Age 42).
- [x] **Turnover Ratio:** PASSED (₦5.0M / ₦950k = 5.26x).
- [x] **Loan Purpose:** PASSED (Agriculture supply).

#### Risk Assessment & Reasoning:
- **Risk Level:** High (Confidence: 0.94)
- **LLM Reasoning:** CRITICAL ANOMALY: Bank statement account name ('Apex Global Logistics Ltd') completely conflicts with the applicant and registered business ('Bakare Agro Allied Ventures / Tunde Bakare').

#### Core Ambiguity:
- Third-party bank statements submitted without verifiable power of attorney or subsidiary documentation. High probability of fabricated financial evidence.

#### Recommended Action:
- Decline immediately or issue formal Request for Explanation regarding third-party financial records.""",
        "generated_letter": None,
        "letter_validation_status": None,
        "human_decision": None,
        "officer_id": None,
        "human_notes": None,
        "is_override": 0,
        "created_at": (datetime.now() - timedelta(hours=6)).isoformat(),
        "updated_at": (datetime.now() - timedelta(hours=6)).isoformat(),
    },
    # 3. Escalated - Scanned PDF / Incomplete OCR Intake
    {
        "id": "APP-2026-003",
        "applicant_name": "Chioma Eze",
        "applicant_age": 29,
        "business_name": "Chioma Cold Room & Seafoods",
        "business_registration_number": "BN-9928172",
        "operating_months": 15,
        "loan_amount": 2000000.0,
        "monthly_turnover": 450000.0,
        "purpose": "Purchase of a backup solar power inverter and commercial deep freezers.",
        "purpose_category": "equipment_acquisition",
        "bank_statement_account_name": "Chioma Cold Room & Seafoods",
        "status": "escalated",
        "ai_recommendation": "Escalate for manual document inspection (Scanned image PDF attached).",
        "briefing_text": """### FlowMind Escalation Briefing: Chioma Cold Room & Seafoods
**Applicant:** Chioma Eze | **Loan Amount:** ₦2,000,000 | **Monthly Turnover:** ₦450,000

#### Eligibility Checklist:
- [x] **Business Registration:** PASSED (15 months).
- [x] **Applicant Age:** PASSED (Age 29).
- [x] **Turnover Ratio:** PASSED (₦2.0M / ₦450k = 4.44x).
- [x] **Loan Purpose:** PASSED (Equipment acquisition).

#### Risk Assessment & Reasoning:
- **Risk Level:** Medium (Confidence: 0.55)
- **Extraction Flag:** PyMuPDF detected an image-only / flat-scanned PDF for the tax certificate with zero selectable text layer. Automated document parsing confidence degraded.

#### Core Ambiguity:
- Document image quality requires manual human verification to confirm official CAC tax stamp before disbursement.

#### Recommended Action:
- Loan officer visually inspect attached PDF image or request digital statement download.""",
        "generated_letter": None,
        "letter_validation_status": None,
        "human_decision": None,
        "officer_id": None,
        "human_notes": None,
        "is_override": 0,
        "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
        "updated_at": (datetime.now() - timedelta(hours=2)).isoformat(),
    },
    # 4. Auto Approved - Clean low risk
    {
        "id": "APP-2026-004",
        "applicant_name": "Emeka Nnamdi",
        "applicant_age": 39,
        "business_name": "Nnamdi Auto Spares Ltd",
        "business_registration_number": "RC-4482019",
        "operating_months": 48,
        "loan_amount": 2500000.0,
        "monthly_turnover": 850000.0,
        "purpose": "Inventory restocking for Japanese and German brake pads and suspension kits.",
        "purpose_category": "inventory_purchase",
        "bank_statement_account_name": "Nnamdi Auto Spares Ltd",
        "status": "auto_approved",
        "ai_recommendation": "Autonomous Approval",
        "briefing_text": "Processed autonomously. Passed all 4 criteria with 100% confidence. Risk: Low (0.96).",
        "generated_letter": "Dear Emeka Nnamdi,\n\nWe are pleased to inform you that your loan application of ₦2,500,000 for Nnamdi Auto Spares Ltd has received conditional approval. Your business has operated successfully for 48 months with demonstrated monthly turnover of ₦850,000.\n\nClearPath Capital Team",
        "letter_validation_status": "passed",
        "human_decision": None,
        "officer_id": None,
        "human_notes": None,
        "is_override": 0,
        "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
        "updated_at": (datetime.now() - timedelta(days=1)).isoformat(),
    },
    # 5. Auto Declined - Failed operating time & prohibited purpose
    {
        "id": "APP-2026-005",
        "applicant_name": "Femi Adeleke",
        "applicant_age": 24,
        "business_name": "CryptoWave Ventures",
        "business_registration_number": "BN-1029384",
        "operating_months": 4,  # Failed (< 12 months)
        "loan_amount": 4000000.0,
        "monthly_turnover": 200000.0,  # Failed (20x turnover)
        "purpose": "Arbitrage trading on cryptocurrency exchange markets.",  # Prohibited
        "purpose_category": "cryptocurrency",
        "bank_statement_account_name": "CryptoWave Ventures",
        "status": "auto_declined",
        "ai_recommendation": "Autonomous Decline",
        "briefing_text": "Processed autonomously. Failed 3 criteria: operating tenure (4 mos < 12 mos), turnover ratio (20x > 10x max), and prohibited loan purpose.",
        "generated_letter": "Dear Femi Adeleke,\n\nThank you for applying to ClearPath Capital. We regret to inform you that your application for ₦4,000,000 for CryptoWave Ventures cannot be approved because your business has operated for 4 months (minimum 12 months required) and the requested purpose (cryptocurrency) is not within our approved categories.\n\nClearPath Capital Team",
        "letter_validation_status": "passed",
        "human_decision": None,
        "officer_id": None,
        "human_notes": None,
        "is_override": 0,
        "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
        "updated_at": (datetime.now() - timedelta(days=2)).isoformat(),
    },
    # 6. Human Approved after Escalation
    {
        "id": "APP-2026-006",
        "applicant_name": "Folashade Alabi",
        "applicant_age": 45,
        "business_name": "Alabi Pharmacy & Supermarket",
        "business_registration_number": "RC-8819203",
        "operating_months": 36,
        "loan_amount": 4000000.0,
        "monthly_turnover": 600000.0,
        "purpose": "Bulk purchase of pharmaceuticals and medical consumables ahead of monsoon season.",
        "purpose_category": "inventory_purchase",
        "bank_statement_account_name": "Alabi Pharmacy & Supermarket",
        "status": "human_approved",
        "ai_recommendation": "Escalate for verification of NAFDAC pharmaceutical licenses.",
        "briefing_text": "Escalated for license check. Passed criteria.",
        "generated_letter": None,
        "letter_validation_status": None,
        "human_decision": "human_approved",
        "officer_id": "officer_1",
        "human_notes": "Verified active NAFDAC pharmacist certification and confirmed excellent repayment history on previous credit line.",
        "is_override": 0,
        "created_at": (datetime.now() - timedelta(days=3)).isoformat(),
        "updated_at": (datetime.now() - timedelta(days=2, hours=22)).isoformat(),
    },
    # 7. Human Override (AI recommended decline due to turnover ratio, officer approved with collateral)
    {
        "id": "APP-2026-007",
        "applicant_name": "Ibrahim Danjuma",
        "applicant_age": 51,
        "business_name": "Danjuma Rice Mills & Processing",
        "business_registration_number": "RC-3920194",
        "operating_months": 60,
        "loan_amount": 6000000.0,
        "monthly_turnover": 550000.0,
        "purpose": "Diesel generator maintenance and bulk paddy rice purchase.",
        "purpose_category": "working_capital",
        "bank_statement_account_name": "Danjuma Rice Mills",
        "status": "human_approved",
        "ai_recommendation": "Decline (Ratio 10.9x exceeds 10x ceiling).",
        "briefing_text": "Turnover ratio 10.9x is slightly over 10x threshold.",
        "generated_letter": None,
        "letter_validation_status": None,
        "human_decision": "human_approved",
        "officer_id": "officer_2",
        "human_notes": "OVERRIDE: Applicant provided verified landed property C of O in Ikeja as additional security. Approved subject to legal charge.",
        "is_override": 1,
        "created_at": (datetime.now() - timedelta(days=4)).isoformat(),
        "updated_at": (datetime.now() - timedelta(days=3, hours=18)).isoformat(),
    },
]

def seed_sample_data(reset: bool = False):
    """Inserts sample applications into database."""
    if reset:
        supabase.table("applications").delete().execute()
        supabase.table("decisions_audit").delete().execute()

    for app in SAMPLE_APPLICATIONS:
        supabase.table("applications").insert(app).execute()

    print(f"Successfully seeded {len(SAMPLE_APPLICATIONS)} sample applications.")

if __name__ == "__main__":
    seed_sample_data(reset=True)
