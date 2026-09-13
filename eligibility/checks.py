APPROVED_PURPOSES = [
    "inventory",
    "equipment",
    "expansion",
    "working capital"
]


def check_registration_months(record: dict) -> dict:
    months = record.get("months_registered")

    if months is None:
        return {
            "criterion": "registration",
            "passed": False,
            "confidence": "low",
            "evidence": "months_registered missing"
        }

    return {
        "criterion": "registration",
        "passed": months >= 12,
        "confidence": "high",
        "evidence": f"{months} months registered"
    }


def check_applicant_age(record: dict) -> dict:
    age = record.get("age")

    if age is None:
        return {
            "criterion": "age",
            "passed": False,
            "confidence": "low",
            "evidence": "age missing"
        }

    return {
        "criterion": "age",
        "passed": 21 <= age <= 65,
        "confidence": "high",
        "evidence": f"Applicant age is {age}"
    }


def check_loan_to_turnover(record: dict) -> dict:
    loan = record.get("loan_amount")
    turnover = record.get("avg_monthly_turnover")

    if loan is None or turnover is None:
        return {
            "criterion": "loan_to_turnover",
            "passed": False,
            "confidence": "low",
            "evidence": "loan amount or turnover missing"
        }

    if turnover == 0:
        return {
            "criterion": "loan_to_turnover",
            "passed": False,
            "confidence": "low",
            "evidence": "Average monthly turnover is zero"
        }

    maximum_allowed = turnover * 10

    return {
        "criterion": "loan_to_turnover",
        "passed": loan <= maximum_allowed,
        "confidence": "high",
        "evidence": (
            f"Loan amount {loan}; monthly turnover {turnover}; "
            f"maximum allowed {maximum_allowed}"
        )
    }


def check_purpose_category(record: dict) -> dict:
    purpose = record.get("purpose")

    if not purpose:
        return {
            "criterion": "purpose",
            "passed": False,
            "confidence": "low",
            "evidence": "Loan purpose missing"
        }

    purpose_clean = purpose.lower().strip()

    return {
        "criterion": "purpose",
        "passed": purpose_clean in APPROVED_PURPOSES,
        "confidence": "high",
        "evidence": f"Loan purpose: {purpose}"
    }


def check_eligibility(record: dict) -> list[dict]:
    return [
        check_registration_months(record),
        check_applicant_age(record),
        check_loan_to_turnover(record),
        check_purpose_category(record)
    ]


if __name__ == "__main__":
    test_record = {
        "applicant_name": "Blessing",
        "business_name": "Kallers Nigeria",
        "age": 25,
        "months_registered": 24,
        "loan_amount": 2000000,
        "avg_monthly_turnover": 500000,
        "purpose": "inventory"
    }

    print(check_eligibility(test_record))