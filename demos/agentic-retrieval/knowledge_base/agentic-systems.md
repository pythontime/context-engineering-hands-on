---
id: agentic-systems
title: "Context Flow in Agentic Systems"
tags: [agents, tool-use, agent-loop, context-flow]
---

# Context Flow in Agentic Systems

An agentic system is one where an LLM operates in a loop — receiving input, deciding on actions (tool calls), observing results, and iterating until a task is complete. The critical difference from a simple chatbot is that **each iteration adds to the context window**, creating a growing record that the model must attend to on every subsequent call.

## The Agent Loop

The core pattern is:

1. User provides input → appended to `messages[]`
2. Model generates response → may include `tool_use` blocks
3. Tool results → appended as `tool_result` messages
4. Loop back to step 2 until model produces a final text response

Each cycle through this loop adds both the model's reasoning (assistant message) and tool outputs (user-role tool results) to the messages array. After 5 tool calls, the context might contain 10+ additional messages the user never explicitly wrote.

## Why Context Grows Fast

Consider a research agent that searches documents then synthesizes findings:
- **Turn 1**: User asks a question (50 tokens) → model calls `search` (20 tokens) → tool returns 3 results (600 tokens) → model synthesizes (200 tokens)
- **Turn 2**: Model calls `get_document` for more detail (20 tokens) → tool returns full doc (800 tokens) → model responds (300 tokens)

After just one user question, the messages array contains ~2,000 tokens of accumulated context. Multiply this by 10 questions in a session, and you approach 20,000 tokens — all being re-sent on every API call.

## Managing Agentic Context

Effective strategies include:
- **Scratchpads**: Let the agent write working notes that persist across turns
- **Context compression**: Summarize old turns to free token budget for new ones
- **Sub-agent isolation**: Delegate sub-tasks to fresh context windows
- **Selective retrieval**: Only pull documents relevant to the current question, not everything available

The key mental model: in an agent loop, the **messages array IS the context window**. Every append to that array directly affects cost, latency, and model attention.
