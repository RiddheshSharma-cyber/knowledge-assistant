\# AI-Powered Knowledge Assistant (Version 1)



A grounded, document-based Question-Answering (QA) application using Retrieval-Augmented Generation (RAG).



\## 📌 Project Overview

This project is an end-to-end RAG system designed to extract, index, and query information from uploaded PDF documents with strict grounding and verifiable citations.



\### Key Goals (Version 1)

\- Deep-dive implementation of RAG mechanics without heavy agentic frameworks.

\- Configurable text chunking and metadata tracking.

\- Local vector embeddings generation.

\- Grounded prompt construction to prevent hallucinations.

\- Structured, traceable page-level source citations.



\---



\## 🏗️ System Architecture \& Data Flow



```text

\[ User Question ]

&#x20;      │

&#x20;      ▼

\[ Query Vectorizer ] ──► \[ ChromaDB Similarity Search ]

&#x20;                                  │

&#x20;                                  ▼

&#x20;                       \[ Relevant Chunks + Metadata ]

&#x20;                                  │

&#x20;                                  ▼

&#x20;                       \[ Strict Grounding Prompt ] ──► \[ LLM Provider ]

&#x20;                                                             │

&#x20;                                                             ▼

&#x20;                       \[ Answer + Page Citations ] ◄─────────┘

