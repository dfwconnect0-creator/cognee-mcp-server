#!/usr/bin/env python3
"""
Ingest system rules into Cognee memory.
Run with: source .venv/bin/activate && python add_system_rules.py
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

import cognee

SYSTEM_RULES = """
# System Rules and Configuration

## Hardware
- GPU: RTX 3060 Ti, CUDA 12.8, nvidia-570 driver (LOCKED - never modify GPU config)
- SSD: ~/Projects (active work directory)
- HDD: /media/bladina/Archive (storage)
- AI Models location: /media/bladina/Archive/Archives/

## Package Management
- Always use uv, not pip, for Python package management

## Download Policy
- Ask before downloading anything larger than 300MB

## Install Policy
- Test after every install to verify it works correctly
"""


async def main():
    print("Adding system rules to Cognee memory...")

    # Add text to cognee
    await cognee.add(SYSTEM_RULES, dataset_name="system_rules")
    print("Text ingested. Building knowledge graph (cognify)...")

    # Process into knowledge graph
    await cognee.cognify()
    print("Knowledge graph built.")

    # Verify by searching
    print("\nVerifying — querying for 'GPU rules'...")
    results = await cognee.search("GPU configuration rules", query_type="insights")
    if results:
        print(f"Found {len(results)} result(s):")
        for r in results[:3]:
            print(f"  - {r}")
    else:
        print("No results returned (may need a moment to index).")

    print("\nDone. System rules are stored in Cognee memory.")


if __name__ == "__main__":
    asyncio.run(main())
