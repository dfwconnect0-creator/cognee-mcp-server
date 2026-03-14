# Session Walkthrough — March 14, 2026 (Final Update 7:05 PM)

**Time**: 11:00 AM → 7:05 PM (8 hours)  
**Goal**: Set up Cognee MCP Server for OpenClaw MVP  
**Deadline**: March 15, 2026  
**Status**: ✅ Server works, ready for Antigravity restart

---

## What We Built

Official Cognee MCP server (10+ tools) running locally with:
- **Neo4j** + APOC (Docker) | **LanceDB** (vectors) | **SQLite** (metadata)
- **Ollama** llama3.2 (LLM) + nomic-embed-text (embeddings)
- **server_wrapper.py** silencing stdout noise for clean MCP JSON-RPC

---

## Directory Layout

```
~/Desktop/install_link/                     ← SYMLINK to /home/mo/Desktop/install/
├── cognee/                                 ← CUSTOM repo (backup, pushed to GitHub)
│   ├── cognee_mcp_server.py                   5-tool custom server (rollback)
│   ├── ingest_rules.py, prune_memory.py       Working utilities
│   ├── global_rules.md, .env                  Config files
│   └── SESSION_MARCH14.md                     This doc (also in GitHub)
│
└── cognee-official/                        ← OFFICIAL repo (git clone topoteretes/cognee)
    └── cognee-mcp/
        ├── src/server.py                      Official 10+ tool server
        ├── server_wrapper.py                  Stdout silencer + migration runner
        ├── .env                               Copied from custom repo
        └── .venv/                             Fresh, rebuilt with uv
```

---

## The 6 Traps We Hit (and How We Fixed Them)

### Trap 1: stdout Corruption ("0 Tools" Bug)
**Problem**: Official `server.py` prints logs to stdout → corrupts MCP JSON-RPC  
**Fix**: `server_wrapper.py` redirects `sys.stdout = sys.stderr` during import

### Trap 2: Empty Environment Variables
**Problem**: `"env": {}` in MCP config → Cognee defaults to OpenAI cloud  
**Fix**: Pass ALL env vars (Ollama, Neo4j, LanceDB) directly in `mcp_config.json`

### Trap 3: Missing Working Directory
**Problem**: No `"cwd"` → Python can't find `src/` imports → `ModuleNotFoundError`  
**Fix**: Added `"cwd": ".../cognee-mcp"` to MCP config

### Trap 4: Alembic Subprocess PATH Crash
**Problem**: Migration script calls bare `python` instead of venv Python  
**Fix**: `server_wrapper.py` injects venv `bin/` into `os.environ["PATH"]`

### Trap 5: HuggingFace Interactive Prompt
**Problem**: `trust_remote_code` prompt blocks server startup in non-interactive mode  
**Fix**: Set `HF_HUB_TRUST_REMOTE_CODE=1` and `TRUST_REMOTE_CODE=true` in wrapper

### Trap 6: Ghost `/home/mo/` Paths (The Symlink)
**Problem**: `install_link` is a symlink → Python resolves to `/home/mo/Desktop/install/`  
**Reality**: This is **NOT a bug**. The files physically live on the old drive. Python just shows the resolved real path in logs. Permissions work fine, migrations succeed.  
**Lesson**: Don't waste time trying to "fix" this — it's cosmetic.

---

## Final Working Config

### `~/.gemini/antigravity/mcp_config.json`
```json
{
  "mcpServers": {
    "cognee_mcp": {
      "command": ".../cognee-mcp/.venv/bin/python3",
      "args": [".../cognee-mcp/server_wrapper.py"],
      "cwd": ".../cognee-mcp",
      "env": {
        "PYTHONPATH": "...",
        "LLM_PROVIDER": "ollama",
        "LLM_MODEL": "llama3.2:latest",
        "LLM_ENDPOINT": "http://localhost:11434/v1",
        "LLM_API_KEY": "ollama",
        "EMBEDDING_PROVIDER": "ollama",
        "EMBEDDING_MODEL": "nomic-embed-text:latest",
        "GRAPH_DATABASE_PROVIDER": "neo4j",
        "GRAPH_DATABASE_URL": "bolt://localhost:7687",
        "GRAPH_DATABASE_USERNAME": "neo4j",
        "GRAPH_DATABASE_PASSWORD": "cognee_local_2026",
        "COGNEE_LOG_LEVEL": "CRITICAL",
        "ENABLE_BACKEND_ACCESS_CONTROL": "false"
      }
    }
  }
}
```
*(Full paths in the actual file at `~/.gemini/antigravity/mcp_config.json`)*

---

## Git History (GitHub backup)

**Repo**: `https://github.com/dfwconnect0-creator/cognee-mcp-server.git`
```
563b077 docs: updated session walkthrough with migration steps and rollback plan
697a92b feat: add missing cognee_search tool to MCP server
bcb28b8 feat: add prune_memory.py reset utility
042a896 fix: working ingest_rules.py with correct search API
f0a53a1 docs: add troubleshooting guide and rules, fix environment
af8e258 Initial commit
```

---

## Rollback Plan

If the official server fails after restart:
```bash
# 1. Edit MCP config to point back to custom server
# Change "args" to point to cognee_mcp_server.py
# Change "command" to old .venv Python
# Remove "cwd" and "env" (old server uses .env file directly)

# 2. Old server still works — tested and verified
```

---

## Next Steps After Restart

1. Restart Antigravity (close/reopen IDE)
2. Say "test" → verify MCP tools are connected
3. If working → move to ComfyUI pipeline setup
4. If not → rollback to custom server
