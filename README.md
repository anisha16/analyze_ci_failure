**CI/CD Debugger using OpenAI and AWS Lambda**

This project is an AI-powered Lambda function that receives CI/CD failure logs, analyzes them using OpenAI’s API, and sends a summarized explanation or potential fix to a configured Slack channel.

**Project Overview**

The Lambda function acts as an automated CI/CD log analyzer. It integrates OpenAI’s GPT model to interpret build logs and returns useful feedback to help DevOps engineers debug faster. The feedback is then pushed to Slack for immediate visibility.

**Prerequisites**
	•	Docker installed and running
	•	AWS account with access to Lambda (Python 3.11 runtime)
	•	OpenAI API key
	•	Slack Incoming Webhook URL

**Workflow**
	1.	A CI/CD pipeline failure sends the logs to this Lambda function (via an API Gateway or direct trigger).
	2.	The function sends those logs to OpenAI GPT for summarization.
	3.	OpenAI returns an explanation and suggestion.
	4.	The result is posted in a Slack channel using a webhook.

**How to Run the Project**
	1.	Clone this repository to your local machine.
	2.	Install dependencies inside a Docker container for compatibility with AWS Lambda’s execution environment. Use a manylinux-compatible base for correct binary formats.
	3.	Package the Lambda deployment ZIP file by combining:
	•	lambda_function.py
	•	All installed dependencies inside a python/ directory (flattened)
	4.	Deploy the ZIP file to AWS Lambda using the AWS Console or CLI.
	5.	Set environment variables in Lambda for:
	•	OPENAI_API_KEY
	•	SLACK_WEBHOOK
	6.	Test the function by sending a mock CI/CD failure log event to it.
