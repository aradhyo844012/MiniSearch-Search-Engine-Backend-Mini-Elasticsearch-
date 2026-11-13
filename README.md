# MiniSearch — Search Engine Backend

**A lightweight, Python-based search engine built from scratch to demonstrate the fundamentals of information retrieval, document indexing, ranked search, and search analytics.**

---

## 1. Project Overview

MiniSearch is a small Python-based search engine that allows users to search through a collection of text documents efficiently.

Imagine having hundreds or thousands of text files on your computer. If you want to find documents containing a particular word, you could open every file and search through it manually. However, this becomes increasingly slow and inconvenient as the number of documents grows.

MiniSearch addresses this problem by building an **inverted index** — a data structure that stores which documents contain each word. Instead of repeatedly scanning every document for every query, the search engine uses this index to locate matching documents more efficiently.

Users can enter a search query through a web interface, receive ranked results, view relevant text snippets, and open complete documents.

The project is designed as an educational implementation of fundamental search-engine concepts, without depending on existing full-text search engines such as Elasticsearch or Lucene.

## 2. Problem Statement

Searching through a large collection of unorganized text documents can be inefficient when every search requires checking documents individually.

A useful search system should be able to:

- Organize documents in a searchable structure.
- Retrieve documents containing relevant terms.
- Rank results according to their relevance.
- Handle common spelling mistakes.
- Display useful previews of matching documents.
- Provide information about the index and search performance.
- Analyze document and query statistics.

MiniSearch aims to demonstrate how these capabilities can be implemented using Python and fundamental data structures and algorithms.

## 3. Project Objectives

The primary objectives of MiniSearch are to:

1. Understand and implement an inverted index from scratch.
2. Develop a document-processing and tokenization pipeline.
3. Implement term-frequency-based document ranking.
4. Support both OR and AND search operations.
5. Implement basic typo correction using edit distance.
6. Generate contextual snippets for search results.
7. Expose search functionality through a lightweight JSON API.
8. Build a browser-based frontend for interacting with the search engine.
9. Implement index persistence and command-line operations.
10. Evaluate search performance and analyze document-frequency distributions.

## 4. How MiniSearch Works

The search engine follows a sequence of processing steps.

### Step 1: Document Collection

MiniSearch works with a collection of local UTF-8 text files (`.txt`).

Each document is assigned a unique document ID and associated with its title and original content.

### Step 2: Tokenization

Before indexing, the document text is converted into searchable terms.

For example:

Original text:

`Python is a powerful programming language.`

After lowercasing and tokenization:

`["python", "is", "a", "powerful", "programming", "language"]`

The tokenizer uses non-alphanumeric boundaries to separate words. The same tokenization rules are applied to search queries to maintain consistency.

### Step 3: Inverted Index Construction

An inverted index maps each term to the documents in which it appears.

For example:

| Term | Document ID | Term Frequency |
|---|---:|---:|
| python | 1 | 3 |
| python | 2 | 1 |
| programming | 1 | 2 |
| programming | 3 | 4 |
| search | 2 | 2 |

Here, **term frequency (TF)** means the number of times a particular term occurs in a document.

This structure allows the search engine to locate documents associated with a query term without scanning every original document.

### Step 4: Query Processing

When a user enters a search query:

1. The query is validated.
2. It is converted into lowercase tokens.
3. The inverted index is checked for those terms.
4. Matching document candidates are retrieved.
5. The selected search mode determines which candidates qualify.

MiniSearch supports two search modes:

- **OR Search:** Returns documents containing at least one of the query terms.
- **AND Search:** Returns only documents containing every query term.

### Step 5: Document Ranking

Matching documents are ranked using a simple term-frequency scoring method.

The score for a document is calculated as:

`Score = Sum of term frequencies of matching query terms`

Higher scores indicate that the document contains more occurrences of the searched terms.

When two documents have equal scores, the ranking rules are:

1. Shorter document first.
2. Lower document ID first if document lengths are also equal.

The search engine uses heap-based top-k selection or an equivalent approach to avoid sorting every matching document unnecessarily.

### Step 6: Typo Correction

MiniSearch includes a basic typo-correction mechanism.

For example:

- User query: `pythn`
- Possible correction: `python`

The system uses edit distance to identify vocabulary terms that are similar to a misspelled query term.

The maximum allowed edit distance is:

- 1 for short terms.
- 2 for longer terms.

When multiple candidates are available, the system prioritizes smaller edit distance and then higher document frequency.

The original query is preserved, and the corrected query is returned separately when a correction is applied.

### Step 7: Snippet Generation

Instead of displaying an entire document in the search-results list, MiniSearch generates a short text preview around relevant matching terms.

The backend returns snippets as plain text along with the matched terms. The frontend is responsible for safely highlighting those terms.

Users can open a result to view its complete document.

### Step 8: API Communication

The backend exposes its functionality through HTTP endpoints that return JSON responses.

The frontend communicates with the backend using JavaScript's Fetch API.

This separation allows the backend search logic and frontend interface to be developed independently while following a shared API contract.

## 5. Key Features

### Core Search Engine

- **Document Loading:** Reads a collection of local UTF-8 text documents.
- **Text Tokenization:** Converts text into lowercase searchable tokens.
- **Inverted Index:** Maps terms to document IDs and their term frequencies.
- **Document Frequency:** Tracks how many documents contain each term.
- **OR Search:** Retrieves documents containing at least one query term.
- **AND Search:** Retrieves documents containing all query terms.
- **Term-Frequency Ranking:** Assigns relevance scores based on matching-term frequencies.
- **Top-k Retrieval:** Efficiently selects the highest-ranked results.
- **Pagination:** Supports result limits and offsets while preserving ranking order.
- **Tie-breaking:** Uses document length and document ID when scores are equal.

### Search Experience

- Search through a browser-based interface.
- Display ranked search results.
- Show document titles and relevance scores.
- Display contextual result snippets.
- Identify matched query terms.
- Provide basic typo correction.
- Allow users to open complete documents.
- Display search latency and total matching-result count.
- Support loading, empty, no-results, and error states.

### Index Management and Storage

- Build an inverted index from the document collection.
- Persist the generated index locally using JSON or pickle.
- Load an existing persisted index.
- Rebuild the index when required through the command-line workflow.
- Retrieve index statistics.

### Search Analytics and Evaluation

- Measure query execution time.
- Benchmark search performance on a large document collection.
- Report median (p50) and 95th-percentile (p95) query latency.
- Evaluate typo-correction recall.
- Analyze query-term frequencies.
- Calculate document frequencies.
- Generate a Zipf-style log-log distribution plot.
- Estimate the distribution's slope and R-squared value.

## 6. System Architecture

MiniSearch is organized into independent components, each responsible for a specific part of the application.

```text
                    USER
                      |
                      v
             FRONTEND INTERFACE
             HTML / CSS / JavaScript
                      |
                      | HTTP + JSON
                      v
                PYTHON API
                      |
                      v
             SEARCH ENGINE CORE
                      |
        +-------------+-------------+
        |             |             |
        v             v             v
    Tokenizer     Indexer       Search Engine
                      |             |
                      |             v
                      |          Ranker
                      |             |
                      |             v
                      |       Typo Correction
                      |             |
                      |             v
                      |      Snippet Generator
                      |             |
                      +-------------+
                      |
                      v
               INDEX STORAGE
                      |
                      v
              ORIGINAL DOCUMENTS

             SUPPORTING COMPONENTS
              CLI / Benchmarking
                / Analytics
```

### Main Backend Components

| Component | Responsibility |
|---|---|
| Corpus Loader | Reads and prepares text documents. |
| Tokenizer | Converts text and queries into searchable tokens. |
| Indexer | Builds the inverted index and document statistics. |
| Search Engine | Retrieves documents matching a query. |
| Ranker | Scores and orders matching documents. |
| Typo Corrector | Identifies possible spelling corrections. |
| Snippet Generator | Creates contextual result previews. |
| Index Storage | Saves and loads the generated index. |
| API Server | Handles HTTP requests and returns JSON responses. |
| CLI | Provides terminal-based project operations. |

The command-line interface and HTTP API use the same underlying search-engine logic.

## 7. API Endpoints

MiniSearch uses a lightweight Python HTTP server and JSON-based communication.

**Local development base URL:** `http://localhost:8000`

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/search` | Search documents and retrieve ranked results. |
| GET | `/stats` | Retrieve index statistics. |
| GET | `/doc/{id}` | Retrieve the complete content of a document. |

### Search API Example

Request:

`GET /search?query=python&mode=OR&k=10&offset=0`

Example response:

```json
{
  "query": "python",
  "mode": "OR",
  "k": 10,
  "offset": 0,
  "totalHits": 2,
  "correctedQuery": null,
  "latencyMs": 2.4,
  "results": [
    {
      "docId": 1,
      "title": "Introduction to Python",
      "score": 5,
      "snippet": "Python is a programming language...",
      "matchedTerms": ["python"]
    }
  ]
}
```

### Statistics API

`GET /stats`

Provides information such as:

- Total indexed documents.
- Vocabulary size.
- Persisted index size in bytes.
- Index build time.
- Last successful build timestamp.

### Document API

`GET /doc/{id}`

Returns the complete original document content, its title, and its unique document ID.

All API errors follow a consistent JSON structure defined in `API_CONTRACT.md`.

For complete request parameters, response structures, validation rules, and error codes, refer to the project's **API_CONTRACT.md**.

## 8. Command-Line Interface

In addition to the browser-based interface, MiniSearch provides command-line operations for managing and evaluating the search engine.

| Operation | Purpose |
|---|---|
| Build | Construct and persist the inverted index. |
| Search | Execute a search query from the terminal. |
| Stats | Display index statistics. |
| Benchmark | Evaluate search performance and typo recall. |
| Analyze | Perform query-log and document-frequency analysis. |

The CLI provides an alternative way to interact with the search engine without using the browser.

## 9. Benchmarking and Performance Evaluation

An important objective of MiniSearch is to understand how search performance changes as the document collection grows.

The benchmark workflow is designed to:

- Use a corpus containing 100,000 or more documents.
- Execute a documented set of search queries.
- Measure repeated query execution times.
- Calculate p50 and p95 latency.
- Evaluate typo-correction recall using labelled typo cases.
- Record the hardware, operating system, Python version, corpus size, and query conditions.

**PRD performance target:** p95 query latency below 50 milliseconds on a corpus containing 100,000 or more documents, under documented test conditions.

This is a target to measure and evaluate, not a claim of achieved performance.

### Typo Recall

Typo recall evaluates whether the search engine can recover the intended search term from an intentionally misspelled query.

The evaluation checks whether the expected document appears within the top 10 search results for the corresponding typo query.

## 10. Data Analysis and Zipf's Law

MiniSearch also includes an extended data-analysis component that studies the frequency distribution of terms in documents and search queries.

The analysis workflow includes:

1. Loading query data using pandas.
2. Tokenizing queries using the same tokenizer as the search engine.
3. Identifying the ten most frequent query terms.
4. Calculating document frequency for indexed terms.
5. Sorting terms by document frequency.
6. Plotting document frequency against term rank on logarithmic axes.
7. Fitting a line using NumPy.
8. Calculating the slope and R-squared value.
9. Producing a short interpretation of the observed distribution.

The analysis helps demonstrate how frequently occurring words and rare words are distributed across a document collection.

## 11. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3 | Backend development and search-engine implementation. |
| Python Standard Library | HTTP server, data structures, file handling, and core processing. |
| HTML5 | Frontend structure. |
| CSS3 | Frontend styling and responsive layout. |
| Vanilla JavaScript | User interactions and API communication. |
| Bootstrap 5 | Frontend layout and responsive UI components. |
| JSON / Pickle | Local index persistence. |
| pandas | Query-log and data analysis. |
| NumPy | Numerical analysis and line fitting. |
| Matplotlib | Data visualization and Zipf-style plots. |
| Git and GitHub | Version control and team collaboration. |

The search engine's indexing, retrieval, and ranking logic is implemented from scratch. Existing full-text search engines and indexing libraries are not used.

## 12. Project Structure

The proposed project organization separates the backend, frontend, data, testing, benchmarking, and documentation.

```text
MiniSearch/
│
├── README.md
├── API_CONTRACT.md
├── .gitignore
├── requirements.txt
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── cli.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── corpus_loader.py
│   │   ├── tokenizer.py
│   │   ├── indexer.py
│   │   ├── search.py
│   │   ├── ranker.py
│   │   ├── typo_corrector.py
│   │   ├── snippet_generator.py
│   │   └── text_utils.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── server.py
│   │
│   └── storage/
│       ├── __init__.py
│       └── index_storage.py
│
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── main.js
│   │   ├── api.js
│   │   └── results.js
│   └── assets/
│
├── corpus/
│   ├── sample_documents/
│   └── README.md
│
├── data/
│   ├── index/
│   └── logs/
│
├── tests/
│   ├── test_corpus_loader.py
│   ├── test_tokenizer.py
│   ├── test_indexer.py
│   ├── test_search.py
│   ├── test_ranker.py
│   ├── test_typo_corrector.py
│   ├── test_snippet_generator.py
│   └── test_api.py
│
├── benchmarks/
│   ├── benchmark.py
│   ├── corpus_generator.py
│   ├── query_generator.py
│   ├── typo_evaluator.py
│   ├── metrics.py
│   └── results/
│
├── analysis/
│   ├── analyze.py
│   ├── query_log_analyzer.py
│   ├── document_frequency.py
│   ├── zipf_analysis.py
│   ├── query_log.csv
│   ├── output/
│   └── reports/
│
└── docs/
    ├── project_overview.md
    ├── architecture.md
    ├── setup_guide.md
    ├── benchmark_report.md
    ├── analysis_interpretation.md
    └── screenshots/
```

This is the planned organization. Files may be combined or adjusted during development where doing so keeps the implementation simpler without compromising separation of responsibilities.

## 13. Testing Strategy

Testing is essential to ensure that the search engine behaves correctly.

The project will include tests for:

- Text tokenization.
- Document loading.
- Inverted-index construction.
- Document-frequency calculation.
- OR and AND search behaviour.
- Ranking and tie-breaking.
- Top-k retrieval and pagination.
- Typo correction.
- Snippet generation.
- API request validation.
- API response formats.
- Document retrieval.
- Error handling.

The frontend will also be tested for search interactions, result rendering, document viewing, loading states, and error handling.

## 14. Optional Enhancements

The following features are possible extensions beyond the initial required implementation:

- TF-IDF or BM25 ranking.
- Phrase search.
- Prefix search.
- Search autocomplete.
- Incremental indexing.
- Multiprocessing and sharding.
- Automatic query logging.
- Zero-result query reports.
- Additional analytics visualizations.

These enhancements will only be considered after the required project functionality is implemented and tested.

MiniSearch does not aim to implement distributed search clusters, semantic/vector search, machine-learning ranking, or advanced document parsing.

## 15. Team Responsibilities

MiniSearch is developed by a two-member team.

**Backend Development**
- Python-based search-engine implementation.
- Document loading and processing.
- Inverted-index construction.
- Search and ranking algorithms.
- Typo correction and snippet generation.
- Index persistence.
- HTTP API and CLI.
- Backend testing and benchmarking.
- Data analysis.

**Frontend Development**
- HTML and CSS interface.
- Responsive page layout.
- Search input and controls.
- API communication using JavaScript.
- Search-result presentation.
- Snippet and matched-term highlighting.
- Complete document viewing.
- Loading, empty, and error states.

Both developers follow the shared `API_CONTRACT.md` to ensure that the frontend and backend integrate correctly.

## 16. Development Status

MiniSearch is currently in its initial development stage.

The features described in this README represent the project scope and planned functionality. They should not be interpreted as confirmation that every feature has already been implemented.

Implementation progress, testing results, screenshots, and benchmark measurements will be updated as development proceeds.

## 17. Learning Outcomes

Through MiniSearch, we aim to gain practical experience with:

- Python programming and software design.
- Data structures and algorithms.
- Information retrieval fundamentals.
- Inverted indexes and term-frequency scoring.
- HTTP APIs and JSON communication.
- Frontend-backend integration.
- File handling and data persistence.
- Testing and debugging.
- Git and GitHub collaboration.
- Performance benchmarking.
- Data analysis and visualization.
- Technical documentation.

## 18. Project Documentation

- **`README.md`** — Project introduction, features, architecture, and setup.
- **`API_CONTRACT.md`** — The agreed interface specification for frontend-backend communication.
- **`docs/`** — Architecture, setup instructions, benchmark reports, and supporting documentation.

---

**MiniSearch — Understanding how search engines find, retrieve, and rank information, one document at a time.**
