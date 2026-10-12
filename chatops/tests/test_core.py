"""
Unit tests for chatops.core and chatops.formatter.
"""

import pytest
from chatops.core import AnalysisResult, _filter_evidence
from chatops.formatter import (
    to_slack_blocks,
    to_slack_error_blocks,
    to_teams_adaptive_card,
    to_teams_error_card,
    _chunk_text,
)


def test_chunk_text_within_limit():
    text = "Short text."
    chunks = _chunk_text(text, 100)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_exceeding_limit():
    paragraphs = ["First paragraph " * 10, "Second paragraph " * 10]
    full_text = "\n\n".join(paragraphs)
    chunks = _chunk_text(full_text, 80)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 120  # bounded chunking


def test_filter_evidence_service_specific():
    sample_evidence = {
        "region": "us-east-1",
        "infrastructure": {
            "ec2": [{"id": "i-123"}],
            "rds": [{"id": "db-1"}],
        },
        "metrics": {
            "ec2": {"cpu": [10.5]},
            "rds": {"cpu": [20.1]},
        },
    }

    filtered = _filter_evidence(sample_evidence, "ec2")
    assert filtered["service_filter"] == "ec2"
    assert "ec2" in filtered["infrastructure"]
    assert "rds" not in filtered["infrastructure"]
    assert "ec2" in filtered["metrics"]
    assert "rds" not in filtered["metrics"]


def test_to_slack_blocks_success():
    result = AnalysisResult(
        success=True,
        region="us-east-1",
        service_filter="all",
        analysis="Everything is running smoothly.",
        provider="sample",
        model="sample-model",
        warnings=["Test warning"],
    )

    blocks = to_slack_blocks(result)
    assert len(blocks) >= 4
    assert any(b.get("type") == "header" for b in blocks)
    assert any("Test warning" in str(b) for b in blocks)
    assert any("Everything is running smoothly." in str(b) for b in blocks)


def test_to_slack_blocks_failure():
    result = AnalysisResult(
        success=False,
        region="us-east-1",
        service_filter="all",
        analysis="",
        error="Connection refused",
    )

    blocks = to_slack_blocks(result)
    assert len(blocks) == 1
    assert "Connection refused" in blocks[0]["text"]["text"]


def test_to_slack_error_blocks():
    blocks = to_slack_error_blocks("Something went wrong")
    assert len(blocks) == 1
    assert "Something went wrong" in blocks[0]["text"]["text"]


def test_to_teams_adaptive_card_success():
    result = AnalysisResult(
        success=True,
        region="us-east-1",
        service_filter="ec2",
        analysis="EC2 CPU utilization normal.",
        provider="sample",
        model="sample-model",
    )

    card = to_teams_adaptive_card(result)
    assert card["contentType"] == "application/vnd.microsoft.card.adaptive"
    body = card["content"]["body"]
    assert any(item.get("type") == "TextBlock" and "InfraBuddy" in item.get("text", "") for item in body)


def test_to_teams_adaptive_card_failure():
    result = AnalysisResult(
        success=False,
        region="us-east-1",
        service_filter="all",
        analysis="",
        error="Timeout",
    )

    card = to_teams_adaptive_card(result)
    body = card["content"]["body"]
    assert any("Timeout" in item.get("text", "") for item in body)


def test_to_teams_error_card():
    card = to_teams_error_card("Unauthorized")
    body = card["content"]["body"]
    assert any("Unauthorized" in item.get("text", "") for item in body)
