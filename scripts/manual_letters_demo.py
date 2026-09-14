"""
Manual Ollama letter-generation demonstration.

This file is intentionally not an automated unit test because it requires
a running local Ollama service and the Llama 3 model.

Run manually with:
python scripts/manual_letters_demo.py
"""

from actions.letters import (
    generate_approval_letter,
    generate_decline_letter,
)


INELIGIBLE_RECORDS = [
    {
        "applicant_name": "Blessing",
        "business_name": "Kallers Nigeria",
        "failed": [
            {
                "criterion": "age",
                "evidence": "Applicant age is 19",
            }
        ],
    },
    {
        "applicant_name": "Ada",
        "business_name": "Ada Stores",
        "failed": [
            {
                "criterion": "registration",
                "evidence": "Business has been registered for only 5 months",
            }
        ],
    },
    {
        "applicant_name": "Tunde",
        "business_name": "Tunde Ventures",
        "failed": [
            {
                "criterion": "loan_to_turnover",
                "evidence": (
                    "Loan amount is 6,000,000; monthly turnover is "
                    "500,000; maximum permitted loan is 5,000,000"
                ),
            }
        ],
    },
]


ELIGIBLE_RECORDS = [
    {
        "applicant_name": "Blessing",
        "business_name": "Kallers Nigeria",
    },
    {
        "applicant_name": "Chidi",
        "business_name": "Chidi Enterprises",
    },
    {
        "applicant_name": "Amina",
        "business_name": "Amina Trading",
    },
]


def run_manual_letter_demonstration():
    """Generate sample letters through the locally running Ollama model."""
    print("\n--- DECLINE LETTERS ---\n")

    for item in INELIGIBLE_RECORDS:
        record = {
            "applicant_name": item["applicant_name"],
            "business_name": item["business_name"],
        }

        letter = generate_decline_letter(record, item["failed"])
        print(letter)
        print("\n" + "=" * 70 + "\n")

    print("\n--- APPROVAL LETTERS ---\n")

    for record in ELIGIBLE_RECORDS:
        letter = generate_approval_letter(record)
        print(letter)
        print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    run_manual_letter_demonstration()