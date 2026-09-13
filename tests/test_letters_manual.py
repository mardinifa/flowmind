from actions.letters import generate_decline_letter, generate_approval_letter


ineligible_records = [
    {
        "applicant_name": "Blessing",
        "business_name": "Kallers Nigeria",
        "failed": [
            {
                "criterion": "age",
                "evidence": "Applicant age is 19"
            }
        ]
    },
    {
        "applicant_name": "Ada",
        "business_name": "Ada Stores",
        "failed": [
            {
                "criterion": "registration",
                "evidence": "5 months registered"
            }
        ]
    },
    {
        "applicant_name": "Tunde",
        "business_name": "Tunde Ventures",
        "failed": [
            {
                "criterion": "loan_to_turnover",
                "evidence": "Loan amount 6000000; monthly turnover 500000; maximum allowed 5000000"
            }
        ]
    }
]


eligible_records = [
    {
        "applicant_name": "Blessing",
        "business_name": "Kallers Nigeria"
    },
    {
        "applicant_name": "Chidi",
        "business_name": "Chidi Enterprises"
    },
    {
        "applicant_name": "Amina",
        "business_name": "Amina Trading"
    }
]


print("\n--- DECLINE LETTERS ---\n")

for item in ineligible_records:
    record = {
        "applicant_name": item["applicant_name"],
        "business_name": item["business_name"]
    }

    letter = generate_decline_letter(record, item["failed"])

    print(letter)
    print("\n" + "=" * 70 + "\n")


print("\n--- APPROVAL LETTERS ---\n")

for record in eligible_records:
    letter = generate_approval_letter(record)

    print(letter)
    print("\n" + "=" * 70 + "\n")