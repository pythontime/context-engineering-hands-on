---
id: prompt-vs-context-eng
title: "Prompt Engineering vs Context Engineering"
tags: [prompt-engineering, context-engineering, comparison]
---

# Prompt Engineering vs Context Engineering

Prompt engineering focuses on crafting the right instruction text to elicit desired model behavior. Context engineering is the broader discipline of designing, managing, and optimizing **everything** that flows into the model's context window — not just the prompt, but also system instructions, retrieved documents, tool definitions, conversation history, and structured metadata.

## The Shift in Thinking

As Andrej Karpathy noted: "I would like to mass rename 'prompt engineering' to 'context engineering' because the art/science isn't just about the prompt (instruction to the LLM) but about filling in the context window."

The key insight is that a prompt is one **slice** of the context, while context engineering manages the **entire window** as a system.

## What Context Engineering Adds

| Dimension | Prompt Engineering | Context Engineering |
|-----------|-------------------|-------------------|
| Scope | Single instruction | Entire context window |
| Concern | What to say | What to include, exclude, and when |
| Time horizon | Single turn | Multi-turn, multi-agent |
| Optimization | Phrasing & structure | Token budget, retrieval, compression |
| Audience | One model call | Agent loops, tool chains, pipelines |

## Why This Matters for Agents

In a simple chatbot, prompt engineering might suffice — you write a system prompt and the user provides input. But in an agentic system where the model makes multiple tool calls across many turns, the context window fills up with tool results, intermediate reasoning, and accumulated history. Without deliberate context engineering, the agent degrades: it forgets early instructions, gets distracted by irrelevant tool results, or exhausts its token budget.

## The Three Pillars

Context engineering rests on three pillars:
1. **Provide enough context** — the model has what it needs to act correctly
2. **Avoid too much context** — irrelevant information doesn't dilute attention
3. **Present context effectively** — structure and placement optimize model performance
