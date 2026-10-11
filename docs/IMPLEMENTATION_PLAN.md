# InfraBuddy AI - Implementation Plan

## Repository Baseline Assessment

### Current State (Milestone 1 Complete)

**What Exists:**
- Python CLI application (`main.py`) that collects AWS infrastructure evidence and sends to LLM
- AWS service modules: EC2, ALB, ASG, EBS, RDS, CloudWatch
- Evidence collection and prompt building pipeline
- NVIDIA Nemotron integration via OpenAI-compatible API (hardcoded)
- MCP Server (Node.js) exposing 40+ AWS resources as MCP resources
- Basic project structure with `uv` for dependency management

**What's Missing/Incomplete:**
- ❌ No FastAPI backend
- ❌ No Strands Agents integration
- ❌ No configurable model provider abstraction
- ❌ No sample-data mode (requires real AWS credentials)
- ❌ No structured diagnosis output (free-text only)
- ❌ No frontend/dashboard
- ❌ No Docker/Docker Compose configuration
- ❌ No tests (unit, integration, mocked)
- ❌ No CI/CD pipeline
- ❌ No security hardening (secrets handling, input validation, audit logging)
- ❌ No Slack/ChatOps integration
- ❌ No Terraform infrastructure

**Broken/Issues:**
- `src/aws_ai_devops_agent/` is empty (console script points to non-existent module)
- Duplicate `get_ec2_evidence` function in `aws/metrics.py`
- LLM class raises `ValueError` if env vars missing (no sample mode fallback)
- Hardcoded region in `main.py`
- No request timeouts or retries on AWS calls
- No input validation on resource identifiers

---

## Architecture Overview (Target)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           InfraBuddy AI Platform                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐  │
│  │   Frontend   │◄──▶│   FastAPI    │◄──▶│  Orchestrator│◄──▶│Specialist│  │
│  │  (Dashboard) │    │   Backend    │    │    Agent     │    │ Agents   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘    └──────────┘  │
│                            │                       │                         │
│                            ▼                       ▼                         │
│                   ┌──────────────┐    ┌────────────────────────────────┐   │
│                   │ Model Provider│    │      AWS Tool Registry        │   │
│                   │  Abstraction  │    │  (Allowlisted Read-Only Ops)  │   │
│                   └──────────────┘    └────────────────────────────────┘   │
│                            │                       │                         │
│                            ▼                       ▼                         │
│                   ┌──────────────┐    ┌────────────────────────────────┐   │
│                   │ NVIDIA Nemotron│    │  Boto3 / MCP Server / SSM    │   │
│                   │  (Primary)    │    │  (Future: Systems Manager)   │   │
│                   └──────────────┘    └────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Milestone 2 — NVIDIA Model Integration & Provider Abstraction

### Objective
Create a configurable model provider interface supporting NVIDIA Nemotron Super with sample-data fallback mode.

### Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `agent/providers/__init__.py` | Create | Provider abstraction package |
| `agent/providers/base.py` | Create | Abstract base class `ModelProvider` |
| `agent/providers/nvidia.py` | Create | NVIDIA Nemotron implementation |
| `agent/providers/sample.py` | Create | Sample-data provider for offline mode |
| `agent/providers/factory.py` | Create | Factory to select provider by config |
| `agent/llm.py` | Modify | Refactor to use provider abstraction |
| `agent/config.py` | Create | Configuration management (Pydantic Settings) |
| `.env.example` | Create | Template for environment variables |
| `pyproject.toml` | Modify | Add `pydantic-settings`, `httpx` dependencies |

### Security Risks & Assumptions
- **Risk**: API keys exposed in logs → **Mitigation**: Never log full keys, use `***` masking
- **Risk**: Unvalidated model responses → **Mitigation**: Schema validation on all responses
- **Assumption**: NVIDIA NIM API is OpenAI-compatible (verified via docs)
- **Assumption**: Sample mode returns deterministic mock data for testing

### Acceptance Criteria
- [ ] Application runs without AWS credentials or NVIDIA API key (sample mode)
- [ ] Switching providers requires only config change
- [ ] Rate limits, timeouts, malformed responses handled gracefully
- [ ] Structured output (JSON) from model, not free text

---

## Milestone 3 — Diagnostic Agent & EC2 CPU Workflow

### Objective
Integrate Strands Agents, implement EC2 CPU investigation workflow with allowlisted tools.

### Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `agent/tools/__init__.py` | Create | Tool registry package |
| `agent/tools/aws_tools.py` | Create | Allowlisted read-only AWS diagnostic tools |
| `agent/tools/validation.py` | Create | Input validation for resource IDs, regions |
| `agent/agents/__init__.py` | Create | Agents package |
| `agent/agents/orchestrator.py` | Create | Orchestrator agent with Strands |
| `agent/agents/specialists/ec2_cpu.py` | Create | EC2 CPU specialist agent |
| `agent/schemas/diagnosis.py` | Create | Pydantic models for structured diagnosis |
| `agent/prompts.py` | Modify | Update prompts for structured output |
| `pyproject.toml` | Modify | Add `strands-agents`, `strands-agents-tools` dependencies |

### Allowlisted Tools (Read-Only)
```python
# EC2 Tools
- get_instance_metadata(instance_id: str, region: str) -> InstanceMetadata
- get_cpu_metrics(instance_id: str, region: str, minutes: int) -> CPUMetrics
- get_instance_status_checks(instance_id: str, region: str) -> StatusChecks

# CloudWatch Tools
- get_metric_statistics(namespace, metric_name, dimensions, period, stat) -> MetricData

# CloudTrail Tools (future)
- lookup_events(resource_id, start_time, end_time) -> Events
```

### Security Risks & Assumptions
- **Risk**: Tool injection → **Mitigation**: Strict allowlist, no dynamic tool registration
- **Risk**: Resource ID injection → **Mitigation**: Regex validation (e.g., `^i-[0-9a-f]{8,17}$`)
- **Risk**: Model hallucinates metrics → **Mitigation**: Tools return typed data, model cannot invent values
- **Assumption**: Strands Agents supports tool calling with structured output

### Acceptance Criteria
- [ ] Single-agent workflow diagnoses high EC2 CPU
- [ ] Input validation rejects invalid instance IDs/regions
- [ ] Missing metrics, permission errors, unavailable instances handled
- [ ] Structured diagnosis: problem, evidence, hypotheses, confidence, recommendations, runbook refs
- [ ] Audit event logged (sanitized, no secrets)

---

## Milestone 4 — FastAPI Backend & Dashboard

### Objective
Expose diagnostic workflow via REST API, connect existing frontend.

### Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `api/__init__.py` | Create | API package |
| `api/main.py` | Create | FastAPI app with lifespan, middleware |
| `api/routes/diagnose.py` | Create | POST `/api/v1/diagnose/ec2-cpu` endpoint |
| `api/routes/health.py` | Create | GET `/health` endpoint |
| `api/models/requests.py` | Create | Request/response Pydantic models |
| `api/models/responses.py` | Create | Diagnosis response models |
| `api/middleware/auth.py` | Create | Optional API key auth for future |
| `api/middleware/logging.py` | Create | Structured request logging |
| `frontend/` | Create/Modify | React/Vue dashboard (preserve existing if any) |
| `docker-compose.yml` | Create | Local dev stack (API, frontend, mock services) |
| `Dockerfile` | Create | Multi-stage build for API |
| `pyproject.toml` | Modify | Add `fastapi`, `uvicorn`, `pydantic`, `python-multipart` |

### API Contract (EC2 CPU Diagnosis)
```python
# POST /api/v1/diagnose/ec2-cpu
Request:
{
  "instance_id": "i-0123456789abcdef0",
  "region": "us-east-1",
  "lookback_minutes": 30
}

Response:
{
  "diagnosis_id": "diag-abc123",
  "timestamp": "2026-10-10T12:00:00Z",
  "instance_id": "i-0123456789abcdef0",
  "problem_summary": "CPU sustained >90% for 25 minutes",
  "evidence": [
    {"metric": "CPUUtilization", "value": 94.2, "timestamp": "..."},
    {"metric": "StatusCheck", "value": "passed", "timestamp": "..."}
  ],
  "hypotheses": [
    {"cause": "Application load spike", "confidence": 0.7, "evidence_refs": [0]},
    {"cause": "Runaway process", "confidence": 0.2, "evidence_refs": []},
    {"cause": "Noisy neighbor", "confidence": 0.1, "evidence_refs": []}
  ],
  "confidence": 0.7,
  "uncertainty": "Cannot inspect OS-level processes without SSM",
  "recommended_steps": [
    "Check application logs for traffic spike",
    "Review recent deployments",
    "Enable detailed monitoring for 1-min granularity"
  ],
  "safe_remediation": [
    {"action": "Scale out ASG", "risk": "low", "requires_approval": true},
    {"action": "Restart application service", "risk": "medium", "requires_approval": true}
  ],
  "runbook_references": [
    {"title": "High CPU Troubleshooting", "url": "runbooks/ec2-high-cpu.md"}
  ],
  "audit_event_id": "audit-xyz789"
}
```

### Security Risks & Assumptions
- **Risk**: Unauthenticated API access → **Mitigation**: API key middleware (optional in dev, required in prod)
- **Risk**: SSRF via region parameter → **Mitigation**: Allowlist valid AWS regions
- **Risk**: Large request payloads → **Mitigation**: Request size limits
- **Assumption**: Frontend served separately or via FastAPI static files

### Acceptance Criteria
- [ ] API starts and serves `/health` endpoint
- [ ] EC2 CPU diagnosis endpoint returns structured response
- [ ] Dashboard displays loading, error, evidence, diagnosis, recommendations states
- [ ] Sample mode works without AWS credentials
- [ ] Request validation with clear error messages

---

## Milestone 5 — Tests & Reliability

### Objective
Comprehensive test coverage for all components, CI/CD pipeline.

### Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `tests/__init__.py` | Create | Test package |
| `tests/conftest.py` | Create | Pytest fixtures (mock AWS, sample data) |
| `tests/unit/test_providers.py` | Create | Provider unit tests |
| `tests/unit/test_tools.py` | Create | AWS tool validation tests |
| `tests/unit/test_schemas.py` | Create | Schema validation tests |
| `tests/integration/test_diagnose_flow.py` | Create | End-to-end diagnosis flow tests |
| `tests/security/test_injection.py` | Create | Prompt injection, ID validation tests |
| `tests/fixtures/sample_evidence.py` | Create | Sample evidence data for testing |
| `.github/workflows/ci.yml` | Create | GitHub Actions CI pipeline |
| `.github/workflows/cd.yml` | Create | GitHub Actions CD pipeline (staging) |
| `pyproject.toml` | Modify | Add `pytest`, `pytest-asyncio`, `pytest-mock`, `moto`, `ruff`, `mypy` |

### Test Scenarios (Must Pass)
| Scenario | Expected Behavior |
|----------|-------------------|
| Missing AWS credentials | Sample mode activates, returns mock diagnosis |
| Invalid instance ID format | 400 error with validation message |
| Instance not found | 404 with clear message |
| AccessDenied on CloudWatch | Graceful degradation, partial evidence noted |
| Empty metrics (new instance) | Hypothesis: "Insufficient data", low confidence |
| API timeout (NVIDIA) | Retry with backoff, then fallback to sample |
| Prompt injection attempt | Rejected, audit logged, safe response |
| Rate limit (NVIDIA) | Exponential backoff, circuit breaker |

### Acceptance Criteria
- [ ] Unit test coverage >80% for business logic
- [ ] Integration tests mock all external dependencies
- [ ] Security tests validate input sanitization
- [ ] CI runs on every PR, blocks on failure
- [ ] Linting (ruff) and type checking (mypy) pass

---

## Milestone 6 — Specialist Agents Expansion

### Objective
Add ALB health, networking, RDS specialists behind tested interfaces.

### Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `agent/agents/specialists/alb_health.py` | Create | ALB target health specialist |
| `agent/agents/specialists/networking.py` | Create | VPC, SG, routing specialist |
| `agent/agents/specialists/rds.py` | Create | RDS performance specialist |
| `agent/agents/orchestrator.py` | Modify | Route to specialists based on problem type |
| `agent/tools/aws_tools.py` | Extend | Add ALB, VPC, RDS read-only tools |
| `api/routes/diagnose.py` | Extend | Add `/alb-health`, `/network`, `/rds` endpoints |
| `tests/integration/test_specialists.py` | Create | Specialist integration tests |

### Acceptance Criteria
- [ ] Each specialist has dedicated tests covering happy/error paths
- [ ] Orchestrator correctly routes based on user query
- [ ] All tools remain read-only, allowlisted
- [ ] Structured diagnosis format consistent across specialists

---

## Milestone 7+ — Future (Separate Reviewed Milestones)

| Milestone | Scope |
|-----------|-------|
| 7 | Slack ChatOps integration (slash commands, interactive messages) |
| 8 | AWS Systems Manager integration for OS-level diagnostics |
| 9 | Remediation approval workflow (human-in-the-loop) |
| 10 | Terraform infrastructure for AWS deployment |
| 11 | Multi-region, multi-account support |
| 12 | Knowledge base / runbook ingestion (RAG) |

---

## Engineering Standards Checklist

- [ ] Type hints on all public functions
- [ ] Pydantic validation on all inputs/outputs
- [ ] Clear separation: routes → services → agents → tools → providers
- [ ] No hardcoded credentials or endpoints
- [ ] Meaningful docstrings (Google style)
- [ ] Structured logging (JSON) with correlation IDs
- [ ] `.env.example` updated with all required variables
- [ ] README updated with quickstart, architecture, API docs
- [ ] Security documentation (threat model, data handling)
- [ ] CHANGELOG.md maintained

---

## Next Steps

1. **Immediate**: Create `docs/IMPLEMENTATION_PLAN.md` (this file) ✓
2. **Next**: Begin Milestone 2 - Provider abstraction and NVIDIA integration
3. **Then**: Milestone 3 - Diagnostic agent with Strands
4. **Then**: Milestone 4 - FastAPI + Dashboard
5. **Then**: Milestone 5 - Tests + CI/CD
6. **Then**: Milestone 6 - Specialist expansion

---

## Appendix: Current File Inventory

```
aws-ai-devops-agent/
├── .agents/                    # Agent skill definitions
├── .claude/                    # Claude configuration
├── .github/                    # GitHub workflows (to be created)
├── .venv/                      # Virtual environment
├── agent/
│   ├── evidence.py             # Evidence aggregation
│   ├── llm.py                  # LLM client (needs refactor)
│   └── prompts.py              # Prompt templates
├── api/                        # TO BE CREATED (Milestone 4)
├── aws/
│   ├── __init__.py
│   ├── alb.py                  # ALB operations
│   ├── asg.py                  # Auto Scaling Groups
│   ├── client.py               # Boto3 client factory
│   ├── cloudwatch.py           # CloudWatch metrics
│   ├── ebs.py                  # EBS volumes
│   ├── ec2.py                  # EC2 instances
│   ├── health.py               # Infrastructure snapshot
│   ├── metrics.py              # Metric aggregation (has duplicate)
│   └── rds.py                  # RDS instances
├── docs/
│   └── IMPLEMENTATION_PLAN.md  # THIS FILE
├── frontend/                   # TO BE CREATED (Milestone 4)
├── mcp-server/
│   └── index.js                # MCP server (Node.js)
├── tests/                      # TO BE CREATED (Milestone 5)
├── ARCHITECTURE.md             # Current architecture docs
├── WORKFLOW.md                 # Operational workflow docs
├── README.md                   # Project overview
├── main.py                     # CLI entry point
├── pyproject.toml              # Project config
├── uv.lock                     # Locked dependencies
└── .env                        # Local secrets (not committed)
```