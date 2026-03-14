# Session Walkthrough — March 14, 2026

**Time**: 11:00 AM → 3:34 PM (4.5 hours)  
**Goal**: Set up Cognee MCP Server for OpenClaw MVP  
**Deadline**: March 15, 2026  
**Result**: ✅ Cognee is fully operational

---

## What We Built

A local, fully offline AI knowledge graph powered by:
- **Neo4j** (graph database, Docker, APOC plugin enabled)
- **LanceDB** (vector embeddings, file-based)
- **Ollama** (llama3.2 for LLM, nomic-embed-text for embeddings)
- **Cognee 0.5.4** (Python SDK orchestrating all of the above)

Antigravity is configured to connect to this as an MCP server on next restart.

---

## Git History (All Pushed to GitHub)

**Repo**: `https://github.com/dfwconnect0-creator/cognee-mcp-server.git`

```
bcb28b8 feat: add prune_memory.py reset utility
042a896 fix: working ingest_rules.py with correct search API
f0a53a1 docs: add troubleshooting guide and rules, fix environment
af8e258 Initial commit: last working cognee MCP server (pre-reinstall)
```

---

## Files in the Repository

| File | Purpose |
|------|---------|
| `cognee_mcp_server.py` | The MCP server (419 lines). Antigravity launches this as a subprocess. |
| `ingest_rules.py` | Ingests `global_rules.md` into Neo4j + LanceDB. **Tested & working.** |
| `prune_memory.py` | One-command memory reset utility. |
| `global_rules.md` | Your system rules (hardware, forbidden actions, project context). |
| `troubleshooting_guide.md` | Documents every error we hit and how we fixed it. |
| `.env` | Local config (Ollama endpoints, Neo4j password). **Not in git.** |
| `.env.example` | Sanitized template of `.env`. **In git.** |
| `.gitignore` | Ignores `.venv/`, `.env`, `__pycache__/`. |

---

## Errors We Fixed (in order)

1. **Broken `.venv`** → Python 3.10 symlinks on a Python 3.12 system → recreated venv
2. **Missing `transformers`** → `uv pip install transformers`
3. **Missing `qwen2.5:7b`** → Switched to `llama3.2:latest` (already installed)
4. **Missing `nomic-embed-text`** → `ollama pull nomic-embed-text`
5. **Missing `neo4j` package** → `pip install neo4j`
6. **Neo4j APOC not installed** → Recreated Docker container with `NEO4J_PLUGINS='["apoc"]'`
7. **Wrong `cognee.search()` API** → Fixed to use `query_text=` and `query_type=SearchType.SUMMARIES`

---

## Key Configs

### Antigravity MCP Config (`~/.gemini/antigravity/mcp_config.json`)
```json
{
  "mcpServers": {
    "cognee_mcp": {
      "command": "/home/bladina/Desktop/install_link/cognee/.venv/bin/python3",
      "args": ["/home/bladina/Desktop/install_link/cognee/cognee_mcp_server.py"],
      "env": {},
      "disabled": false
    }
  }
}
```

### Antigravity Rules (`~/.config/antigravity/rules.md`)
81 lines of hardware specs, forbidden actions, required actions, model search paths. **Already active and working.**

### Neo4j Docker Container
```bash
sudo docker run \
    --name neo4j --restart always \
    --publish=7474:7474 --publish=7687:7687 \
    --env NEO4J_AUTH=neo4j/cognee_local_2026 \
    --env NEO4J_PLUGINS='["apoc"]' \
    -d neo4j:latest
```

---

## Test Results (All Passing)

```
TEST 1: What GPU does the system have?        ✅
TEST 2: What actions are forbidden?           ✅
TEST 3: What is the current project?          ✅
```

---

## What To Do After Restart

1. **Restart Antigravity** (close and reopen the IDE)
2. **Test MCP connection**: Ask Antigravity *"Search Cognee for my hardware rules"*
3. If MCP works → **Move to ComfyUI setup**
4. If MCP fails → Check that Neo4j Docker is running: `sudo docker ps`

### Quick Commands Reference
```bash
# Check Neo4j is running
sudo docker ps | grep neo4j

# Re-ingest rules (if needed)
cd ~/Desktop/install_link/cognee && source .venv/bin/activate && python3 ingest_rules.py

# Reset memory (if pipeline goes bad)
cd ~/Desktop/install_link/cognee && source .venv/bin/activate && python3 prune_memory.py

# Check Ollama models
ollama list
```
