# Copilot instructions

## Build and run

This project uses `uv` and requires Python 3.14 or newer (`.python-version` is 3.14).

```bash
uv sync
```

### Running the analysis

The primary analysis script is located at `main.py` in the repository root. It can be run directly with:

```bash
uv run python main.py
```

Alternatively, after installing the package in development mode, you can use the console script:

```bash
uv run aws-ai-devops-agent
```

Note: The console script currently points to a placeholder in the package (`src/aws_ai_devops_agent/main.py`) that simply directs users to run the root `main.py`. The actual analysis logic resides in the root `main.py`.

### Environment configuration

The analyzer requires:
- AWS credentials available through the standard boto3 credential chain (environment variables, ~/.aws/credentials, etc.)
- LLM configuration via `.env` file or environment variables:
  - `LLM_API_KEY`: API key for the NVIDIA NIM service
  - `LLM_BASE_URL`: Base URL for the LLM API (default: https://integrate.api.nvidia.com/v1)
  - `LLM_MODEL`: Model identifier (default: nvidia/nemotron-3-super-120b-a12b)

The script currently analyzes the `us-east-1` region. To change the region, modify the `REGION` constant in `main.py`.

## Architecture

- `main.py` (root): Orchestrates the analysis by:
  1. Creating regional AWS clients via `AWSClients`
  2. Collecting infrastructure evidence (EC2, ALB, ASG, EBS, RDS)
  3. Gathering CloudWatch metrics for EC2 and RDS
  4. Building an analysis prompt from the evidence
  5. Sending the prompt to a configured LLM (OpenAI-compatible API)
  6. Printing the LLM's analysis and recommendations

- `aws/client.py`: Defines the `AWSClients` class that creates and shares boto3 clients for various services.

- Resource-specific modules in `aws/` (e.g., `ec2.py`, `rds.py`, `cloudwatch.py`):
  - Use the shared `AWSClients` instance
  - Normalize AWS responses into dictionaries for easier consumption
  - Handle pagination and error handling where appropriate

- `agent/evidence.py`: Combines data from AWS resource modules and metrics into a cohesive evidence structure.

- `agent/prompts.py`: Formats the evidence into a prompt instructing the LLM to act as an AWS DevOps analyst.

- `agent/llm.py`: Handles communication with the LLM API, including retries and error handling.

## Repository conventions

- Pass the shared `AWSClients` instance to AWS collection functions rather than creating new boto3 clients in each module.
- Keep AWS API interaction within the relevant `aws/` module and return normalized data.
- The current analysis flow is read-only: it collects AWS state and metrics, then returns textual recommendations. It does not modify any AWS resources.
- The package structure in `src/aws_ai_devops_agent` is currently a placeholder for distributable console scripts. The core logic remains in the repository root.

## Project structure

Key directories and files:
- `main.py`: Primary analysis script (root)
- `aws/`: AWS service modules and client
- `agent/`: Evidence collection, prompt building, and LLM interaction
- `src/aws_ai_devops_agent/`: Python package containing the console script entry point
- `.env`: Environment variables for LLM configuration (not committed)
- `.python-version`: Specifies Python 3.14
- `pyproject.toml`: Project configuration and dependencies
- `uv.lock`: Locked dependencies
- `agency-agents/`: Separate repository (submodule) containing agent definitions for various domains (not directly used in the AWS analysis)

## Testing and linting

There are currently no test files or linting configurations in the repository.

If tests are added using the standard library `unittest` framework:
- Run the full test suite: `uv run python -m unittest discover -s tests`
- Run a specific test: `uv run python -m unittest tests.test_module.TestClass.test_method`

## Dependencies

Core dependencies managed by `uv` and specified in `pyproject.toml`:
- `boto3`: AWS SDK for Python
- `openai`: OpenAI-compatible client (used for NVIDIA NIM)
- `python-dotenv`: For loading environment variables from `.env`

Development dependencies are not currently specified.

## MCP Server Configuration

For enhanced functionality with this AWS AI DevOps agent, you may want to configure MCP (Model Context Protocol) servers. Since you indicated interest in accessing all AWS services through MCP servers, here's how you could approach this:

### Comprehensive AWS MCP Server Approach

If you had access to a comprehensive AWS MCP server, it could potentially provide standardized access to:
- Compute: EC2, Lambda, Elastic Beanstalk, ECS/EKS
- Storage: S3, EBS, EFS, Glacier
- Database: RDS, DynamoDB, ElastiCache, Redshift
- Networking: VPC, CloudFront, Route 53, API Gateway, Load Balancers
- Management: CloudFormation, CloudWatch, CloudTrail, Config, Systems Manager
- Security: IAM, KMS, Secrets Manager, WAF, GuardDuty
- Analytics: Athena, EMR, Kinesis, QuickSight
- Application Integration: SNS, SQS, Step Functions

### Practical Implementation Options

Since a single "all AWS services" MCP server may not be readily available, you could consider:

1. Individual Service MCP Servers: Look for or create MCP servers for specific services you use most frequently
2. AWS CLI Wrapper MCP: An MCP server that wraps the AWS CLI, providing access to any service through standardized commands
3. AWS SDK MCP Server: An MCP server that exposes boto3 functionality through standardized interfaces
4. Infrastructure as Code MCP: Focus on MCP servers for Terraform or CloudFormation to manage AWS resources declaratively

### Configuration Approach

To configure MCP servers for comprehensive AWS access:
1. Research available MCP servers for AWS services (check MCP registries, GitHub, etc.)
2. Install and configure selected MCP servers according to their documentation
3. Ensure they have appropriate AWS credentials and permissions
4. Test connectivity and basic operations
5. Integrate them into your Copilot workflow as needed

### Recommended Starting Point

For an AWS-focused AI DevOps agent, you might start with:
- An MCP server for core infrastructure services (EC2, S3, RDS, Lambda)
- An MCP server for Infrastructure as Code (Terraform/CloudFormation)
- An MCP server for monitoring and logging (CloudWatch)
- An MCP server for identity and access management (IAM)

Would you like me to help you research or configure specific MCP servers for any of these AWS service categories? If you have particular services you use most frequently in your workflow, I can provide more targeted suggestions.
