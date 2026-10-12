# Deploying InfraBuddy on AWS Lambda + API Gateway

This guide walks you through deploying **InfraBuddy** to **AWS Lambda** with **Amazon API Gateway (HTTP API)** using AWS SAM or Docker/AWS CLI.

---

## Prerequisites

1. **AWS CLI** configured (`aws configure` with an administrator or deployment IAM role).
2. **AWS SAM CLI** (`sam --version`) or Docker.
3. Access to **Amazon Bedrock** (ensure model access for `amazon.nova-pro-v1:0` is enabled in the Bedrock console in your target region, e.g. `us-east-1`).

---

## Method 1: Deploy with AWS SAM (Recommended)

1. **Build the container image**:
   ```bash
   sam build
   ```

2. **Deploy to your AWS account**:
   ```bash
   sam deploy --guided
   ```

   SAM will prompt you for:
   - **Stack Name**: `infrabuddy-stack`
   - **AWS Region**: `us-east-1` (or your preferred region)
   - **SlackBotToken**: (optional, enter your `xoxb-...` token or press Enter to skip)
   - **SlackSigningSecret**: (optional, enter your signing secret or press Enter to skip)
   - Confirm creating the ECR repository and IAM role: Type `Y`

3. **Get your deployment outputs**:
   Once finished, SAM outputs your live URLs:
   - `ApiUrl`: `https://abc123xyz.execute-api.us-east-1.amazonaws.com`
   - `SlackEventsUrl`: `https://abc123xyz.execute-api.us-east-1.amazonaws.com/slack/events`
   - `TeamsMessagesUrl`: `https://abc123xyz.execute-api.us-east-1.amazonaws.com/teams/messages`

---

## Method 2: Deploy Container Directly to ECR & Lambda via AWS CLI

1. **Create an ECR repository**:
   ```bash
   aws ecr create-repository --repository-name infrabuddy --region us-east-1
   ```

2. **Login and push the Docker image**:
   ```bash
   ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com
   docker build -t infrabuddy .
   docker tag infrabuddy:latest ${ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/infrabuddy:latest
   docker push ${ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/infrabuddy:latest
   ```

3. **Create the Lambda function** pointing to the ECR image with `server.handler`.

---

## Testing Your Live Deployment

Verify liveness and Bedrock provider health:
```bash
curl https://<your-api-id>.execute-api.us-east-1.amazonaws.com/health
```

Expected Response:
```json
{
  "status": "healthy",
  "service": "infrabuddy-chatops",
  "region": "us-east-1",
  "provider": "bedrock"
}
```
