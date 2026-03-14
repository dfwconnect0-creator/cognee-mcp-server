#!/usr/bin/env python3
"""Ingest global rules into Cognee knowledge store."""
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env
load_dotenv(Path(__file__).parent / ".env")

import cognee
from cognee.api.v1.search import SearchType


async def ingest_rules():
    rules_file = Path(__file__).parent / "global_rules.md"
    rules_text = rules_file.read_text()

    print(f"📄 Read {len(rules_text)} chars from global_rules.md")

    print("➕ Adding rules to Cognee...")
    await cognee.add(rules_text)
    print("✅ Rules added to knowledge store")

    print("🧠 Building knowledge graph (this may take 30-120s)...")
    await cognee.cognify()
    print("✅ Knowledge graph built!")

    print("\n🔍 Testing search: 'What GPU does the system have?'")
    results = await cognee.search(query_text="What GPU does the system have?", query_type=SearchType.SUMMARIES)
    if results:
        for r in results[:3]:
            print(f"  → {r}")
    else:
        print("  ⚠️  No results (graph may need time to index)")

    print("\n🎉 Done! Rules are now searchable via cognee_search.")


if __name__ == "__main__":
    asyncio.run(ingest_rules())
