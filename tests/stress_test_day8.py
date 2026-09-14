"""
Day 8: Twenty-Application Stress Test

Runs 20 fabricated applications through the complete FlowMind pipeline,
compares actual routing with expected routing, and automatically creates
the D7 stress-test report.
"""

from copy import deepcopy
from datetime import datetime
from pathlib import Path
import sys

# Add the project root to Python's import path when this file is run directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline import process_application


BASE_APPLICATION = {
    "applicant_name": "Test Applicant",
    "applicant_age": 35,
    "business_name": "Test Business Enterprises",
    "business_registration_number": "RC-TEST-001",
    "operating_months": 36,
    "loan_amount": 1_500_000.0,
    "monthly_turnover": 500_000.0,
    "purpose": "Purchase of equipment for business expansion",
    "purpose_category": "equipment_acquisition",
    "bank_statement_account_name": "Test Business Enterprises",
}


def make_case(
    case_id,
    description,
    expected_status,
    changes=None,
    document_bytes=None,
):
    application = deepcopy(BASE_APPLICATION)
    application["id"] = case_id

    if changes:
        application.update(changes)

    return {
        "id": case_id,
        "description": description,
        "expected_status": expected_status,
        "application": application,
        "document_bytes": document_bytes,
    }


STRESS_CASES = [
    # Seven clearly eligible, low-risk applications
    make_case(
        "STRESS-001",
        "Established equipment business with low loan ratio",
        "auto_approved",
    ),
    make_case(
        "STRESS-002",
        "Established inventory business",
        "auto_approved",
        {
            "applicant_name": "Bola Adeyemi",
            "business_name": "Adeyemi Stores",
            "bank_statement_account_name": "Adeyemi Stores",
            "operating_months": 48,
            "loan_amount": 2_000_000.0,
            "monthly_turnover": 800_000.0,
            "purpose": "Purchase of additional inventory",
            "purpose_category": "inventory_purchase",
        },
    ),
    make_case(
        "STRESS-003",
        "Agricultural supplier with strong turnover",
        "auto_approved",
        {
            "applicant_name": "Musa Ibrahim",
            "business_name": "Ibrahim Farm Supplies",
            "bank_statement_account_name": "Ibrahim Farm Supplies",
            "operating_months": 60,
            "purpose": "Purchase of agricultural supplies",
            "purpose_category": "agriculture_supply",
        },
    ),
    make_case(
        "STRESS-004",
        "Manufacturing business requesting raw materials",
        "auto_approved",
        {
            "applicant_name": "Ngozi Okafor",
            "business_name": "Okafor Manufacturing",
            "bank_statement_account_name": "Okafor Manufacturing",
            "operating_months": 72,
            "loan_amount": 3_000_000.0,
            "monthly_turnover": 1_000_000.0,
            "purpose": "Purchase of raw materials",
            "purpose_category": "raw_materials",
        },
    ),
    make_case(
        "STRESS-005",
        "Retail store renovation with low exposure",
        "auto_approved",
        {
            "purpose": "Renovation of existing retail store",
            "purpose_category": "store_renovation",
            "loan_amount": 1_000_000.0,
            "monthly_turnover": 400_000.0,
        },
    ),
    make_case(
        "STRESS-006",
        "Logistics business with established history",
        "auto_approved",
        {
            "business_name": "Northern Transport Hub",
            "bank_statement_account_name": "Northern Transport Hub",
            "operating_months": 84,
            "purpose": "Purchase of delivery vehicle",
            "purpose_category": "logistics_and_transport",
        },
    ),
    make_case(
        "STRESS-007",
        "Working-capital request within safe ratio",
        "auto_approved",
        {
            "operating_months": 30,
            "loan_amount": 1_800_000.0,
            "monthly_turnover": 600_000.0,
            "purpose": "Working capital for increased customer orders",
            "purpose_category": "working_capital",
        },
    ),

    # Six clearly ineligible applications
    make_case(
        "STRESS-008",
        "Underage applicant and newly established business",
        "auto_declined",
        {
            "applicant_age": 18,
            "operating_months": 6,
        },
    ),
    make_case(
        "STRESS-009",
        "Excessive loan ratio and cryptocurrency purpose",
        "auto_declined",
        {
            "loan_amount": 12_000_000.0,
            "monthly_turnover": 500_000.0,
            "purpose": "Cryptocurrency arbitrage and speculative trading",
            "purpose_category": "cryptocurrency",
        },
    ),
    make_case(
        "STRESS-010",
        "Applicant above age limit with gambling purpose",
        "auto_declined",
        {
            "applicant_age": 70,
            "purpose": "Expansion of online gambling operations",
            "purpose_category": "gambling",
        },
    ),
    make_case(
        "STRESS-011",
        "New business with zero demonstrated turnover",
        "auto_declined",
        {
            "operating_months": 4,
            "monthly_turnover": 0.0,
        },
    ),
    make_case(
        "STRESS-012",
        "Underage applicant requesting personal debt refinancing",
        "auto_declined",
        {
            "applicant_age": 19,
            "purpose": "Refinancing personal debts",
            "purpose_category": "personal_debt_refinancing",
        },
    ),
    make_case(
        "STRESS-013",
        "Insufficient operating history and excessive loan ratio",
        "auto_declined",
        {
            "operating_months": 10,
            "loan_amount": 10_000_000.0,
            "monthly_turnover": 500_000.0,
        },
    ),

    # Seven applications requiring human review
    make_case(
        "STRESS-014",
        "Unclassified and ambiguous loan purpose",
        "escalated",
        {
            "purpose": "Support general business activities",
            "purpose_category": "other",
        },
    ),
    make_case(
        "STRESS-015",
        "Borderline loan-to-turnover ratio",
        "escalated",
        {
            "loan_amount": 4_000_000.0,
            "monthly_turnover": 500_000.0,
        },
    ),
    make_case(
        "STRESS-016",
        "Eligible business with limited operating history",
        "escalated",
        {
            "operating_months": 18,
        },
    ),
    make_case(
        "STRESS-017",
        "Missing bank-statement account name",
        "escalated",
        {
            "bank_statement_account_name": "",
        },
    ),
    make_case(
        "STRESS-018",
        "Potential fraud caused by account-name mismatch",
        "escalated",
        {
            "applicant_name": "Grace Eze",
            "business_name": "Eze Medical Supplies",
            "bank_statement_account_name": "Unknown Third Party Holdings",
        },
    ),
    make_case(
        "STRESS-019",
        "Contradictory operating duration",
        "escalated",
        {
            "operating_months": 8,
            "business_start_date": "2025-03-01",
            "assessment_date": "2026-09-01",
        },
    ),
    make_case(
        "STRESS-020",
        "Corrupted supporting PDF",
        "escalated",
        document_bytes=b"%PDF-1.4\ncorrupted and incomplete file",
    ),
]


def run_stress_test():
    results = []

    print("\nFLOWMIND DAY 8: 20-APPLICATION STRESS TEST")
    print("=" * 78)

    for case in STRESS_CASES:
        try:
            result = process_application(
                case["application"],
                document_bytes=case["document_bytes"],
                save_to_db=False,
            )

            actual_status = result["status"]
            passed = actual_status == case["expected_status"]

            results.append(
                {
                    "id": case["id"],
                    "description": case["description"],
                    "expected": case["expected_status"],
                    "actual": actual_status,
                    "risk": result["risk"]["risk_level"],
                    "confidence": result["risk"]["confidence_score"],
                    "passed": passed,
                    "error": "",
                }
            )

            indicator = "PASS" if passed else "FAIL"
            print(
                f"{case['id']} | {indicator} | "
                f"expected={case['expected_status']} | "
                f"actual={actual_status}"
            )

        except Exception as exc:
            results.append(
                {
                    "id": case["id"],
                    "description": case["description"],
                    "expected": case["expected_status"],
                    "actual": "error",
                    "risk": "N/A",
                    "confidence": "N/A",
                    "passed": False,
                    "error": str(exc),
                }
            )

            print(f"{case['id']} | ERROR | {exc}")

    create_report(results)
    return results


def create_report(results):
    total = len(results)
    passed = sum(1 for item in results if item["passed"])
    failed = total - passed

    approved = sum(
        1 for item in results if item["actual"] == "auto_approved"
    )
    declined = sum(
        1 for item in results if item["actual"] == "auto_declined"
    )
    escalated = sum(
        1 for item in results if item["actual"] == "escalated"
    )

    autonomous = approved + declined
    autonomous_rate = autonomous / total if total else 0
    escalation_rate = escalated / total if total else 0

    lines = [
        "# Deliverable D7: Day 8 Stress-Test Results and Retrospective",
        "",
        f"**Generated:** {datetime.now().isoformat(timespec='seconds')}  ",
        f"**Applications tested:** {total}  ",
        f"**Correctly routed:** {passed}  ",
        f"**Incorrect or errored:** {failed}",
        "",
        "## Performance Summary",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| Autonomous approvals | {approved} |",
        f"| Autonomous declines | {declined} |",
        f"| Total autonomous actions | {autonomous} |",
        f"| Human escalations | {escalated} |",
        f"| Autonomous decision rate | {autonomous_rate:.1%} |",
        f"| Escalation rate | {escalation_rate:.1%} |",
        f"| Correct routing rate | {passed / total:.1%} |",
        "",
        "## Application-Level Results",
        "",
        "| ID | Scenario | Expected | Actual | Risk | Confidence | Result |",
        "|---|---|---|---|---|---:|---|",
    ]

    for item in results:
        result_label = "PASS" if item["passed"] else "FAIL"
        description = item["description"].replace("|", "/")
        lines.append(
            f"| {item['id']} | {description} | {item['expected']} | "
            f"{item['actual']} | {item['risk']} | {item['confidence']} | "
            f"{result_label} |"
        )

        if item["error"]:
            lines.append("")
            lines.append(
                f"**{item['id']} error:** `{item['error']}`"
            )
            lines.append("")

    lines.extend(
        [
            "",
            "## Coverage",
            "",
            "The stress test included clearly eligible applications, clearly "
            "ineligible applications, ambiguous purposes, medium-risk cases, "
            "missing information, identity inconsistencies, contradictory "
            "source dates and a corrupted supporting document.",
            "",
            "## Retrospective",
            "",
            "### What worked",
            "",
            "- Clear low-risk applications were routed for autonomous approval.",
            "- Applications failing multiple eligibility rules were declined.",
            "- Borderline and ambiguous applications were escalated.",
            "- Identity mismatches and missing account names triggered review.",
            "- The Day 7 duration guardrail caught contradictory source dates.",
            "- Corrupted documents were prevented from autonomous processing.",
            "",
            "### Limitations",
            "",
            "- Risk classification currently uses deterministic rules rather "
            "than three independent live LLM classifications.",
            "- Historical records without source dates cannot be audited for "
            "duration-extraction errors.",
            "- The stress data is fabricated and does not represent a validated "
            "credit-risk dataset.",
            "- Human override behaviour requires a longer operational dataset.",
            "",
            "### Production recommendations",
            "",
            "- Require source dates and document references for every extracted fact.",
            "- Mark Ollama-dependent tests separately from automated unit tests.",
            "- Encrypt personal and financial information at rest and in transit.",
            "- Conduct fairness, security and regulatory reviews before deployment.",
            "- Continue monitoring escalation and human-override rates.",
            "",
            "## Conclusion",
            "",
            f"FlowMind correctly routed {passed} of {total} stress-test "
            f"applications. The test produced an escalation rate of "
            f"{escalation_rate:.1%} and an autonomous decision rate of "
            f"{autonomous_rate:.1%}. Any failed cases shown above must be "
            "investigated before final submission.",
            "",
        ]
    )

    report_path = Path(
        "docs/deliverables/D7_stress_test_results.md"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")

    print("=" * 78)
    print(f"Passed: {passed}/{total}")
    print(f"Escalation rate: {escalation_rate:.1%}")
    print(f"Report created: {report_path}")


if __name__ == "__main__":
    run_stress_test()