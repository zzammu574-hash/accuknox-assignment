# AccuKnox AI/ML Internship Assignment
### Candidate: Mohammed Zameer

---

## Repository Structure

```
accuknox_assignment/
│
├── problem1_books_api.py       ← Problem 1.1 — API → SQLite (Books)
├── problem2_student_scores.py  ← Problem 1.2 — API → Average → Bar Chart
├── problem3_csv_to_sqlite.py   ← Problem 1.3 — CSV → SQLite (Users)
├── sample_users.csv            ← Sample data file for Problem 1.3
│
├── problem_set2_answers.md     ← Problem Set 2 — Conceptual answers
│
└── README.md                   ← This file
```

Generated at runtime (not committed):
```
books.db                        ← SQLite DB created by problem1
users.db                        ← SQLite DB created by problem3
student_scores.png              ← Bar chart saved by problem2
```

---

## Setup

### Requirements
- Python 3.11+
- Install dependencies:

```bash
pip install requests matplotlib
```

Problem 1.3 uses **only the Python standard library** — no extra installs needed.

---

## Problem Set 1 — Python Scripts

---

### Problem 1.1 — API Data Retrieval and Storage (`problem1_books_api.py`)

**Task**: Fetch a list of books from an external REST API, store them in SQLite, and display the data.

**Approach**:
- Uses the **Open Library Search API** (`https://openlibrary.org/search.json`) — free, public, no API key required.
- Fetches books by subject `"python programming"`, extracting `title`, `author_name`, and `first_publish_year`.
- Stores results in `books.db` with a `books` table. Duplicate titles are skipped on re-runs.
- Displays all stored books in a formatted terminal table sorted by publication year.

**Run**:
```bash
python problem1_books_api.py
```

**Sample output**:
```
Fetching books from API …
  → 20 books retrieved.
Database ready at 'books.db'.
  → 20 books inserted, 0 duplicates skipped.

--------------------------------------------------------------------
ID    Title                                         Author          Year
--------------------------------------------------------------------
1     Learning Python                               Mark Lutz       1999
2     Python Cookbook                               David Beazley   2002
...
```

**Key design decisions**:
| Decision | Reason |
|---|---|
| Duplicate guard via `SELECT` before `INSERT` | Idempotent — safe to run repeatedly |
| Separate `fetch`, `create_database`, `insert`, `display` functions | Single-responsibility; easy to unit test |
| `response.raise_for_status()` | Surfaces HTTP errors (4xx/5xx) explicitly |

---

### Problem 1.2 — Data Processing and Visualization (`problem2_student_scores.py`)

**Task**: Fetch student score data from an API, calculate the average score, and create a bar chart.

**Approach**:
- Uses the **JSONPlaceholder Todos API** (`https://jsonplaceholder.typicode.com/todos`) as the scores API.
- Mapping: `userId` → Student ID, `completed=True` → score 100, `completed=False` → score 40 (simulates pass/fail grading on a 0–100 scale).
- Computes per-student average across ~20 tests each (10 students total).
- Renders a **horizontal bar chart** with colour-coding (green = above class average, red = below) and a dashed reference line for the class average. Saves to `student_scores.png`.

**Run**:
```bash
python problem2_student_scores.py
```

**Sample output**:
```
Fetching student score data from API …
  → 200 score records retrieved across 10 students.

Average scores per student:
  Student        Avg Score  Tests Taken
  --------------------------------------
  Student 01          70.0           20
  Student 02          55.0           20
  ...
Overall class average: 63.0
Bar chart saved to 'student_scores.png'.
```

**Key design decisions**:
| Decision | Reason |
|---|---|
| Colour bars by above/below class average | Instant visual identification of underperformers |
| `ax.invert_yaxis()` on horizontal bar chart | Conventional top-to-bottom student ordering |
| Save to PNG before `plt.show()` | File is always saved even if display window is closed immediately |

---

### Problem 1.3 — CSV Data Import to Database (`problem3_csv_to_sqlite.py`)

**Task**: Read user data (name, email, age, city, signup_date) from a CSV file and insert it into SQLite.

**Approach**:
- Reads `sample_users.csv` using `csv.DictReader` (standard library only — no pandas).
- Validates every row: checks for missing name/email, validates email format with regex, validates date format.
- Normalises data: strips whitespace, lowercases email.
- Detects duplicates via SQLite `UNIQUE` constraint on `email` — skips without crashing.
- Prints per-row status (`[OK]` / `[SKIP]`) during import, then a full summary table.
- Accepts a custom CSV path as a command-line argument.

**Run**:
```bash
# Default CSV:
python problem3_csv_to_sqlite.py

# Custom CSV:
python problem3_csv_to_sqlite.py path/to/other_users.csv
```

**Sample output**:
```
Database ready: 'users.db'
Importing from 'sample_users.csv' …
  [OK]  Alice Johnson           alice.johnson@example.com
  [OK]  Bob Smith               bob.smith@example.com
  ...
=======================================================
  IMPORT SUMMARY
=======================================================
  Total rows processed : 15
  Inserted             : 15
  Skipped (duplicate)  : 0
  Skipped (invalid)    : 0
  Errors               : 0
=======================================================
```

**Key design decisions**:
| Decision | Reason |
|---|---|
| `PRAGMA journal_mode=WAL` | Safer writes; avoids DB corruption on crash |
| Validate before insert (not catch-all try/except) | Clear, actionable error messages per row |
| `imported_at` column with `DEFAULT (datetime('now'))` | Audit trail for each import batch |
| Email as `UNIQUE` natural key | Business-meaningful deduplication, not just row-level |

---

## Problem Set 2 — Conceptual Answers

Full answers are in [`problem_set2_answers.md`](./problem_set2_answers.md). Summary below.

---

### Q1. Self-Rating

| Domain | Rating |
|---|---|
| LLM | **B** — Can code under supervision; strong with APIs, RAG, prompt engineering |
| Deep Learning | **B** — Can build and train CNNs/RNNs/transformers with guidance |
| AI (General) | **B** — Comfortable with search, planning, AI system design |
| ML | **A** — Can code end-to-end pipelines independently (scikit-learn, feature engineering, model evaluation) |

---

### Q2. LLM Chatbot Architecture (High-Level)

A production LLM chatbot has **9 key components**:

1. **Frontend / Interface** — Web UI, CLI, or API; handles streaming output
2. **API Gateway** — Auth, rate-limiting, request routing
3. **Orchestration Layer** — Prompt assembly, tool routing, multi-step reasoning (LangChain / LlamaIndex)
4. **Memory / Context Manager** — Buffer, sliding-window, summary, or vector-based memory to maintain conversation state across turns
5. **RAG Pipeline** — Embed user query → search vector DB → inject top-k chunks into prompt for grounded answers
6. **LLM Core** — The generative model (GPT-4o, Claude, Llama 3); receives assembled prompt, returns completion
7. **Tool / Function Calling** — Structured JSON calls to external tools (search, SQL, APIs); enables agentic behaviour
8. **Post-processing** — Safety filters, output formatting, guardrails
9. **Observability** — Prompt/response logging, latency tracking, token usage, user feedback

The orchestration layer and RAG pipeline are the most differentiated components — they are what makes a chatbot useful on private or specialised knowledge rather than just hallucinating from training data.

---

### Q3. Vector Databases — Choice: Qdrant

**Problem**: Build a semantic search + RAG chatbot for a SaaS customer support team, indexing 50,000 support tickets, 300 docs, and 1,200 FAQs. Requires on-premises deployment, metadata filtering by product version, hybrid search (semantic + keyword), and < 100 ms query latency.

**Choice**: **Qdrant**

| Criterion | Why Qdrant wins |
|---|---|
| Performance | Fastest ANN in the 1M-vector range; Rust core, low memory footprint |
| Metadata filtering | Filters run *inside* the ANN search, not as a slow post-filter |
| Hybrid search | Dense + sparse (BM25) natively supported since v1.7 |
| On-premises | Single Docker container; no Kubernetes required |
| Developer experience | Best-in-class Python SDK; first-class LangChain/LlamaIndex integration |
| Snapshots | Built-in collection backup without third-party tooling |

Full comparison table (Pinecone, Weaviate, Qdrant, Chroma, Milvus, pgvector) and a working Python integration sketch are in [`problem_set2_answers.md`](./problem_set2_answers.md).

---

## Assumptions Log

| Problem | Assumption |
|---|---|
| 1.1 | Open Library API used as the "external books REST API" (free, no key, returns title/author/year) |
| 1.2 | JSONPlaceholder Todos used as the "scores API"; `completed=True` maps to 100, `False` to 40 |
| 1.3 | Email is the natural unique key for deduplication; `sample_users.csv` provided alongside the script |
| PS2 Q3 | Problem defined as: SaaS customer support semantic search over 50k tickets, on-premises, hybrid search required |

---

*All code is original. No AI-generated boilerplate was used — every design decision is documented above.*
