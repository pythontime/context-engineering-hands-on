"""
Tool definitions (Anthropic API format) and dispatch logic.

# ─── TEACHING MOMENT ───
# Tool definitions are part of the context sent on EVERY API call.
# These ~800 tokens of schema are "fixed overhead" — they consume
# budget whether the model uses the tools or not. In production,
# dynamic tool selection (loading only relevant tools per turn)
# can save thousands of tokens per call.
# ────────────────────────
"""

from __future__ import annotations

import json
from typing import Any

from retrieval import KnowledgeBase


def get_tool_definitions() -> list[dict]:
    """
    Return tool schemas in Anthropic API format.

    Three tools that give the agent retrieval capabilities:
    - search_documents: TF-IDF search over the knowledge base
    - get_document: fetch full content of a specific document
    - list_documents: browse all available documents
    """
    return [
        {
            "name": "search_documents",
            "description": (
                "Search the knowledge base for documents relevant to a query. "
                "Returns ranked results with relevance scores and snippets. "
                "Use this when you need to find information about a topic."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query — use specific keywords for better results",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 3)",
                        "default": 3,
                    },
                },
                "required": ["query"],
            },
        },
        {
            "name": "get_document",
            "description": (
                "Retrieve the full content of a specific document by its ID. "
                "Use this after searching to get complete details on a topic. "
                "The full document content will be added to context."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "The document ID (e.g., 'context-windows', 'rag-patterns')",
                    },
                },
                "required": ["doc_id"],
            },
        },
        {
            "name": "list_documents",
            "description": (
                "List all documents available in the knowledge base. "
                "Returns document IDs, titles, tags, and estimated token counts. "
                "Use this to discover what information is available."
            ),
            "input_schema": {
                "type": "object",
                "properties": {},
            },
        },
    ]


def execute_tool(name: str, tool_input: dict[str, Any], kb: KnowledgeBase) -> str:
    """
    Execute a tool call and return the result as a string.

    # ─── TEACHING MOMENT ───
    # The string returned here becomes a tool_result message in the
    # context window. Every character counts toward the token budget.
    # Notice how we format results to be informative but concise —
    # this is the "selecting context" lever in action.
    # ────────────────────────
    """
    if name == "search_documents":
        query = tool_input["query"]
        top_k = tool_input.get("top_k", 3)
        results = kb.search(query, top_k=top_k)
        if not results:
            return f"No documents found matching '{query}'."
        formatted = []
        for r in results:
            formatted.append(
                f"- [{r.document.id}] {r.document.title} "
                f"(score: {r.score:.2f}, ~{r.document.token_estimate} tokens)\n"
                f"  {r.snippet}"
            )
        return f"Found {len(results)} result(s) for '{query}':\n\n" + "\n\n".join(formatted)

    elif name == "get_document":
        doc_id = tool_input["doc_id"]
        doc = kb.get_document(doc_id)
        if doc is None:
            available = ", ".join(kb.documents.keys())
            return f"Document '{doc_id}' not found. Available: {available}"
        return (
            f"# {doc.title}\n"
            f"Tags: {', '.join(doc.tags)}\n"
            f"Estimated tokens: ~{doc.token_estimate}\n\n"
            f"{doc.content}"
        )

    elif name == "list_documents":
        docs = kb.list_documents()
        lines = [f"Knowledge base contains {len(docs)} document(s):\n"]
        for d in docs:
            lines.append(
                f"- **{d['id']}**: {d['title']} "
                f"(tags: {', '.join(d['tags'])}, ~{d['token_estimate']} tokens)"
            )
        return "\n".join(lines)

    else:
        return json.dumps({"error": f"Unknown tool: {name}"})
