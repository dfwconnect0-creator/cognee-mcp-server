# Cognee MCP Setup: Troubleshooting Guide

**Project**: OpenClaw MVP Autonomous Video Pipeline  
**Date**: March 14, 2026  
**Environment**: Ubuntu 24.04, RTX 3060 Ti (8GB VRAM)

This guide documents the errors encountered during the initial setup of the Cognee MCP Server, their root causes, and the exact solutions applied. This serves as a reference for future setups or if the system needs to be rebuilt.

## 1. Python Environment Breakage
**Symptoms:** 
- `ModuleNotFoundError: No module named 'pydantic'`
- Terminal displaying broken shell formatting like `^[[200~`
- Python commands linking to missing `python3.10` binaries.

**Root Cause:**
The original `.venv` directory was copied from an older Ubuntu installation running Python 3.10, while the new Ubuntu 24.04 system uses Python 3.12.3. The symlinks inside `.venv/bin/` were pointing to non-existent binaries.

**Solution:**
Recreated the virtual environment natively on the new system.
```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
uv pip install cognee python-dotenv mcp[cli] pydantic transformers neo4j
```

## 2. Missing `transformers` Library
**Symptoms:**
- `ModuleNotFoundError: No module named 'transformers'` during tokenization operations inside Cognee.

**Root Cause:**
Cognee relies on the HuggingFace `transformers` library for text chunking and tokenization, but it was not explicitly listed in the base dependency tree of the recovered environment.

**Solution:**
Installed the package using `uv`.
```bash
uv pip install transformers
```

## 3. Ollama LLM Connection Timeout (InstructorRetryException)
**Symptoms:**
- `cognee.infrastructure.llm.utils` raising `InstructorRetryException`.
- Repeated 500/404 errors when connecting to `http://localhost:11434/v1`.

**Root Cause:**
The `.env` file specified `LLM_MODEL="qwen2.5:7b"`. Because the system was recently wiped and Ollama was moved/reinstalled, the 4.7GB `qwen2.5` model did not exist in the local SSD or the backup Archive drive.

**Solution:**
Switched the local configuration to use a model that was already installed (`llama3.2:latest`) to save bandwidth and time.
1. Edited `.env` to set `LLM_MODEL="llama3.2:latest"`.
2. Verified the model existed by running `ollama list`.

## 4. Vector Embeddings Timeout
**Symptoms:**
- `Ollama embedding error: model "nomic-embed-text:latest" not found, try pulling it first`
- `Embedding connection test timed out after 30s.`

**Root Cause:**
While Llama 3.2 was processing the general text generation, Cognee requires a separate, lightweight embedding model to convert text phrases into mathematical vectors to insert into LanceDB. The default model `nomic-embed-text` was not installed.

**Solution:**
Pulled the embedding model via Ollama. It is very small (~274MB) and downloads quickly.
```bash
ollama pull nomic-embed-text
```

## 5. Neo4j Graph Database APOC Plugin Missing (Current Blocker)
**Symptoms:**
- `neo4j.exceptions.ClientError: {message: There is no procedure with the name apoc.create.addLabels registered for this database instance.}`

**Root Cause:**
Neo4j requires the "Awesome Procedures On Cypher" (APOC) plugin for Cognee to execute advanced graph creation operations. The default `docker run neo4j` command does not activate this plugin by default.

**Solution:**
Stop the current container, destroy it, and launch a new one with the `NEO4J_PLUGINS='["apoc"]'` environment variable active.

```bash
sudo docker stop neo4j
sudo docker rm neo4j
sudo docker run \
    --name neo4j \
    --restart always \
    --publish=7474:7474 --publish=7687:7687 \
    --env NEO4J_AUTH=neo4j/cognee_local_2026 \
    --env NEO4J_PLUGINS='["apoc"]' \
    -d neo4j:latest
```
