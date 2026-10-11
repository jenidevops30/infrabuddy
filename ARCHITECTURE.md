# InfraBuddy — Project Architecture

## Overview

This project is an AI-powered DevOps assistant for AWS operations that collects infrastructure evidence from AWS services, analyzes it using an LLM, and provides actionable recommendations. The system is read-only and does not modify any AWS resources.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              main.py (Entry Point)                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AWSClients (aws/client.py)                         │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌─────┐ ┌────────────┐               │
│  │   EC2   │ │  ELBv2  │ │AutoScaling│ │ RDS │ │ CloudWatch │               │
│  └─────────┘ └─────────┘ └──────────┘ └─────┘ └────────────┘               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        aws/health.py (get_health_snapshot)                   │
│  Collects infrastructure state from all AWS services                         │
└─────────────────────────────────────────────────────────────────────────────┘
                    │                 │                 │
                    ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        aws/metrics.py (get_ec2_evidence, get_rds_evidence)   │
│  Collects CloudWatch metrics for EC2 and RDS resources                       │
└─────────────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        agent/evidence.py (build_evidence)                    │
│  Combines infrastructure snapshot + metrics into unified evidence structure  │
└─────────────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        agent/prompts.py (build_health_prompt)                │
│  Formats evidence into structured prompt for LLM analysis                    │
└─────────────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        agent/llm.py (LLM.analyze)                            │
│  Sends prompt to NVIDIA NIM (OpenAI-compatible API) and returns analysis    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Module Details

### 1. Entry Point: `main.py`

**Purpose**: Orchestrates the complete analysis workflow.

**Flow**:
1. Creates `AWSClients` for `us-east-1` region
2. Calls `build_evidence()` to collect infrastructure + metrics
3. Calls `build_health_prompt()` to format evidence for LLM
4. Calls `LLM.analyze()` to get AI analysis
5. Prints formatted results

**Configuration**: Region is hardcoded as `REGION = "us-east-1"` (modify to change)

---

### 2. AWS Client Layer: `aws/client.py`

**Class**: `AWSClients`

**Responsibility**: Creates and shares boto3 clients for all AWS services used.

**Clients Created**:
| Client | Service | Purpose |
|--------|---------|---------|
| `ec2` | Amazon EC2 | Instance and volume management |
| `elbv2` | Elastic Load Balancing v2 | ALB/NLB management |
| `autoscaling` | Auto Scaling | ASG management |
| `rds` | Amazon RDS | Database instance management |
| `cloudwatch` | CloudWatch | Metrics collection |

**Design Pattern**: Single shared instance passed to all collection functions (dependency injection)

---

### 3. Infrastructure Collection: `aws/health.py`

**Function**: `get_health_snapshot(clients: AWSClients) -> dict`

**Returns**: Complete infrastructure snapshot with:
```python
{
    "region": "us-east-1",
    "ec2": [...],      # List of EC2 instances
    "alb": [...],      # List of ALBs with target groups + health
    "asg": [...],      # List of Auto Scaling Groups
    "ebs": [...],      # List of EBS volumes
    "rds": [...],      # List of RDS instances
}
```

**Data Sources**:
| Resource | Module | Function |
|----------|--------|----------|
| EC2 | `aws/ec2.py` | `list_instances()` |
| ALB | `aws/alb.py` | `list_load_balancers()`, `get_target_groups()`, `get_target_health()` |
| ASG | `aws/asg.py` | `list_auto_scaling_groups()` |
| EBS | `aws/ebs.py` | `list_volumes()` |
| RDS | `aws/rds.py` | `list_db_instances()` |

---

### 4. Resource Collection Modules

#### `aws/ec2.py` - `list_instances()`
Returns normalized EC2 instance data:
```python
{
    "id": "i-1234567890abcdef0",
    "type": "t3.medium",
    "state": "running",
    "private_ip": "10.0.1.50",
    "availability_zone": "us-east-1a"
}
```

#### `aws/alb.py`
- `list_load_balancers()`: Returns ALB metadata (name, ARN, DNS, state, type)
- `get_target_groups(lb_arn)`: Returns target groups for an ALB
- `get_target_health(tg_arn)`: Returns target health for a target group

#### `aws/asg.py` - `list_auto_scaling_groups()`
Returns ASG configuration and instance states:
```python
{
    "name": "my-asg",
    "min_size": 2,
    "max_size": 10,
    "desired_capacity": 3,
    "instances": [
        {"id": "i-123", "state": "InService", "health": "Healthy"}
    ]
}
```

#### `aws/ebs.py` - `list_volumes()`
Returns EBS volume details including attachments:
```python
{
    "id": "vol-123",
    "size_gb": 100,
    "volume_type": "gp3",
    "state": "in-use",
    "iops": 3000,
    "throughput": 125,
    "attachments": [{"instance_id": "i-123", "device": "/dev/sdf", "state": "attached"}]
}
```

#### `aws/rds.py` - `list_db_instances()`
Returns RDS instance details:
```python
{
    "identifier": "my-db",
    "engine": "postgres",
    "engine_version": "15.4",
    "status": "available",
    "instance_class": "db.t3.medium",
    "availability_zone": "us-east-1a",
    "multi_az": True,
    "storage_type": "gp3",
    "allocated_storage_gb": 100,
    "storage_encrypted": True,
    "endpoint": "my-db.xxx.us-east-1.rds.amazonaws.com",
    "port": 5432
}
```

---

### 5. Metrics Collection: `aws/cloudwatch.py`

**Functions** (all return list of `{timestamp, value}` datapoints):

| Function | Namespace | Metric | Dimensions | Statistics |
|----------|-----------|--------|------------|------------|
| `get_ec2_cpu()` | AWS/EC2 | CPUUtilization | InstanceId | Average |
| `get_alb_metric()` | AWS/ApplicationELB | Various | LoadBalancer | Sum |
| `get_target_group_metric()` | AWS/ApplicationELB | Various | LoadBalancer, TargetGroup | Average |
| `get_rds_metric()` | AWS/RDS | Various | DBInstanceIdentifier | Average |
| `get_ebs_metric()` | AWS/EBS | Various | VolumeId | Average |

**Default Time Window**: 30 minutes, 5-minute periods (300 seconds)

**Helper**: `summarize_metric(datapoints)` → Returns `{count, average, minimum, maximum, latest}`

---

### 6. Metrics Evidence: `aws/metrics.py`

**Functions**:
- `get_ec2_evidence(clients, instances)`: Adds 30-min CPU metrics to running instances
- `get_rds_evidence(clients, databases)`: Adds CPU, Connections, FreeStorageSpace metrics

**Output Structure**:
```python
# EC2 Evidence
{
    "instance_id": "i-123",
    "state": "running",
    "instance_type": "t3.medium",
    "cpu_30m": {"count": 6, "average": 45.2, "minimum": 12.1, "maximum": 78.9, "latest": 52.3}
}

# RDS Evidence
{
    "identifier": "my-db",
    "status": "available",
    "engine": "postgres",
    "instance_class": "db.t3.medium",
    "multi_az": True,
    "cpu_30m": {...},
    "connections_30m": {...},
    "free_storage_bytes_30m": {...}
}
```

---

### 7. Evidence Aggregation: `agent/evidence.py`

**Function**: `build_evidence(clients: AWSClients) -> dict`

**Combines**:
1. Infrastructure snapshot from `get_health_snapshot()`
2. EC2 metrics from `get_ec2_evidence()`
3. RDS metrics from `get_rds_evidence()`

**Final Evidence Structure**:
```python
{
    "region": "us-east-1",
    "infrastructure": {
        "ec2": [...],
        "alb": [...],
        "asg": [...],
        "ebs": [...],
        "rds": [...]
    },
    "metrics": {
        "ec2": [...],
        "rds": [...]
    }
}
```

---

### 8. Prompt Building: `agent/prompts.py`

**Function**: `build_health_prompt(evidence: dict) -> str`

**Output**: Formatted prompt with:
- Analysis instructions (6 specific tasks)
- Safety rules (5 constraints)
- Full evidence as pretty-printed JSON

**Prompt Template**:
```
Analyze the following AWS infrastructure evidence.

Determine:
1. Overall health
2. Critical anomalies
3. Most likely problems
4. Evidence supporting each problem
5. Recommended next investigation
6. Whether human intervention may be required

Important rules:
- Use only the supplied evidence.
- Do not invent metrics.
- Do not claim an incident exists without evidence.
- Do not recommend destructive actions.
- Do not modify AWS resources.

AWS EVIDENCE:
{json.dumps(evidence, indent=2, default=str)}
```

---

### 9. LLM Integration: `agent/llm.py`

**Class**: `LLM`

**Configuration** (from environment variables):
- `LLM_API_KEY`: NVIDIA NIM API key
- `LLM_BASE_URL`: API base URL (default: `https://integrate.api.nvidia.com/v1`)
- `LLM_MODEL`: Model identifier (default: `nvidia/nemotron-3-super-120b-a12b`)

**Method**: `analyze(evidence: str) -> str`

**Parameters**:
- `temperature=0.1` (low for deterministic analysis)
- System prompt: Expert AWS DevOps engineer persona
- User prompt: Formatted evidence from `build_health_prompt()`

---

## Data Flow Summary

```
AWS API Calls
     │
     ▼
┌──────────────────────────────────────────┐
│  aws/health.py → get_health_snapshot()   │
│  Returns: infrastructure snapshot        │
└──────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────┐
│  aws/metrics.py → get_ec2_evidence()     │
│  aws/metrics.py → get_rds_evidence()     │
│  Returns: metrics with summaries         │
└──────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────┐
│  agent/evidence.py → build_evidence()    │
│  Returns: unified evidence dict          │
└──────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────┐
│  agent/prompts.py → build_health_prompt()│
│  Returns: formatted prompt string        │
└──────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────┐
│  agent/llm.py → LLM.analyze()            │
│  Returns: AI analysis text               │
└──────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────┐
│  main.py → print(analysis)               │
└──────────────────────────────────────────┘
```

---

## Dependencies

**Runtime** (`pyproject.toml`):
- `boto3>=1.43.108` - AWS SDK
- `openai>=3.26.0` - OpenAI-compatible client for NVIDIA NIM
- `python-dotenv>=1.2.4` - Environment variable loading

**Python Version**: 3.14+ (specified in `.python-version`)

---

## Environment Variables Required

| Variable | Description | Required |
|----------|-------------|----------|
| `LLM_API_KEY` | NVIDIA NIM API key | Yes |
| `LLM_BASE_URL` | LLM API base URL | Yes |
| `LLM_MODEL` | Model identifier | Yes |
| `AWS_REGION` | AWS region (or use default profile) | Via boto3 chain |
| `AWS_PROFILE` | AWS credentials profile | Via boto3 chain |

---

## Extensibility Points

### Adding New AWS Resources
1. Create new module in `aws/` (e.g., `aws/lambda.py`)
2. Add collection function (e.g., `list_functions()`)
3. Add client to `AWSClients` if new service
4. Call from `get_health_snapshot()` in `aws/health.py`
5. Add metrics collection in `aws/metrics.py` if needed
6. Evidence automatically included in prompt

### Adding New Metrics
1. Add function in `aws/cloudwatch.py` for new metric
2. Call from `aws/metrics.py` evidence functions
3. Metrics automatically summarized and included

### Customizing Analysis
- Modify `build_health_prompt()` in `agent/prompts.py` for different analysis focus
- Adjust system prompt in `agent/llm.py` for different persona
- Change temperature for more/less creative responses

---

## Security Considerations

- **Read-only**: No AWS write operations (no `create`, `update`, `delete`, `modify` calls)
- **Least privilege**: Requires only `Describe*` and `GetMetricStatistics` permissions
- **No credentials in code**: Uses standard boto3 credential chain
- **LLM isolation**: Evidence sent to external LLM API (review data sensitivity)

---

## Running the Analysis

```bash
# Using uv (recommended)
uv run python main.py

# Or after installing package
uv run aws-ai-devops-agent
```

**Prerequisites**:
1. AWS credentials configured (via `~/.aws/credentials`, env vars, or IAM role)
2. `.env` file with LLM configuration:
   ```
   LLM_API_KEY=your-nvidia-nim-key
   LLM_BASE_URL=https://integrate.api.nvidia.com/v1
   LLM_MODEL=nvidia/nemotron-3-super-120b-a12b
   ```

---

## Project Structure

```
aws-ai-devops-agent/
├── main.py                    # Entry point
├── pyproject.toml             # Project config & dependencies
├── README.md                  # Project documentation
├── ARCHITECTURE.md            # This file
├── .python-version            # Python 3.14
├── .env                       # LLM config (not committed)
├── aws/
│   ├── __init__.py
│   ├── client.py              # AWSClients - shared boto3 clients
│   ├── health.py              # Infrastructure snapshot collection
│   ├── metrics.py             # Metrics evidence collection
│   ├── cloudwatch.py          # CloudWatch metric queries
│   ├── ec2.py                 # EC2 instance collection
│   ├── alb.py                 # ALB + target group collection
│   ├── asg.py                 # Auto Scaling Group collection
│   ├── ebs.py                 # EBS volume collection
│   └── rds.py                 # RDS instance collection
└── agent/
    ├── __init__.py
    ├── evidence.py            # Evidence aggregation
    ├── prompts.py             # Prompt building
    └── llm.py                 # LLM integration
```

---

## Future Enhancement Opportunities

1. **Additional AWS Services**: Lambda, ECS/EKS, S3, CloudFront, DynamoDB, ElastiCache
2. **Metric Expansion**: Memory, disk, network, custom metrics
3. **Time Series Analysis**: Trend detection, anomaly detection over longer periods
4. **Multi-Region Support**: Aggregate across regions
5. **Output Formats**: JSON, HTML reports, Slack/Teams notifications
6. **Interactive Mode**: Follow-up questions, drill-down analysis
7. **CI/CD Integration**: GitHub Actions, GitLab CI for scheduled runs
8. **Prompt Versioning**: Track prompt iterations with changelog
9. **Test Suite**: Unit tests for collection functions, integration tests
10. **Configuration File**: YAML/JSON config for regions, services, metrics