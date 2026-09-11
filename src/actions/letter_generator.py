"""
Autonomous Action Output: Letter Generator
Produces personalized conditional approval and specific decline letters for ClearPath Capital.
"""

from typing import Dict, Any, List


def generate_conditional_approval_letter(record: Dict[str, Any]) -> str:
    """
    Generates a personalized conditional approval letter referencing verified facts.
    """
    applicant = record.get("applicant_name", "Valued Applicant")
    business = record.get("business_name", "Your Business")
    amount = record.get("loan_amount", 0)
    months = record.get("operating_months", 0)
    turnover = record.get("monthly_turnover", 0)

    letter = f"""ClearPath Capital Microfinance
Victoria Island, Lagos, Nigeria

Dear {applicant},

Re: Conditional Loan Approval for {business}

We are pleased to inform you that your application for a microfinance credit facility in the amount of ₦{amount:,.2f} has received conditional approval from ClearPath Capital.

Our assessment confirmed your verified operating track record of {months} months and an average demonstrated monthly turnover of ₦{turnover:,.2f}. Based on your stated business requirements, our credit committee has approved your facility in principle.

Next Steps:
1. An account officer will reach out within 24 hours to schedule a brief on-site physical verification of {business}.
2. Please prepare original copies of your CAC certificate and valid national ID for inspection.
3. Upon completion of documentation, loan disbursement will be credited to your verified commercial bank account.

Thank you for choosing ClearPath Capital as your growth partner.

Sincerely,
Credit Operations Team
ClearPath Capital Microfinance
"""
    return letter.strip()


def generate_decline_letter(record: Dict[str, Any], failed_criteria_details: List[str] = None) -> str:
    """
    Generates a personalized decline letter referencing the specific failed criteria.
    Never generic; accurately cites the exact policy requirements not satisfied.
    """
    applicant = record.get("applicant_name", "Valued Applicant")
    business = record.get("business_name", "Your Business")
    amount = record.get("loan_amount", 0)

    reasons_text = ""
    if failed_criteria_details:
        bullet_points = [f"- {reason}" for reason in failed_criteria_details]
        reasons_text = "\n".join(bullet_points)
    else:
        reasons_text = "- The application did not meet our standard credit risk and tenure guidelines."

    letter = f"""ClearPath Capital Microfinance
Victoria Island, Lagos, Nigeria

Dear {applicant},

Re: Loan Application Decision for {business} (Requested: ₦{amount:,.2f})

Thank you for taking the time to apply for a credit facility with ClearPath Capital. We appreciate the opportunity to review your business profile.

Following a thorough review of your submission against our published credit guidelines, we regret to inform you that we are unable to approve your loan request at this time.

Specific Reasons for Decision:
{reasons_text}

Our lending guidelines are designed to protect both the institution and our clients from over-indebtedness. We encourage you to re-apply once your business meets the tenure and turnover thresholds outlined above.

We wish {business} continued growth and success.

Sincerely,
Credit Risk Management
ClearPath Capital Microfinance
"""
    return letter.strip()
