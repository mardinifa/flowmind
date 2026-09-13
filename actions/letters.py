import ollama


def generate_decline_letter(record: dict, failed: list) -> str:
    failed_text = "\n".join(
        f"- {f['criterion']}: {f['evidence']}"
        for f in failed
    )

    prompt = (
        f"Write a polite, professional decline letter to "
        f"{record['applicant_name']} of {record['business_name']}.\n\n"
        f"The loan application was declined because these criteria "
        f"were not met:\n{failed_text}\n\n"
        f"Explain each reason briefly and accurately. "
        f"Do not mention criteria that passed. "
        f"Do not invent facts, dates, or numbers."
    )

    response = ollama.chat(
        model="llama3",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


def generate_approval_letter(record: dict) -> str:
    prompt = (
        f"Write a professional conditional loan approval letter to "
        f"{record['applicant_name']} of {record['business_name']}.\n\n"
        f"State that their application has successfully passed the "
        f"initial eligibility assessment. "
        f"Explain that any remaining verification or documentation "
        f"must still be completed before final disbursement. "
        f"Do not invent dates, numbers, interest rates, conditions "
        f"or other facts that are not in the application."
    )

    response = ollama.chat(
        model="llama3",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]