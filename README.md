# InfraBuddy

An AI-powered DevOps sidekick for AWS — collects live infrastructure evidence from EC2, ALB, ASG, RDS, and CloudWatch, then uses an LLM (NVIDIA NIM / Nemotron) to diagnose issues and recommend safe remediation steps.

## Overview

The repository contains the code for an agent that can interact with AWS resources, support infrastructure automation tasks, and help developers and operators work more efficiently in cloud-native environments.

## How We Use the Agent

This agent is used as part of an AWS operations workflow to:

- review AWS resource state and operational issues
- suggest safe remediation steps and automation actions
- help generate infrastructure changes and deployment guidance
- support troubleshooting for incidents, rollout issues, and environment drift
- accelerate developer and DevOps decision making with context-aware AWS recommendations

I also use Jev as part of the broader workflow to help validate environment assumptions, support operational checks, and complement the agent with additional hands-on review and execution patterns.

## Related Projects & References

This project shares conceptual similarities with the [EKS Troubleshooting Agentic AI ChatOps](https://github.com/aws-solutions-library-samples/eks-troubleshooting-agentic-ai-chatops) solution from AWS Solutions Library, which provides:

- Agentic AI workflow for Kubernetes troubleshooting using Strands Agent framework
- Integration with EKS MCP server for real-time cluster interaction
- Amazon Bedrock for AI model orchestration
- S3 Vectors for knowledge base of historical troubleshooting cases
- Slack-based ChatOps interface for team collaboration

While the EKS troubleshooting agent focuses specifically on Kubernetes cluster issues, this AWS AI DevOps Agent provides broader infrastructure analysis across multiple AWS services (EC2, ALB, ASG, EBS, RDS) with similar LLM-powered analysis capabilities.

## Project Structure

```
infrabuddy/
├── agent/            # Evidence processing, prompts, LLM providers (NVIDIA NIM / Sample)
├── aws/              # AWS clients and collectors (EC2, ALB, ASG, RDS, CloudWatch, EBS)
├── chatops/          # Slack Bolt & Microsoft Teams Bot Framework integration
│   ├── slack/        # Slack app handlers and /slack router
│   └── teams/        # Teams bot handler and /teams router
├── tests/            # Test suite (pytest + pytest-asyncio + moto)
├── mcp-server/       # Model Context Protocol (MCP) server integration
├── docs/             # Technical guides and implementation plans
├── main.py           # CLI diagnosis entry point
├── server.py         # Unified FastAPI ChatOps server
├── pyproject.toml    # Project dependencies and tool configurations
├── .env.example      # Environment variables template
├── ARCHITECTURE.md   # Architectural design documentation
└── WORKFLOW.md       # Operational workflow documentation
```

## Features

- AWS-aware automation workflows
- AI-assisted operational guidance
- DevOps task support for deployments and troubleshooting
- Extensible architecture for integrating additional services and tools
- Ready for local development and cloud deployment
- Foundation for extension to EKS-specific troubleshooting (see Extension Opportunities below)

## Tech Stack

- Python 3.14+ agent runtime
- AWS SDK / Boto3 / AWS services integration
- LLM orchestration via OpenAI-compatible API (NVIDIA NIM)
- CI/CD-friendly project layout

## Getting Started

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies
4. Configure AWS credentials and environment variables
5. Run the application or test suite

Example:

```bash
git clone https://github.com/<your-username>/infrabuddy.git
cd infrabuddy
uv sync
```

## Configuration

Set up the required environment variables for AWS access and model integration:

```bash
# AWS credentials (via standard boto3 chain)
export AWS_REGION=us-east-1
export AWS_PROFILE=default  # or use AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY

# LLM configuration (NVIDIA NIM)
export LLM_API_KEY=your-nvidia-nim-api-key
export LLM_BASE_URL=https://integrate.api.nvidia.com/v1
export LLM_MODEL=nvidia/nemotron-3-super-120b-a12b
```

## Usage

Run the project locally or integrate it into your DevOps workflow.

```bash
uv run python main.py
# or after installing the package
uv run infrabuddy
```

## Testing

Use the project test suite to verify behavior before deployment:

```bash
pytest
```

## Deployment

This project is designed to be deployed in AWS environments with infrastructure automation and operational monitoring in mind. Adjust deployment configuration to fit your environment, security requirements, and team workflows.

## ChatOps Integration (Slack & Microsoft Teams)

InfraBuddy includes a built-in ChatOps interface supporting both Slack and Microsoft Teams via FastAPI and Bot Framework / Bolt.

### 1. Installation
Install with ChatOps optional dependencies:
```bash
uv sync --extra chatops
```

### 2. Configure ChatOps Variables
Copy `.env.example` to `.env` and set:
- **Slack**: `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET` (and `SLACK_APP_TOKEN` for Socket Mode)
- **Teams**: `MICROSOFT_APP_ID`, `MICROSOFT_APP_PASSWORD`

### 3. Start the ChatOps Server
```bash
uv run uvicorn server:app --host 0.0.0.0 --port 8000 --reload
# or using console script
uv run infrabuddy-server
```

Endpoints available:
- `GET /health` — Health check
- `POST /slack/events` — Slack Webhook / Interactivity endpoint
- `POST /teams/messages` — Microsoft Teams Messaging endpoint

### 4. Bot Commands
- `/infrabuddy analyze [service]` (Slack) or `@InfraBuddy analyze [service]` (Teams)
- `/infrabuddy status` or `@InfraBuddy status`
- `/infrabuddy help` or `@InfraBuddy help`

## Extension Opportunities

Based on the EKS Troubleshooting Agentic AI ChatOps reference architecture, this project could be extended to include:

1. **EKS-specific analysis**: Add modules for EKS cluster, node group, and workload inspection
2. **MCP server integration**: Connect to EKS MCP server for real-time kubectl command execution
3. **Knowledge base**: Implement S3 Vectors or similar for storing historical analysis patterns
4. **Multi-model orchestration**: Use different models for different tasks (analysis vs. embeddings)
6. **Agentic workflow**: Implement specialized agents for different AWS service domains

See `ARCHITECTURE.md` and `WORKFLOW.md` for detailed technical documentation.

## License

This project is provided as-is for development and experimentation. Add your preferred license if you plan to distribute it.

## Contributing

Contributions are welcome. Please keep changes focused, add tests where appropriate, and document any new configuration or operational requirements.
