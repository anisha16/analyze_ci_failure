CI/CD Failure Analyzer with GenAI (OpenAI + AWS Lambda + Slack)
This project uses AWS Lambda, OpenAI GPT-4, and Slack to automatically analyze CI/CD logs and send intelligent summaries + fix recommendations to Slack. It is ideal for teams that want to debug pipeline failures in real time using AI.

Project Architecture
GitHub Actions → AWS API Gateway → Lambda (Python) → OpenAI API → Slack Webhook

Setup Instructions

1. Clone the repo

   git clone
   cd
2. Add dependencies in requirements.txt
3. Install dependencies for AWS Lambda architecture (Linux x86_64)
   mkdir -p python

docker run --rm -v "$PWD":/var/task -w /var/task \
  public.ecr.aws/sam/build-python3.11 \
  pip install -r requirements.txt --platform manylinux2014_x86_64 \
  --target python --upgrade --only-binary=:all:

4. Add Lambda function
