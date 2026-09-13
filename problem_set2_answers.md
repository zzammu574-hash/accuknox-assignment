# Problem Set 2 — Conceptual Answers
### AccuKnox AI/ML Internship Assignment

---

## Q1. Self-Rating on LLM, Deep Learning, AI, ML

| Domain | Rating | Justification |
|---|---|---|
| **LLM** | B | I can work with LLM APIs (OpenAI, Hugging Face), build prompt pipelines, implement RAG patterns, and fine-tune smaller models with supervision. I understand transformer internals at a conceptual level but have not yet trained a large model from scratch independently. |
| **Deep Learning** | B | I can design, train, and debug CNNs, RNNs, and transformer-based architectures using PyTorch/Keras under guidance. I understand backpropagation, regularisation, and common training pathologies (vanishing gradients, overfitting). |
| **AI (General)** | B | I have hands-on experience with search algorithms, planning, and classical AI methods, and can reason about AI system design independently; more complex multi-agent or symbolic reasoning systems would benefit from senior oversight. |
| **ML** | A | I can independently implement and tune supervised/unsupervised ML pipelines end-to-end: feature engineering, model selection, cross-validation, evaluation, and deployment using scikit-learn and related libraries. |

---

## Q2. Key Architectural Components of an LLM-Based Chatbot

### High-Level Overview

An LLM-based chatbot is not just a model — it is a **multi-layer system** that connects user input to intelligent responses through several cooperating components. The diagram below shows the logical flow:

```
User Input
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                      CHATBOT SYSTEM                         │
│                                                             │
│  ┌──────────────┐    ┌──────────────────┐                  │
│  │   Frontend   │───▶│  API / Gateway   │                  │
│  │  (UI/CLI)    │◀───│  (Auth, Rate-    │                  │
│  └──────────────┘    │   limiting)      │                  │
│                      └────────┬─────────┘                  │
│                               │                             │
│                      ┌────────▼─────────┐                  │
│                      │  Orchestration   │                  │
│                      │  Layer           │                  │
│                      │  (LangChain /    │                  │
│                      │   LlamaIndex /   │                  │
│                      │   custom)        │                  │
│                      └──┬──────┬────────┘                  │
│                         │      │                            │
│              ┌──────────▼──┐ ┌─▼──────────────┐           │
│              │  Memory /   │ │  Retrieval      │           │
│              │  Context    │ │  (RAG Pipeline) │           │
│              │  Manager    │ │  Vector DB      │           │
│              └─────────────┘ └─────────────────┘           │
│                         │                                   │
│                      ┌──▼──────────────┐                   │
│                      │   LLM Core      │                   │
│                      │  (GPT-4 /       │                   │
│                      │   Claude /      │                   │
│                      │   Llama 3)      │                   │
│                      └──┬──────────────┘                   │
│                         │                                   │
│              ┌──────────▼──────────────┐                   │
│              │  Post-processing        │                   │
│              │  (safety filter,        │                   │
│              │   formatting,           │                   │
│              │   structured output)    │                   │
│              └─────────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
Response to User
```

---

### Component Breakdown

#### 1. Frontend / Interface Layer
The entry point for the user. Can be a web UI (React/Streamlit), mobile app, CLI, or API endpoint. Responsible for capturing input, rendering markdown/code, and managing conversation UX (streaming tokens, typing indicators).

#### 2. API Gateway
Handles authentication (API keys, OAuth), rate-limiting, request logging, and routing. In production this is critical to prevent abuse and track usage per tenant. Tools: Kong, AWS API Gateway, or a simple FastAPI middleware layer.

#### 3. Orchestration Layer
The "brain" that decides what happens with each user message. It:
- Builds the **prompt** from system instructions + conversation history + retrieved context
- Decides whether to call external **tools** (search, calculator, database lookup)
- Manages **multi-step reasoning** chains (e.g., ReAct: Reason → Act → Observe → Repeat)

Frameworks: LangChain, LlamaIndex, or a custom state machine. This layer is what separates a simple API wrapper from a real chatbot product.

#### 4. Memory / Context Manager
LLMs are stateless — they have no memory across turns by default. The context manager solves this:

| Memory Type | How It Works | Use Case |
|---|---|---|
| **Buffer memory** | Appends every turn to the prompt | Short conversations |
| **Sliding window** | Keeps only the last N turns | Token budget management |
| **Summary memory** | Summarises older turns with the LLM | Long sessions |
| **Entity memory** | Tracks named entities (people, dates) | Personalised assistants |
| **External (vector)** | Stores embeddings of past turns in a DB | Long-term user memory |

#### 5. Retrieval-Augmented Generation (RAG) Pipeline
When the chatbot needs to answer questions about private or up-to-date data (company docs, PDFs, knowledge bases), RAG allows it to **retrieve relevant chunks** before generating:

```
User Query
    │
    ▼
Embed query ──▶ Vector DB similarity search ──▶ Top-k chunks
                                                     │
                                                     ▼
                                          Inject into prompt context
                                                     │
                                                     ▼
                                               LLM generates answer
                                           grounded in retrieved chunks
```

This is the most important technique for making LLM chatbots factually reliable on domain-specific knowledge.

#### 6. LLM Core
The generative model itself. Can be:
- **Proprietary API**: OpenAI GPT-4o, Anthropic Claude, Google Gemini — easy, powerful, costly
- **Open-source self-hosted**: Llama 3, Mistral, Phi-3 — private, customisable, requires infra

The LLM receives the fully assembled prompt and returns a completion. Temperature, top-p, and max tokens are tuned here to control creativity vs. determinism.

#### 7. Tool / Function Calling Layer
Modern LLMs (GPT-4, Llama 3.1) can emit structured JSON calls to invoke external tools — web search, SQL queries, REST APIs, calculators. The orchestration layer executes these calls and feeds results back into the next LLM turn. This is the foundation of **agentic** chatbots.

#### 8. Post-processing Layer
Before the response reaches the user:
- **Safety filters**: block harmful or off-policy content (OpenAI Moderation API, custom classifiers)
- **Output formatting**: parse structured output (JSON mode), render tables/code blocks
- **Guardrails**: validate that the response stays on topic (e.g., NeMo Guardrails)

#### 9. Observability & Logging
Crucial for production systems: log every prompt-response pair, track latency, token usage, user feedback (thumbs up/down), and failure modes. Tools: LangSmith, Helicone, custom ELK stack.

---

## Q3. Vector Databases — Explanation, Problem Definition, and Selection

### What is a Vector Database?

Traditional databases store and query data by **exact or pattern-matched values** (WHERE name = 'Alice'). This breaks down for AI applications where the query is conceptual rather than literal — "find documents similar in meaning to this question."

A **vector database** stores data as high-dimensional numerical vectors (embeddings) and retrieves records by **similarity** rather than exact match. An embedding model (e.g., `text-embedding-3-small`, `sentence-transformers`) converts text, images, or audio into a dense vector of 384–3072 floating-point numbers. Semantically similar items cluster close together in this vector space.

```
Text: "How do I reset my password?"
         │
         ▼  Embedding Model
Vector: [0.021, -0.143, 0.876, ..., 0.034]  ← 1536 dimensions

Similarity search finds nearest vectors:
  → "Steps to change account password"  (cosine sim: 0.97) ✓
  → "Forgot login credentials help"     (cosine sim: 0.91) ✓
  → "DELETE FROM users WHERE id=1"      (cosine sim: 0.12) ✗
```

**Approximate Nearest Neighbour (ANN)** algorithms (HNSW, IVF, PQ) make this search fast even across millions of vectors, trading a tiny accuracy loss for orders-of-magnitude speed gains.

---

### Key Capabilities of a Vector Database

| Feature | Description |
|---|---|
| **Vector indexing** | HNSW, IVF-Flat, IVF-PQ — trades recall for speed |
| **Metadata filtering** | Pre/post-filter by scalar fields alongside the vector search |
| **Hybrid search** | Combine dense vector search with keyword (BM25) search |
| **Multi-tenancy** | Namespace isolation per user or organisation |
| **CRUD on vectors** | Update and delete embeddings without full re-indexing |
| **Scalability** | Horizontal sharding for billion-scale vector collections |

---

### The Hypothetical Problem

**Domain**: Customer Support Automation for a SaaS product (e.g., a cloud security platform like AccuKnox).

**Problem**: The support team has 50,000+ historical support tickets, 300 documentation articles, and 1,200 FAQ entries. When a new customer submits a support ticket, agents spend 8–12 minutes searching for relevant prior resolutions. The goal is to build a **semantic search + RAG chatbot** that instantly surfaces the top 5 most relevant prior answers and drafts a suggested reply.

**Requirements**:
- Dataset: ~50,000 documents, each embedded to 1536-dim vectors
- Latency: < 100 ms per query at peak load (200 concurrent users)
- Metadata filtering: filter by product version, issue category, resolution status
- Hybrid search: combine semantic similarity with keyword matching on ticket IDs and error codes
- Deployment: on-premises or private cloud (data privacy — customer PII in tickets)
- Team size: 2–3 engineers; needs good Python SDK and clear documentation

---

### Vector Database Comparison

| Database | Type | Strengths | Weaknesses |
|---|---|---|---|
| **Pinecone** | Managed cloud | Easiest setup, great scaling, hybrid search | Proprietary, data leaves your infra, costly at scale |
| **Weaviate** | OSS / managed | Hybrid search (BM25 + vector), GraphQL API, modular | More complex ops, heavier resource use |
| **Qdrant** | OSS / managed | Fastest ANN benchmarks, rich filtering, Rust core, great Python SDK | Smaller community than Chroma |
| **Chroma** | OSS embedded | Simplest to get started, great for prototyping | Not production-ready at large scale |
| **Milvus** | OSS / managed | Billion-scale, enterprise-grade, GPU acceleration | Operationally complex (Kubernetes-native) |
| **pgvector** | PostgreSQL extension | No new infra if already on Postgres, SQL familiarity | Slower ANN at large scale, limited index types |

---

### My Choice: **Qdrant**

**Why Qdrant for this problem:**

1. **Performance**: Qdrant consistently leads ANN benchmarks (ann-benchmarks.com) for the 1M–10M vector range relevant to this problem. Its Rust core delivers low latency and low memory footprint — important for on-premises deployment where hardware is constrained.

2. **Rich payload filtering**: Qdrant supports filtering on arbitrary JSON metadata *inside* the ANN search (not as a post-filter), meaning queries like "find semantically similar tickets WHERE product_version='4.2' AND status='resolved'" execute efficiently without full-scan overhead. This is essential for routing tickets by product version.

3. **Hybrid search out of the box**: Qdrant (v1.7+) supports sparse + dense hybrid search natively, combining BM25 for exact error-code matching with semantic vector search — crucial when users paste exact error strings.

4. **On-premises deployment**: Qdrant runs as a single Docker container or a distributed cluster without requiring Kubernetes. For a 50,000-document corpus this is trivially deployable on a single VM, keeping customer PII entirely within the organisation's infra.

5. **Excellent Python SDK**: `qdrant-client` is well-documented and integrates directly with LangChain and LlamaIndex — reducing integration time for a small team.

6. **Snapshot & backup**: Built-in collection snapshots make disaster recovery straightforward without third-party tooling.

**Sample Integration Sketch (Python)**:

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from openai import OpenAI

qdrant = QdrantClient("localhost", port=6333)
openai_client = OpenAI()

# --- Indexing a support ticket ---
def index_ticket(ticket_id: str, text: str, metadata: dict) -> None:
    embedding = openai_client.embeddings.create(
        model="text-embedding-3-small", input=text
    ).data[0].embedding

    qdrant.upsert(
        collection_name="support_tickets",
        points=[PointStruct(
            id=ticket_id,
            vector=embedding,
            payload={**metadata, "text": text}
        )]
    )

# --- Semantic search with metadata filter ---
def search_similar_tickets(query: str, product_version: str, top_k: int = 5):
    query_vector = openai_client.embeddings.create(
        model="text-embedding-3-small", input=query
    ).data[0].embedding

    results = qdrant.search(
        collection_name="support_tickets",
        query_vector=query_vector,
        query_filter=Filter(
            must=[FieldCondition(
                key="product_version",
                match=MatchValue(value=product_version)
            )]
        ),
        limit=top_k,
        with_payload=True
    )
    return [(r.payload["text"], r.score) for r in results]
```

This architecture — Qdrant + OpenAI embeddings + LangChain orchestration + GPT-4o generation — gives a production-ready support chatbot that drafts contextually grounded replies in under 2 seconds, with all customer data remaining on-premises.

---

*All answers are original. Assumptions are documented inline.*
