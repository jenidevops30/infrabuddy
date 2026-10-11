#!/usr/bin/env python3
"""
InfraBuddy AI - AWS Infrastructure Analysis CLI

Collects AWS infrastructure evidence and analyzes it using an LLM provider.
Supports both NVIDIA Nemotron and sample mode for offline development.
"""

import asyncio
import json
import logging
import sys

from agent.config import get_settings
from agent.llm import LLM
from agent.prompts import build_health_prompt
from aws.client import AWSClients
from agent.evidence import build_evidence

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    settings = get_settings()
    
    logger.info(f"Starting InfraBuddy AI analysis (region={settings.aws_region})")
    logger.info(f"Model provider: {settings.model_provider}, model: {settings.model_name}")
    
    # Create AWS clients
    aws = AWSClients(settings.aws_region)
    
    print("Collecting AWS evidence...")
    
    try:
        evidence = build_evidence(aws)
    except Exception as e:
        logger.error(f"Failed to collect AWS evidence: {e}")
        print(f"\nError collecting AWS evidence: {e}")
        print("Falling back to sample mode...")
        evidence = {"sample_mode": True, "error": str(e)}
    
    prompt = build_health_prompt(evidence)
    
    print("Analyzing infrastructure...")
    
    # Create LLM with configuration
    llm = LLM()
    
    try:
        analysis = llm.analyze(prompt)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        print(f"\nError during analysis: {e}")
        sys.exit(1)
    finally:
        # Clean up async resources
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(llm.close())
            else:
                loop.run_until_complete(llm.close())
        except Exception:
            pass
    
    print("\n" + "=" * 70)
    print("AI DEVOPS ANALYSIS")
    print("=" * 70)
    print()
    print(analysis)
    
    # Print provider info
    provider_info = llm.provider_info
    print("\n" + "-" * 70)
    print(f"Provider: {provider_info.get('provider', 'unknown')}")
    print(f"Model: {provider_info.get('model', 'unknown')}")


if __name__ == "__main__":
    main()
