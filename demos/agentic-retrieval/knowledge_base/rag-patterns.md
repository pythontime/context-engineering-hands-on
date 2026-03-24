---
id: rag-patterns
title: "RAG Patterns and Context Selection"
tags: [rag, retrieval, selection, vector-search]
---

# RAG Patterns and Context Selection

Retrieval-Augmented Generation (RAG) is the most common pattern for dynamically selecting context at inference time. Instead of stuffing all knowledge into the prompt or fine-tuning the model, RAG retrieves relevant documents from an external store and injects them into the context window just before the model generates a response.

## Basic RAG Pipeline

1. **Index**: Chunk documents, compute embeddings, store in vector database
2. **Retrieve**: Given a query, find the top-K most similar chunks
3. **Augment**: Insert retrieved chunks into the system or user message
4. **Generate**: Model produces a response grounded in the retrieved context

## RAG as Context Engineering

From a context engineering perspective, RAG is fundamentally a **selection** operation — deciding which documents enter the context window. The quality of this selection directly determines output quality:

- **Too few results**: Model lacks sufficient information and hallucinates
- **Too many results**: Context becomes noisy, diluting the model's attention
- **Wrong results**: Model is confidently wrong, grounded in irrelevant context

## Agentic RAG vs Traditional RAG

In traditional RAG, retrieval happens once before generation. In **agentic RAG**, the model itself decides when and what to retrieve by calling search tools:

| Aspect | Traditional RAG | Agentic RAG |
|--------|----------------|-------------|
| Who retrieves | Application code | The model via tool calls |
| When | Before generation | Any time during generation |
| How many times | Once | As many times as needed |
| Query crafting | User's raw query | Model reformulates queries |

Agentic RAG is more powerful because the model can iteratively refine its searches, drill down into specific documents, and decide when it has enough context to answer.

## Practical Considerations

- **Chunk size**: 200–500 tokens per chunk balances precision and context
- **Top-K selection**: Start with K=3–5 and tune based on answer quality
- **Re-ranking**: Use a cross-encoder to re-score initial retrieval results
- **Citation**: Include document IDs so answers can reference their sources
