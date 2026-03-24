---
id: context-failures
title: "Context Failure Modes in LLM Applications"
tags: [failures, debugging, poisoning, distraction]
---

# Context Failure Modes in LLM Applications

When LLM applications fail, the root cause is often not the model itself but the context it was given. Drew Breunig's taxonomy identifies four primary failure modes, all traceable to context engineering problems.

## The Four Failure Modes

### 1. Context Poisoning
Bad or contradictory information enters the context window and corrupts the model's output. This often happens when:
- Retrieved documents contain outdated information
- User-provided content includes adversarial instructions (prompt injection)
- Tool results return error messages that the model treats as facts

**Fix**: Validate and sanitize all context before it enters the window. Use the **write** and **select** levers — curate what goes in.

### 2. Context Distraction
Too much irrelevant information overwhelms the model's attention, causing it to lose track of the actual question. Symptoms include:
- Answers that address retrieved documents instead of the user's question
- Verbose responses that wander off-topic
- The "Lost in the Middle" effect at scale

**Fix**: Reduce noise through the **select** and **compress** levers — retrieve fewer, more relevant documents and summarize verbose content.

### 3. Context Confusion
The model receives ambiguous or poorly structured context and misinterprets it. Common causes:
- Mixing instructions from multiple sources without clear boundaries
- Inconsistent formatting between system prompt and tool results
- Missing metadata that would help the model understand document context

**Fix**: Improve context structure using the **write** lever — add clear delimiters, labels, and formatting conventions.

### 4. Context Clash
Different parts of the context contain conflicting instructions or information. The model must choose between them, often unpredictably. Examples:
- System prompt says "be concise" but retrieved docs are verbose
- Two tools return contradictory information about the same topic
- User instruction conflicts with system-level safety guidelines

**Fix**: Resolve conflicts through the **write** and **isolate** levers — establish clear priority rules and separate conflicting contexts into different windows.

## The Diagnosis Workflow

When output quality degrades: (1) identify the failure mode, (2) trace it to the context source, (3) apply the appropriate lever (write/select/compress/isolate).
