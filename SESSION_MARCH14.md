# Session Walkthrough — March 14, 2026 (Updated 4:14 PM)

**Time**: 11:00 AM → 4:14 PM (5+ hours)  
**Goal**: Set up Cognee MCP Server for OpenClaw MVP  
**Deadline**: March 15, 2026  

---

## CURRENT STATE: Migrating to Official Cognee MCP Server

We discovered our `cognee_mcp_server.py` was a **custom simplified version** (5 tools), not the official one. The official server from `github.com/topoteretes/cognee/tree/main/cognee-mcp` has **10+ tools** including code analysis, interaction logging, and developer rules.

We are now installing the official version. **Nothing has been deleted** — the old server is untouched.

---

## Directory Layout (NOTHING DELETED)

```
~/Desktop/install_link/
├── cognee/                  ← OUR CUSTOM REPO (untouched, pushed to GitHub)
│   ├── cognee_mcp_server.py    ← Custom MCP server (5 tools, still works)
│   ├── ingest_rules.py         ← Working ingestion script
│   ├── prune_memory.py         ← Memory reset utility
│   ├── global_rules.md         ← System rules
│   ├── troubleshooting_guide.md
│   ├── SESSION_MARCH14.md      ← This file
│   ├── .env                    ← Our config (DO NOT DELETE)
│   └── .venv/                  ← Working Python venv
│
└── cognee-official/         ← OFFICIAL COGNEE REPO (just cloned)
    └── cognee-mcp/
        ├── src/server.py       ← Official MCP server (10+ tools)
        ├── pyproject.toml      ← Modified: removed postgres extra
        └── .venv/              ← Being installed via uv sync
```

---

## Git History (All Safely Pushed)

**Repo**: `https://github.com/dfwconnect0-creator/cognee-mcp-server.git`

```
697a92b feat: add missing cognee_search tool to MCP server
bcb28b8 feat: add prune_memory.py reset utility
042a896 fix: working ingest_rules.py with correct search API
f0a53a1 docs: add troubleshooting guide and rules, fix environment
af8e258 Initial commit: last working cognee MCP server (pre-reinstall)
```

---

## Phase 1: Initial Setup (COMPLETE ✅)

1. ✅ Fixed broken Python venv (3.10 → 3.12)
2. ✅ Installed missing deps (transformers, neo4j)
3. ✅ Configured Ollama (llama3.2, nomic-embed-text)
4. ✅ Fixed Neo4j APOC plugin (recreated Docker with NEO4J_PLUGINS='["apoc"]')
5. ✅ Ingested global_rules.md into knowledge graph
6. ✅ Verified search works (3/3 tests passing)
7. ✅ Created troubleshooting_guide.md + prune_memory.py
8. ✅ All code committed and pushed to GitHub

## Phase 2: Official MCP Server Migration (IN PROGRESS)

1. ✅ Verified official server at github.com/topoteretes/cognee/tree/main/cognee-mcp
2. ✅ Cloned official cognee repo to ~/Desktop/install_link/cognee-official
3. ✅ Installed uv globally via curl (to ~/.local/bin)
4. ✅ Modified pyproject.toml: removed `postgres` extra (we use Neo4j+SQLite)
5. 🔄 Running `uv sync` to install dependencies (~5-8 min)
6. ⬜ Copy .env from our repo to official cognee-mcp
7. ⬜ Update ~/.gemini/antigravity/mcp_config.json to point to official server
8. ⬜ Restart Antigravity and test MCP connection

## Phase 3: Next Steps (PENDING)

1. ⬜ ComfyUI pipeline setup
2. ⬜ End-to-end OpenClaw MVP test

---

## Key Configs (BACKUP)

### .env (at ~/Desktop/install_link/cognee/.env)
```
LLM_PROVIDER="ollama"
LLM_MODEL="llama3.2:latest"
LLM_ENDPOINT="http://localhost:11434/v1"
LLM_API_KEY="ollama"
EMBEDDING_PROVIDER="ollama"
EMBEDDING_MODEL="nomic-embed-text:latest"
EMBEDDING_ENDPOINT="http://localhost:11434/api/embed"
EMBEDDING_DIMENSIONS="768"
HUGGINGFACE_TOKENIZER="nomic-ai/nomic-embed-text-v1.5"
GRAPH_DATABASE_PROVIDER="neo4j"
GRAPH_DATABASE_URL="bolt://localhost:7687"
GRAPH_DATABASE_USERNAME="neo4j"
GRAPH_DATABASE_PASSWORD="cognee_local_2026"
GRAPH_DATASET_DATABASE_HANDLER="neo4j_aura_dev"
ENABLE_BACKEND_ACCESS_CONTROL="false"
VECTOR_DB_PROVIDER="lancedb"
DB_PROVIDER="sqlite"
```

### Antigravity MCP Config (will be updated after uv sync)
```json
{
  "mcpServers": {
    "cognee_mcp": {
      "command": "<path-to-official-venv>/bin/python3",
      "args": ["<path-to-official>/cognee-mcp/src/server.py"],
      "env": {},
      "disabled": false
    }
  }
}
```

### Neo4j Docker (running)
```bash
sudo docker run \
    --name neo4j --restart always \
    --publish=7474:7474 --publish=7687:7687 \
    --env NEO4J_AUTH=neo4j/cognee_local_2026 \
    --env NEO4J_PLUGINS='["apoc"]' \
    -d neo4j:latest
```

---

## Rollback Plan (if official server fails)

If the official server doesn't work, we can immediately revert:
1. Edit `~/.gemini/antigravity/mcp_config.json` back to original paths
2. Original server at `~/Desktop/install_link/cognee/cognee_mcp_server.py` still works
3. All data in Neo4j and LanceDB is untouched — no data loss

---

## Errors Fixed Today (Reference)

1. Broken .venv (Python 3.10 symlinks on 3.12) → Recreated venv
2. Missing transformers → uv pip install transformers
3. Missing qwen2.5:7b → Switched to llama3.2:latest
4. Missing nomic-embed-text → ollama pull nomic-embed-text
5. Missing neo4j package → pip install neo4j
6. Neo4j APOC missing → Recreated Docker with NEO4J_PLUGINS
7. Wrong cognee.search() API → Fixed to use query_text= keyword arg
8. Missing cognee_search tool → Added to custom server (but now switching to official)
