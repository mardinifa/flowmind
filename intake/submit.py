import sys
import json
import httpx


def submit_application(file_path, webhook_url):
    try:
        with open(file_path, 'r') as file:
            payload = json.load(file)

        print(f"Sending payload from {file_path}...")
        response = httpx.post(webhook_url, json=payload)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python intake/submit.py <file_path> <webhook_url>")
        sys.exit(1)

    submit_application(sys.argv[1], sys.argv[2])