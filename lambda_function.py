import os
import json
import time
import requests

def lambda_handler(event, context):
    try:
        print("Received event:")
        print(json.dumps(event, indent=2))

        # Try to parse logs from the incoming event
        try:
            raw_body = event.get("body", "{}")
            body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
            logs = body.get("logs", "")
            print("Parsed logs from event.")
        except Exception as parse_error:
            print(f"Couldn't parse logs: {str(parse_error)}")
            logs = ""

        if not logs:
            print("No logs found in the incoming event.")
            return {"statusCode": 400, "body": json.dumps("No logs to process")}

        slack_webhook = os.environ["SLACK_WEBHOOK"]

        # Send a test/demo message if in simulation mode
        if "simulate" in logs.lower() or "demo" in logs.lower():
            print("Running in demo mode. Sending predefined solution to Slack.")

            fake_solution = (
                "CI/CD Failure Solution:\n"
                "The pipeline failed during the `Install dependencies` step due to a version conflict with `pydantic`.\n\n"
                "Suggested Fix:\n"
                "Update `requirements.txt` to specify a compatible version:\n"
                "```\npydantic>=1.10.0,<2.0.0\n```\n"
                "Then re-run the pipeline to resolve the dependency error."
            )

            requests.post(slack_webhook, json={"text": fake_solution})
            return {"statusCode": 200, "body": json.dumps("Demo solution sent successfully")}

        # Skip OpenAI call if logs are too generic
        if not any(keyword in logs.lower() for keyword in ["error", "failed", "exception", "traceback"]):
            print("Logs don't contain recognizable failure indicators. Skipping OpenAI analysis.")
            requests.post(slack_webhook, json={
                "text": "*CI/CD failure detected, but the logs didn't contain enough detail to suggest a fix.*"
            })
            return {"statusCode": 400, "body": json.dumps("Logs lacked actionable detail")}

        # Trim logs to fit within token limits
        trimmed_logs = logs[-3000:]

        openai_api_key = os.environ["OPENAI_API_KEY"]

        headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }

        prompt = (
            "You are a DevOps assistant helping engineers resolve CI/CD build failures. "
            "Analyze the following GitHub Actions logs and provide a direct, specific solution. "
            "Focus on identifying the error and suggesting a concrete fix.\n\n"
            f"{trimmed_logs}"
        )

        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "You are a helpful DevOps assistant."},
                {"role": "user", "content": prompt}
            ]
        }

        # Retry logic for rate limits
        for attempt in range(3):
            print(f"Calling OpenAI API (attempt {attempt + 1})...")
            response = requests.post("https://api.openai.com/v1/chat/completions",
                                     headers=headers, json=payload)

            print(f"OpenAI responded with status code {response.status_code}.")

            if response.status_code == 429:
                wait_time = 2 * (attempt + 1)
                print(f"Rate limited. Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
            else:
                break

        response.raise_for_status()

        solution = response.json()['choices'][0]['message']['content']
        print("Successfully received solution from OpenAI:")
        print(solution)

        slack_payload = {"text": f"*CI/CD Failure Solution:*\n{solution}"}
        slack_response = requests.post(slack_webhook, json=slack_payload)

        print(f"Posted solution to Slack (status: {slack_response.status_code}).")

        return {"statusCode": 200, "body": json.dumps("Solution shared on Slack")}

    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        try:
            fallback_msg = {
                "text": f"*OpenAI couldn't analyze the logs.*\nPartial logs:\n```{logs[:500]}```"
            }
            requests.post(os.environ["SLACK_WEBHOOK"], json=fallback_msg)
            print("Sent fallback message to Slack.")
        except Exception as slack_error:
            print(f"Error while sending fallback message: {str(slack_error)}")

        return {"statusCode": 500, "body": json.dumps(str(e))}
