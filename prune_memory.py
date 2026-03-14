"""
Prune Cognee Memory — One-command reset button.

Usage:
    python3 prune_memory.py                  # Wipe project data only (keeps global_rules)
    python3 prune_memory.py --all            # Wipe EVERYTHING including rules
    python3 prune_memory.py --dataset NAME   # Wipe a specific dataset
"""
import asyncio
import os
import sys
from pathlib import Path

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRUST_REMOTE_CODE"] = "true"
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

import cognee


async def prune(wipe_all: bool = False, dataset_name: str = None):
    if dataset_name:
        print(f"🗑️  Pruning dataset: {dataset_name}")
        await cognee.prune.prune_data(dataset_name)
        print(f"✅ Dataset '{dataset_name}' wiped.")
    elif wipe_all:
        print("⚠️  WIPING ALL COGNEE DATA (including global rules)...")
        await cognee.prune.prune_data()
        await cognee.prune.prune_system(metadata=True)
        print("✅ All data and metadata wiped. You'll need to re-ingest rules.")
    else:
        print("🗑️  Pruning all project data (keeping global_rules)...")
        await cognee.prune.prune_data()
        print("✅ Project data wiped. Global rules will need re-ingestion.")
        print("   Run: python3 ingest_rules.py")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--all" in args:
        asyncio.run(prune(wipe_all=True))
    elif "--dataset" in args:
        idx = args.index("--dataset")
        if idx + 1 < len(args):
            asyncio.run(prune(dataset_name=args[idx + 1]))
        else:
            print("❌ Usage: python3 prune_memory.py --dataset NAME")
    else:
        asyncio.run(prune())
