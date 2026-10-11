import json


def build_health_prompt(evidence: dict) -> str:
    return f"""
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
"""
