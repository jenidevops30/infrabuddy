# AWS AI DevOps Agent - Operational Workflow

## Overview

This document describes the complete operational workflow for the AWS AI DevOps Agent, from setup through analysis execution and result interpretation.

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           COMPLETE OPERATIONAL WORKFLOW                          │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   SETUP      │────▶│  EXECUTE     │────▶│   ANALYZE    │────▶│   ACT        │
│  PHASE       │     │  PHASE       │     │  PHASE       │     │  PHASE       │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
      │                    │                    │                    │
      ▼                    ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ 1. Install   │     │ 1. Collect   │     │ 1. LLM       │     │ 1. Review    │
│    deps      │     │    infra     │     │    analyzes  │     │    findings  │
│ 2. Config    │     │ 2. Collect   │     │ 2. Returns   │     │ 2. Prioritize│
│    AWS creds │     │    metrics   │     │    structured  │     │ 3. Investigate│
│ 3. Config    │     │ 3. Build     │     │    findings  │     │ 4. Remediate │
│    LLM       │     │    evidence  │     │              │     │ 5. Monitor   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

---

## Phase 1: Setup

### 1.1 Install Dependencies

```bash
# Clone repository
git clone <repository-url>
cd aws-ai-devops-agent

# Install using uv (recommended)
uv sync

# Or install package in development mode
uv pip install -e .
```

### 1.2 Configure AWS Credentials

The agent uses standard boto3 credential chain. Choose one:

**Option A: AWS CLI Profile**
```bash
aws configure --profile my-profile
export AWS_PROFILE=my-profile
```

**Option B: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=AKIA...
export AWS_SECRET_ACCESS_KEY=...
export AWS_REGION=us-east-1
```

**Option C: IAM Role (EC2/ECS/Lambda)**
No configuration needed - automatic.

**Required IAM Permissions**:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeVolumes",
                "elasticloadbalancing:DescribeLoadBalancers",
                "elasticloadbalancing:DescribeTargetGroups",
                "elasticloadbalancing:DescribeTargetHealth",
                "autoscaling:DescribeAutoScalingGroups",
                "rds:DescribeDBInstances",
                "cloudwatch:GetMetricStatistics"
            ],
            "Resource": "*"
        }
    ]
}
```

### 1.3 Configure LLM Access

Create `.env` file in project root:

```bash
# .env
LLM_API_KEY=your-nvidia-nim-api-key
LLM_BASE_URL=https://integrate.api.nvidia.com/v1
LLM_MODEL=nvidia/nemotron-3-super-120b-a12b
```

**Get NVIDIA NIM API Key**:
1. Go to https://build.nvidia.com/
2. Sign in / create account
3. Navigate to API Keys
4. Create new key

**Supported Models** (NVIDIA NIM):
- `nvidia/nemotron-3-super-120b-a12b` (default, recommended)
- `nvidia/nemotron-3-ultra-550b-a55b`
- `meta/llama-3.1-405b-instruct`
- `meta/llama-3.1-70b-instruct`
- `mistralai/mistral-large-2-instruct`

### 1.4 Configure Target Region (Optional)

Edit `main.py`:
```python
REGION = "us-east-1"  # Change to your region
```

Or set via environment:
```bash
export AWS_REGION=eu-west-1
```

---

## Phase 2: Execute Analysis

### 2.1 Run the Agent

```bash
# Using uv (recommended)
uv run python main.py

# Or using installed console script
uv run aws-ai-devops-agent
```

### 2.2 What Happens During Execution

```
Step 1: Initialize AWS Clients
        ├── EC2 client
        ├── ELBv2 client
        ├── AutoScaling client
        ├── RDS client
        └── CloudWatch client

Step 2: Collect Infrastructure Snapshot (aws/health.py)
        ├── EC2: DescribeInstances → list_instances()
        ├── ALB: DescribeLoadBalancers → list_load_balancers()
        │   └── For each ALB: DescribeTargetGroups + DescribeTargetHealth
        ├── ASG: DescribeAutoScalingGroups → list_auto_scaling_groups()
        ├── EBS: DescribeVolumes → list_volumes()
        └── RDS: DescribeDBInstances → list_db_instances()

Step 3: Collect Metrics (aws/metrics.py + aws/cloudwatch.py)
        ├── EC2 CPU: GetMetricStatistics (AWS/EC2, CPUUtilization, 30min)
        └── RDS: GetMetricStatistics (AWS/RDS, 30min)
            ├── CPUUtilization
            ├── DatabaseConnections
            └── FreeStorageSpace

Step 4: Build Evidence (agent/evidence.py)
        └── Merge infrastructure + metrics into unified structure

Step 5: Build Prompt (agent/prompts.py)
        └── Format evidence as JSON + analysis instructions

Step 6: LLM Analysis (agent/llm.py)
        └── Send to NVIDIA NIM → Return analysis

Step 7: Output Results
        └── Print formatted analysis to stdout
```

### 2.3 Expected Output

```
Collecting AWS evidence...
Analyzing infrastructure...

======================================================================
AI DEVOPS ANALYSIS
======================================================================

[LLM Analysis Output - varies based on infrastructure state]
```

---

## Phase 3: Analyze Results

### 3.1 Understanding the Analysis Output

The LLM provides structured analysis covering:

| Section | Description |
|---------|-------------|
| **Overall Health** | High-level assessment (Healthy / Degraded / Critical) |
| **Critical Anomalies** | Specific metrics or states exceeding thresholds |
| **Most Likely Problems** | Root cause hypotheses with confidence |
| **Evidence** | Specific data points supporting each finding |
| **Recommended Investigation** | Next steps to confirm/deny hypotheses |
| **Human Intervention Required** | Yes/No with justification |

### 3.2 Example Analysis Output

```
OVERALL HEALTH: DEGRADED

CRITICAL ANOMALIES:
1. EC2 Instance i-0a1b2c3d4e5f6g7h8: CPU at 94.2% average (30min), peak 99.1%
2. RDS Instance prod-db-1: Free storage at 2.3 GB (2.3% of 100 GB allocated)
3. ALB app-alb: Target group tg-api has 3/5 targets unhealthy

MOST LIKELY PROBLEMS:
1. [HIGH CONFIDENCE] CPU saturation on i-0a1b2c3d4e5f6g7h8
   Evidence: CPU 30min avg 94.2%, max 99.1%, instance type t3.medium (2 vCPU)
   
2. [HIGH CONFIDENCE] RDS storage exhaustion imminent
   Evidence: FreeStorageSpace 2.3 GB, trend -0.5 GB/hour, will exhaust in ~4.6 hours
   
3. [MEDIUM CONFIDENCE] Application health degradation
   Evidence: 60% target unhealthy, correlates with EC2 CPU saturation

RECOMMENDED INVESTIGATION:
1. Check application logs on i-0a1b2c3d4e5f6g7h8 for CPU-intensive processes
2. Enable RDS storage autoscaling or increase allocated storage immediately
3. Review ALB access logs for error patterns on unhealthy targets
4. Check ASG scaling policies - desired capacity may be insufficient

HUMAN INTERVENTION REQUIRED: YES
- RDS storage requires immediate action (destructive if exhausted)
- EC2 CPU may require instance type upgrade or horizontal scaling
```

### 3.3 Interpreting Confidence Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **HIGH** | Multiple corroborating metrics | Act immediately |
| **MEDIUM** | Single metric anomaly, plausible cause | Investigate within hours |
| **LOW** | Weak signal, needs correlation | Monitor, investigate if persists |

---

## Phase 4: Act on Findings

### 4.1 Prioritization Matrix

```
┌─────────────────────┬──────────────┬──────────────┬──────────────┐
│                     │  HIGH CONF   │  MED CONF    │  LOW CONF    │
├─────────────────────┼──────────────┼──────────────┼──────────────┤
│ CRITICAL IMPACT     │ IMMEDIATE    │ URGENT       │ INVESTIGATE  │
│ (data loss, down)   │ (minutes)    │ (hours)      │ (hours)      │
├─────────────────────┼──────────────┼──────────────┼──────────────┤
│ HIGH IMPACT         │ URGENT       │ SCHEDULE     │ MONITOR      │
│ (degraded perf)     │ (hours)      │ (same day)   │ (ongoing)    │
├─────────────────────┼──────────────┼──────────────┼──────────────┤
│ MEDIUM IMPACT       │ SCHEDULE     │ MONITOR      │ LOG          │
│ (capacity risk)     │ (this week)  │ (ongoing)    │ (review)     │
└─────────────────────┴──────────────┴──────────────┴──────────────┘
```

### 4.2 Common Remediation Actions

#### EC2 High CPU
```bash
# Option 1: Vertical scaling (requires stop/start)
aws ec2 stop-instances --instance-ids i-123
aws ec2 modify-instance-attribute --instance-id i-123 --instance-type t3.large
aws ec2 start-instances --instance-ids i-123

# Option 2: Horizontal scaling (ASG)
aws autoscaling set-desired-capacity --auto-scaling-group-name my-asg --desired-capacity 5

# Option 3: Investigate application
ssh ec2-user@i-123
top -bn1 | head -20
```

#### RDS Low Storage
```bash
# Enable storage autoscaling (preferred)
aws rds modify-db-instance \
    --db-instance-identifier prod-db-1 \
    --max-allocated-storage 500 \
    --apply-immediately

# Or manual increase
aws rds modify-db-instance \
    --db-instance-identifier prod-db-1 \
    --allocated-storage 200 \
    --apply-immediately
```

#### Unhealthy ALB Targets
```bash
# Check target health details
aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:...

# Check instance health
aws ec2 describe-instance-status --instance-ids i-123 i-456

# Check application logs
# (depends on your logging setup)
```

### 4.3 Verification After Remediation

```bash
# Re-run analysis to verify fix
uv run python main.py

# Or monitor specific metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/EC2 \
    --metric-name CPUUtilization \
    --dimensions Name=InstanceId,Value=i-123 \
    --start-time $(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Average
```

---

## Scheduled/Automated Execution

### 4.4 Cron Job (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Run every 15 minutes
*/15 * * * * cd /path/to/aws-ai-devops-agent && /usr/local/bin/uv run python main.py >> /var/log/aws-ai-devops.log 2>&1

# Run hourly with notification on issues
0 * * * * cd /path/to/aws-ai-devops-agent && /usr/local/bin/uv run python main.py 2>&1 | grep -E "(CRITICAL|DEGRADED)" && mail -s "AWS AI DevOps Alert" ops@example.com
```

### 4.5 GitHub Actions

```yaml
# .github/workflows/aws-health-check.yml
name: AWS Health Check

on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes
  workflow_dispatch:  # Manual trigger

jobs:
  health-check:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
          aws-region: us-east-1
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.14'
      
      - name: Install uv
        run: pip install uv
      
      - name: Install dependencies
        run: uv sync
      
      - name: Run health check
        env:
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
          LLM_BASE_URL: ${{ secrets.LLM_BASE_URL }}
          LLM_MODEL: ${{ secrets.LLM_MODEL }}
        run: uv run python main.py
      
      - name: Create issue on critical findings
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: 'AWS Health Check: Critical Findings',
              body: 'Automated health check detected critical issues. Check workflow logs.',
              labels: ['aws', 'health-check', 'critical']
            })
```

### 4.6 AWS EventBridge + Lambda (Serverless)

```python
# lambda_function.py
import json
import boto3
import os
import subprocess

def lambda_handler(event, context):
    # Run the analysis
    result = subprocess.run(
        ['python', 'main.py'],
        cwd='/var/task',
        capture_output=True,
        text=True,
        timeout=300
    )
    
    # Check for critical findings
    output = result.stdout
    if 'CRITICAL' in output or 'DEGRADED' in output:
        # Send to SNS
        sns = boto3.client('sns')
        sns.publish(
            TopicArn=os.environ['ALERT_TOPIC_ARN'],
            Subject='AWS AI DevOps Alert',
            Message=output
        )
    
    # Log to CloudWatch
    print(output)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Health check completed')
    }
```

---

## Troubleshooting Workflow

### 5.1 Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| `LLM_API_KEY not configured` | Missing .env | Create .env with LLM_API_KEY |
| `NoCredentialsError` | AWS creds not found | Configure AWS credentials |
| `AccessDenied` | Insufficient IAM permissions | Add required permissions to role/user |
| `Timeout` | Too many resources | Reduce region scope or add pagination |
| `Rate limit` | Too many API calls | Add delays, reduce frequency |

### 5.2 Debug Mode

```bash
# Enable debug logging
export AWS_DEBUG=1
export PYTHONPATH=/path/to/aws-ai-devops-agent
uv run python -c "
from aws.client import AWSClients
from agent.evidence import build_evidence
import json

aws = AWSClients('us-east-1')
evidence = build_evidence(aws)
print(json.dumps(evidence, indent=2, default=str))
"
```

### 5.3 Test Individual Components

```bash
# Test EC2 collection
uv run python -c "
from aws.client import AWSClients
from aws.ec2 import list_instances
aws = AWSClients('us-east-1')
print(list_instances(aws))
"

# Test CloudWatch metrics
uv run python -c "
from aws.client import AWSClients
from aws.cloudwatch import get_ec2_cpu
aws = AWSClients('us-east-1')
print(get_ec2_cpu(aws, 'i-1234567890abcdef0'))
"

# Test LLM connection
uv run python -c "
from agent.llm import LLM
llm = LLM()
print(llm.analyze('Test prompt: Say hello'))
"
```

---

## Monitoring the Agent Itself

### 5.4 Health Check for the Agent

Create a wrapper script:

```bash
#!/bin/bash
# health-check-wrapper.sh

set -e

LOG_FILE="/var/log/aws-ai-devops-agent.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] Starting health check..." >> $LOG_FILE

cd /path/to/aws-ai-devops-agent

if uv run python main.py >> $LOG_FILE 2>&1; then
    echo "[$TIMESTAMP] Health check completed successfully" >> $LOG_FILE
else
    echo "[$TIMESTAMP] Health check FAILED" >> $LOG_FILE
    # Alert
    aws sns publish --topic-arn $ALERT_TOPIC --message "Agent health check failed"
fi
```

---

## Workflow Variants

### 6.1 Quick Check (Single Resource)

```bash
# Modify main.py temporarily for focused check
# Or create a focused script:
uv run python -c "
from aws.client import AWSClients
from aws.ec2 import list_instances
from aws.cloudwatch import get_ec2_cpu, summarize_metric

aws = AWSClients('us-east-1')
instances = list_instances(aws)
for i in instances:
    if i['state'] == 'running':
        cpu = get_ec2_cpu(aws, i['id'], minutes=10)
        print(f\"{i['id']} ({i['type']}): {summarize_metric(cpu)}\")
"
```

### 6.2 Multi-Region Analysis

```python
# multi_region_check.py
from aws.client import AWSClients
from agent.evidence import build_evidence
from agent.prompts import build_health_prompt
from agent.llm import LLM

REGIONS = ['us-east-1', 'us-west-2', 'eu-west-1']

for region in REGIONS:
    print(f"\n=== {region} ===")
    aws = AWSClients(region)
    evidence = build_evidence(aws)
    prompt = build_health_prompt(evidence)
    llm = LLM()
    analysis = llm.analyze(prompt)
    print(analysis)
```

### 6.3 CI/CD Pipeline Integration

```yaml
# In your deployment pipeline
- name: Pre-deployment health check
  run: |
    uv run python main.py
    # Fail deployment if critical issues found
    if grep -q "CRITICAL" output.txt; then
      echo "Critical issues found, aborting deployment"
      exit 1
    fi
```

---

## Best Practices

### 7.1 Operational Best Practices

1. **Run regularly**: Every 15-30 minutes for production
2. **Alert on critical**: Set up SNS/email/Slack for CRITICAL/DEGRADED
3. **Log everything**: Keep historical analysis for trend detection
4. **Review weekly**: Human review of all findings weekly
5. **Tune thresholds**: Adjust prompt for your environment's norms

### 7.2 Cost Optimization

- **LLM calls**: ~$0.01-0.10 per analysis depending on model
- **CloudWatch API**: ~$0.01 per 1000 GetMetricStatistics calls
- **Typical run**: ~50-100 API calls = <$0.01
- **Monthly (15min intervals)**: ~3000 runs = ~$30-300 LLM + ~$3 API

### 7.3 Security Best Practices

- Use IAM roles, not access keys
- Restrict LLM API key permissions
- Don't log full evidence (contains resource IDs)
- Review data sent to LLM for sensitivity

---

## Workflow Summary Checklist

### Daily
- [ ] Automated runs executing successfully
- [ ] Alerts received for critical findings
- [ ] Remediation actions taken on critical issues

### Weekly
- [ ] Review all analysis outputs
- [ ] Update prompt if false positives/negatives
- [ ] Verify IAM permissions still correct
- [ ] Check LLM API key validity

### Monthly
- [ ] Review cost of LLM + CloudWatch API calls
- [ ] Evaluate new AWS services to add
- [ ] Update dependencies (uv sync)
- [ ] Review and update runbook procedures

---

## Quick Reference Card

```bash
# One-liner for manual run
uv run python main.py

# With custom region
AWS_REGION=eu-west-1 uv run python main.py

# Debug evidence only
uv run python -c "
from aws.client import AWSClients
from agent.evidence import build_evidence
import json
aws = AWSClients('us-east-1')
print(json.dumps(build_evidence(aws), indent=2, default=str))
"

# Test LLM only
uv run python -c "
from agent.llm import LLM
llm = LLM()
print(llm.analyze('Test: Respond with OK'))
"
```

---

## Support & Escalation

| Issue Type | Contact |
|------------|---------|
| Agent bugs | Create GitHub issue |
| AWS permissions | Cloud/Platform team |
| LLM API issues | NVIDIA NIM support |
| Infrastructure issues | On-call engineer |

---

*Last Updated: 2026-10-08*
*Version: 1.0*