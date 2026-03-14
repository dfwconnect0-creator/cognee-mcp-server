#!/usr/bin/env python3
"""
MCP Server for Cognee — Local AI Knowledge Graph Memory.

This server wraps the Cognee v0.5.3 Python API, providing persistent
AI memory tools for the Antigravity IDE. Uses local Ollama LLM, Neo4j
graph database, and LanceDB vectors — fully offline, no cloud APIs.

Transport: stdio (launched as subprocess by the IDE)
"""

import json
import logging
import os
import sys
from enum import Enum
from typing import Any, Dict, List, Optional

# Load .env before importing cognee so config is picked up
from dotenv import load_dotenv

_ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(_ENV_PATH)

import cognee
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CHARACTER_LIMIT = 25000  # Maximum response size in characters
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("cognee_mcp")

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
mcp = FastMCP("cognee_mcp")

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"


# ---------------------------------------------------------------------------
# Pydantic v2 Input Models
# ---------------------------------------------------------------------------

class CogneeAddInput(BaseModel):
    """Input for ingesting text into the Cognee knowledge store."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    text: str = Field(
        ...,
        description=(
            "The text to ingest into Cognee's knowledge store. "
            "Can be facts, documentation, conversation summaries, or any "
            "knowledge you want the system to remember. "
            "(e.g., 'The server runs Ubuntu 22.04 with an RTX 3060 Ti')"
        ),
        min_length=1,
        max_length=50000,
    )

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only.")
        return v.strip()


class CogneeSearchInput(BaseModel):
    """Input for searching the Cognee knowledge graph."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    query: str = Field(
        ...,
        description=(
            "Natural-language search query over the knowledge graph. "
            "(e.g., 'What GPU does the system have?', 'List installed software')"
        ),
        min_length=1,
        max_length=1000,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable, 'json' for machine-readable.",
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be empty or whitespace only.")
        return v.strip()


class CogneePruneInput(BaseModel):
    """Input for resetting Cognee data and/or system metadata."""
    model_config = ConfigDict(extra="forbid")

    prune_data: bool = Field(
        default=True,
        description="If true, clears all ingested data and knowledge graph content.",
    )
    prune_system: bool = Field(
        default=False,
        description=(
            "If true, also clears system metadata (SQLite tables, vector indices). "
            "Use with caution — this is a full factory reset."
        ),
    )


# ---------------------------------------------------------------------------
# Shared Utilities
# ---------------------------------------------------------------------------

def _handle_cognee_error(e: Exception) -> str:
    """Consistent, actionable error formatting for all Cognee tools.

    Returns a human-readable error string that guides the agent toward
    resolution rather than just reporting the exception.
    """
    error_type = type(e).__name__

    if "ModuleNotFoundError" in error_type:
        return (
            f"Error: Missing Python module — {e}. "
            "Try installing it with: uv pip install <module-name>"
        )
    if "ConnectionRefusedError" in error_type or "ConnectionError" in error_type:
        return (
            "Error: Cannot connect to a backend service. "
            "Check that Ollama is running (systemctl status ollama) "
            "and Neo4j is up (docker ps | grep neo4j)."
        )
    if "TimeoutError" in error_type:
        return (
            "Error: Operation timed out. The LLM or database may be overloaded. "
            "Check GPU memory usage (nvidia-smi) and try again."
        )
    if "InstructorRetryException" in error_type:
        return (
            "Error: The LLM failed to produce valid structured output after retries. "
            "This is the 'schema echo' bug with some Ollama models. "
            "Check that LLM_MODEL in .env is set to qwen2.5:7b (not llama3.1). "
            "Then run cognee_prune and re-ingest data."
        )
    return f"Error: {error_type} — {e}"


def _truncate_response(result: str) -> str:
    """Truncate response if it exceeds CHARACTER_LIMIT."""
    if len(result) > CHARACTER_LIMIT:
        truncated = result[:CHARACTER_LIMIT]
        truncated += (
            f"\n\n--- Response truncated at {CHARACTER_LIMIT} characters. "
            "Use a more specific query or filter to reduce results. ---"
        )
        return truncated
    return result


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool(
    name="cognee_add",
    annotations={
        "title": "Add Knowledge to Cognee",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def cognee_add(params: CogneeAddInput) -> str:
    """Ingest text into Cognee's persistent knowledge store.

    Stores the provided text so it can later be processed into a knowledge
    graph (via cognee_cognify) and searched (via cognee_search). Use this
    to remember facts, documentation, hardware specs, user preferences,
    or conversation summaries.

    After adding text you MUST call cognee_cognify to build/update the
    knowledge graph before the data becomes searchable.

    Args:
        params (CogneeAddInput): Validated input containing:
            - text (str): The knowledge text to ingest (1–50,000 chars)

    Returns:
        str: JSON confirmation with status and character count.

        Success: {"status": "ok", "message": "Added 142 chars to knowledge store."}
        Error:   "Error: <actionable description>"

    Examples:
        - Use when: "Remember that we use uv instead of pip" → text="User preference: always use uv as package manager, pip only as fallback."
        - Use when: "Store our hardware specs" → text="Ubuntu 22.04, Ryzen 9 5900X, RTX 3060 Ti 8GB, 32GB RAM."
        - Don't use when: You want to search existing knowledge → use cognee_search instead.
        - Don't use when: Data is already ingested and you want to rebuild the graph → use cognee_cognify.

    Error Handling:
        - Empty/whitespace text is rejected by input validation.
        - Connection errors suggest checking Ollama and Neo4j services.
    """
    try:
        await cognee.add(params.text)
        return json.dumps({
            "status": "ok",
            "message": f"Added {len(params.text)} chars to knowledge store. "
                       "Run cognee_cognify to make it searchable.",
        })
    except Exception as e:
        return _handle_cognee_error(e)


@mcp.tool(
    name="cognee_cognify",
    annotations={
        "title": "Build Knowledge Graph",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def cognee_cognify() -> str:
    """Build or rebuild the Cognee knowledge graph from all ingested data.

    Processes all text added via cognee_add through the Cognee pipeline:
    entity extraction → relationship mapping → knowledge graph construction.
    This step uses the configured LLM (Ollama/qwen2.5:7b) and writes
    to Neo4j (graph) and LanceDB (vectors).

    This operation can take 30–120 seconds depending on data volume and
    GPU availability. It is idempotent — running it twice produces the
    same graph.

    Args:
        None

    Returns:
        str: JSON confirmation with status.

        Success: {"status": "ok", "message": "Knowledge graph built successfully."}
        Error:   "Error: <actionable description>"

    Examples:
        - Use when: After calling cognee_add with new data.
        - Use when: After pruning and re-adding data.
        - Don't use when: No new data has been added since last cognify.
        - Don't use when: You just want to search → use cognee_search.

    Error Handling:
        - LLM connection errors suggest checking Ollama status.
        - InstructorRetryException means the LLM model can't produce structured output.
        - Timeout errors may indicate GPU memory pressure.
    """
    try:
        await cognee.cognify()
        return json.dumps({
            "status": "ok",
            "message": "Knowledge graph built successfully.",
        })
    except Exception as e:
        return _handle_cognee_error(e)





@mcp.tool(
    name="cognee_status",
    annotations={
        "title": "Check Cognee Status",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def cognee_status() -> str:
    """Check Cognee system status, configuration, and service connectivity.

    Returns the current Cognee configuration including LLM model, embedding
    model, database providers, and version info. Useful for debugging or
    confirming the system is correctly configured.

    Args:
        None

    Returns:
        str: JSON object with system configuration details.

        Success:
        {
            "status": "ok",
            "info": {
                "cognee_version": "0.5.3",
                "llm_provider": "ollama",
                "llm_model": "qwen2.5:7b",
                "embedding_model": "nomic-embed-text:latest",
                "graph_db": "neo4j",
                "vector_db": "lancedb",
                "relational_db": "sqlite",
                "env_file": "/path/to/.env"
            }
        }

    Examples:
        - Use when: "Is Cognee configured correctly?" → run cognee_status
        - Use when: Debugging search failures → check llm_model value
        - Don't use when: You want to search knowledge → use cognee_search

    Error Handling:
        - Should rarely fail since it only reads environment variables.
    """
    try:
        info: Dict[str, Any] = {
            "cognee_version": getattr(cognee, "__version__", "unknown"),
            "llm_provider": os.getenv("LLM_PROVIDER", "not set"),
            "llm_model": os.getenv("LLM_MODEL", "not set"),
            "llm_endpoint": os.getenv("LLM_ENDPOINT", "not set"),
            "embedding_model": os.getenv("EMBEDDING_MODEL", "not set"),
            "graph_db_provider": os.getenv("GRAPH_DATABASE_PROVIDER", "not set"),
            "graph_db_url": os.getenv("GRAPH_DATABASE_URL", "not set"),
            "vector_db": os.getenv("VECTOR_DB_PROVIDER", "not set"),
            "relational_db": os.getenv("DB_PROVIDER", "not set"),
            "env_file": _ENV_PATH,
        }
        return json.dumps({"status": "ok", "info": info}, indent=2)
    except Exception as e:
        return _handle_cognee_error(e)


@mcp.tool(
    name="cognee_prune",
    annotations={
        "title": "Reset Cognee Data",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def cognee_prune(params: CogneePruneInput) -> str:
    """Reset Cognee data and optionally system metadata.

    Clears ingested data (knowledge graph nodes, edges, vectors) and
    optionally resets system metadata (SQLite tables). Use this before
    re-ingesting fresh data or to start from a clean slate.

    WARNING: This is destructive. Pruned data cannot be recovered.

    Args:
        params (CogneePruneInput): Validated input containing:
            - prune_data (bool): Clear ingested data and graph (default: true)
            - prune_system (bool): Also clear metadata — full factory reset (default: false)

    Returns:
        str: JSON confirmation listing what was pruned.

        Success: {"status": "ok", "message": "Data pruned. System metadata pruned."}
        Error:   "Error: <actionable description>"

    Examples:
        - Use when: "Start fresh with clean data" → prune_data=true
        - Use when: "Full factory reset" → prune_data=true, prune_system=true
        - Don't use when: You just want to add more data → use cognee_add (data is additive)
        - Don't use when: You want to search → use cognee_search

    Error Handling:
        - Database connection errors suggest checking Neo4j status.
    """
    try:
        msgs: List[str] = []
        if params.prune_data:
            await cognee.prune.prune_data()
            msgs.append("Data pruned.")
        if params.prune_system:
            await cognee.prune.prune_system(metadata=True)
            msgs.append("System metadata pruned.")
        if not msgs:
            return json.dumps({
                "status": "ok",
                "message": "Nothing pruned — both prune_data and prune_system were false.",
            })
        return json.dumps({"status": "ok", "message": " ".join(msgs)})
    except Exception as e:
        return _handle_cognee_error(e)


# ---------------------------------------------------------------------------
# Entry point — stdio transport (default)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run()
