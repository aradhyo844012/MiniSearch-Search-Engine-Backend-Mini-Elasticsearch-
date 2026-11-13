# MiniSearch — API Contract

**Project:** MiniSearch — Search Engine Backend  
**Contract version:** 1.0  
**Status:** Initial agreed specification  
**Backend:** Python 3 Standard Library  
**Frontend:** HTML5, CSS3, Vanilla JavaScript, Bootstrap 5  
**Communication:** HTTP + JSON  
**Server:** Local development server

---

## 1. Purpose

This document defines the communication interface between the MiniSearch frontend and backend.

The backend and frontend developers work independently but must follow the same API contract.

The backend is responsible for:
- Loading and indexing text documents.
- Processing search queries.
- Retrieving and ranking matching documents.
- Correcting spelling errors.
- Generating snippets.
- Providing search statistics and complete documents.
- Returning responses in the formats defined here.

The frontend is responsible for:
- Collecting search queries and search options.
- Sending HTTP requests to the backend.
- Displaying ranked results.
- Highlighting matched terms safely.
- Displaying correction suggestions, statistics and complete documents.
- Handling loading, empty and error states.

**Important:** This contract defines the public HTTP interface. Internal Python functions, classes and data structures may be organized differently as long as the API behaviour remains consistent.

---

## 2. Technical rules

1. The backend must use Python 3 standard-library HTTP functionality.
2. The search engine must be implemented from scratch in Python.
3. The project must not use Elasticsearch, Lucene, Solr, Whoosh, SQLite FTS or any other full-text search engine/library.
4. Original documents must be stored as local UTF-8 `.txt` files.
5. The generated inverted index must be persisted locally using JSON or pickle, with the chosen format documented.
6. All API responses must use JSON encoded as UTF-8.
7. All API endpoints in this version use HTTP GET.
8. The frontend must use JavaScript Fetch API for backend communication.
9. Both frontend and backend must follow the exact field names and data types defined below.

---

## 3. Server configuration

During local development:

**Base URL**

`http://localhost:8000`

**Frontend**

`http://localhost:8000/`

**API endpoints**

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/search` | Search documents |
| GET | `/stats` | Retrieve index statistics |
| GET | `/doc/{id}` | Retrieve a complete document |

The Python server will serve the frontend files and API from the same origin.

This avoids unnecessary CORS configuration during local development.

---

## 4. Common data conventions

### 4.1 Document IDs

- Every indexed document receives a unique document ID.
- The same ID must be used consistently in the index, search results and document retrieval API.
- The frontend must treat document IDs as identifiers and must not calculate or assume their values.
- IDs must be URL-encoded when placed in a document URL.

### 4.2 Search modes

Two search modes are supported:

**OR mode**
- Default mode.
- Returns documents containing at least one query term.
- Ranks results using the sum of term frequencies for the query terms present in each document.

**AND mode**
- Returns only documents containing every query term.
- Uses the same ranking formula among the matching documents.

### 4.3 Ranking and ordering

For a document:

`score = sum of term frequencies of matching query terms`

Results must follow these ordering rules:

1. Higher score first.
2. If scores are equal, shorter document first.
3. If scores and document lengths are equal, lower document ID first.

The backend must use heap-based top-k selection or an equivalent approach rather than sorting every matching document.

### 4.4 Tokenization

- Document text and search queries must use the same tokenizer.
- Text is converted to lowercase.
- Tokens are separated using non-alphanumeric boundaries.
- Stop-word removal is optional and must be consistent between indexing and querying.
- The selected stop-word policy must be documented.

---

## 5. Endpoint 1 — Search documents

**Method:** GET

**Path:** `/search`

### 5.1 Request parameters

Example:

`GET /search?query=python&mode=OR&k=10&offset=0`

| Parameter | Required | Default | Description |
|---|---|---|---|
| `query` | Yes | None | Search text entered by the user |
| `mode` | No | `OR` | Search mode: `OR` or `AND` |
| `k` | No | `10` | Maximum number of results to return |
| `offset` | No | `0` | Number of ranked results to skip |

Validation rules:

- `query` must not be missing, empty or whitespace-only.
- `mode` accepts only `OR` or `AND`.
- `k` must be an integer between 1 and 100.
- `offset` must be a non-negative integer.
- Invalid parameters must return a structured HTTP 400 error.
- An empty query must never return all documents.

### 5.2 Successful response

**HTTP status:** 200 OK

Example:

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
      "snippet": "Python is a programming language used for...",
      "matchedTerms": ["python"]
    },
    {
      "docId": 2,
      "title": "Python Programming Basics",
      "score": 3,
      "snippet": "Learn the basics of Python programming...",
      "matchedTerms": ["python"]
    }
  ]
}
```

### 5.3 Response field definitions

| Field | Type | Description |
|---|---|---|
| `query` | String | Original query entered by the user |
| `mode` | String | Search mode used |
| `k` | Integer | Requested result limit |
| `offset` | Integer | Starting position in ranked results |
| `totalHits` | Integer | Total number of matching documents before pagination |
| `correctedQuery` | String or null | Corrected query, or null when no correction was applied |
| `latencyMs` | Number | Backend query execution time in milliseconds |
| `results` | Array | Ranked results returned for this request |

Each result contains:

| Field | Type | Description |
|---|---|---|
| `docId` | String or number | Unique document identifier |
| `title` | String | Document title |
| `score` | Number | Term-frequency relevance score |
| `snippet` | String | Short relevant text preview |
| `matchedTerms` | Array of strings | Query terms matched in the document |

### 5.4 Pagination behaviour

- `totalHits` represents all matching documents before pagination.
- `offset` determines where the returned result page begins.
- `k` determines the maximum number of results in that page.
- Pagination must preserve the global ranking order.
- If no further results exist, the backend returns an empty `results` array.

### 5.5 Typo correction behaviour

The backend must implement the typo-correction behaviour specified in the PRD.

Rules:

1. Correction is considered for terms absent from the vocabulary or below a documented rarity threshold.
2. Candidate terms are generated using edit distance.
3. Maximum edit distance is 1 for short terms and 2 for longer terms.
4. Candidate selection prioritizes lower edit distance, then higher document frequency.
5. The original query must always be preserved in `query`.
6. If correction is applied, `correctedQuery` contains the corrected full query.
7. If no correction is applied, `correctedQuery` must be `null`.

Example:

Request:

`GET /search?query=pythn&mode=OR&k=10`

Response excerpt:

```json
{
  "query": "pythn",
  "correctedQuery": "python",
  "totalHits": 2,
  "latencyMs": 2.8,
  "results": []
}
```

The results array in this example is illustrative. Actual results must contain the matching documents returned by the search engine.

The frontend must:

- Display a message such as "Showing results for python".
- Provide an option to search the original query, `pythn`.
- Preserve the original query so the user can return to it.

---

## 6. Endpoint 2 — Index statistics

**Method:** GET

**Path:** `/stats`

### 6.1 Request

`GET /stats`

No query parameters are required.

### 6.2 Successful response

**HTTP status:** 200 OK

Example:

```json
{
  "totalDocuments": 100,
  "vocabularySize": 2500,
  "indexSizeBytes": 524288,
  "buildTimeMs": 1250,
  "builtAt": "2026-11-13T10:30:00"
}
```

### 6.3 Response field definitions

| Field | Type | Description |
|---|---|---|
| `totalDocuments` | Integer | Number of successfully indexed documents |
| `vocabularySize` | Integer | Number of unique terms in the vocabulary |
| `indexSizeBytes` | Integer | Size of the persisted index file in bytes |
| `buildTimeMs` | Number | Time taken to build the index in milliseconds |
| `builtAt` | String or null | Date and time of the most recent successful index build |

The backend must obtain these values from actual index and build information. It must not return fabricated statistics.

If the index has not been built or loaded, return the `INDEX_NOT_READY` error defined below.

---

## 7. Endpoint 3 — Retrieve a complete document

**Method:** GET

**Path:** `/doc/{id}`

### 7.1 Request

Example:

`GET /doc/1`

The ID must correspond to a document ID returned by the search endpoint.

### 7.2 Successful response

**HTTP status:** 200 OK

Example:

```json
{
  "docId": 1,
  "title": "Introduction to Python",
  "content": "Python is a programming language used for general-purpose programming..."
}
```

### 7.3 Response field definitions

| Field | Type | Description |
|---|---|---|
| `docId` | String or number | Unique document identifier |
| `title` | String | Document title |
| `content` | String | Complete original document text |

The frontend must use the document ID from the search result to request the full document.

The backend must return HTTP 404 if the requested document does not exist.

---

## 8. Error response format

All API errors must use one consistent JSON structure.

Example:

```json
{
  "error": {
    "code": "DOCUMENT_NOT_FOUND",
    "message": "The requested document was not found."
  }
}
```

### 8.1 Error codes and HTTP status codes

| HTTP status | Error code | Description |
|---|---|---|
| 400 | `INVALID_QUERY` | Query is missing, empty or whitespace-only |
| 400 | `INVALID_PARAMETER` | Invalid mode, k or offset |
| 404 | `DOCUMENT_NOT_FOUND` | Requested document does not exist |
| 404 | `ENDPOINT_NOT_FOUND` | Requested API endpoint does not exist |
| 503 | `INDEX_NOT_READY` | Index has not been built or loaded |
| 500 | `INTERNAL_SERVER_ERROR` | Unexpected backend error |

### 8.2 Error handling rules

- The backend must not expose Python tracebacks or internal file paths in API responses.
- The frontend must display an understandable error message.
- The frontend must preserve the user's search query after an error.
- API errors must use the same JSON error structure.
- An unavailable server cannot return an API JSON response; the frontend must handle Fetch/network failures separately.

---

## 9. Search snippets and highlighting

The backend is responsible for generating a useful snippet around a relevant match.

The snippet must:

- Contain relevant document text.
- Include the matched search terms where possible.
- Be returned as plain text.
- Not contain HTML markup generated by the backend.

The frontend is responsible for highlighting matched terms visually.

**Security rule:** The frontend must safely escape untrusted document text before inserting highlight markup. It must not insert raw document content or snippets as executable HTML.

---

## 10. Query latency measurement

The `latencyMs` field must measure search-engine query execution time.

It must exclude:

- HTTP network transfer time.
- Browser rendering time.
- Frontend JavaScript execution time.
- Time spent loading the complete document.

Use a monotonic high-resolution timer for measurement.

The benchmark script must separately measure repeated query runs and report p50 and p95 latency.

The PRD target is p95 query latency below 50 ms on a 100k+ document corpus under documented hardware and query conditions.

The API response's `latencyMs` is not an end-to-end browser response time.

---

## 11. Query logging

Automatic query logging by the API is listed as a good-to-have feature in the PRD, not a required MVP endpoint.

The required analysis workflow must be able to load a text query file containing one query per line.

If automatic API logging is implemented later, it must not change the search response format defined in this contract.

Query logs should contain sufficient information for the analysis workflow, including query text, timestamp and result count where available.

---

## 12. Frontend integration requirements

The frontend developer must implement the following behaviour.

| Frontend feature | Backend interaction |
|---|---|
| Search input | `GET /search` |
| OR/AND toggle | `mode` parameter in `/search` |
| Result limit | `k` parameter in `/search` |
| Pagination | `offset` parameter in `/search` |
| Result count | `totalHits` from `/search` |
| Result ranking | Preserve backend result order |
| Search latency | `latencyMs` from `/search` |
| Typo correction notice | `correctedQuery` from `/search` |
| Highlighted snippets | `snippet` and `matchedTerms` |
| Complete document view | `GET /doc/{id}` |
| Index statistics | `GET /stats` |

The frontend must also support:

- Initial search page state.
- Loading state.
- Empty query state.
- No-results state.
- Typo-corrected state.
- API unavailable state.
- Index not built state.
- Invalid input state.
- Error state.
- Responsive layouts for phone, tablet and desktop.

---

## 13. Features outside the HTTP API

The following required PRD features are implemented through Python modules and CLI commands. They do not require additional HTTP endpoints in API Contract v1.0.

### CLI commands

The project must support:

| Command | Purpose |
|---|---|
| `build` | Build and persist the inverted index |
| `search` | Search documents from the terminal |
| `stats` | Display index statistics |
| `benchmark` | Run performance and typo-recall evaluation |
| `analyze` | Run query-log and Zipf analysis |

The CLI and HTTP API must use the same underlying search-engine logic. Ranking must not be implemented twice.

### Benchmarking

The benchmark workflow must:

- Generate or load a 100k+ document benchmark corpus.
- Use a documented query set.
- Measure repeated query latency.
- Report p50 and p95.
- Evaluate typo recall using labelled typo cases.
- Record hardware, operating system, Python version, corpus size, average document length and query-set details.
- Report actual measurements honestly.

### Extended data analysis

The analysis workflow must:

- Load a text query file using pandas.
- Tokenize queries using the engine's tokenizer.
- Compute the top 10 most frequent query terms.
- Calculate document frequency from the inverted index.
- Rank terms by document frequency.
- Generate a log-log document-frequency-versus-rank plot.
- Fit a line using NumPy.
- Report slope and R-squared.
- Save the chart, CSV output and a 3–5 sentence interpretation.

These are required project deliverables, but they are not additional browser API endpoints.

---

## 14. What is not included in API Contract v1.0

The following are optional or stretch features, not part of the initial required API:

- TF-IDF or BM25.
- Phrase search.
- Prefix search.
- Autocomplete.
- Incremental indexing.
- Multiprocessing and sharding.
- Automatic query logging and zero-result reports.
- Analytics dashboard API.
- Authentication and user accounts.
- Semantic or vector search.

Do not add these features before completing the required MVP.

A browser-triggered index rebuild endpoint is also not included in this version. The required initial build/rebuild workflow is provided through the CLI.

---

## 15. Shared development responsibilities

### Backend developer

- Follow the agreed project folder structure.
- Implement all core search functionality.
- Implement the three API endpoints.
- Follow the request and response formats in this document.
- Validate input and handle errors.
- Test API responses independently.
- Inform the frontend developer before any proposed contract change.

### Frontend developer

- Follow the agreed project folder structure.
- Build the UI using HTML, CSS, JavaScript and Bootstrap 5.
- Use mock JSON responses matching this contract during independent development.
- Use the exact endpoint paths and parameter names.
- Display the response fields defined in this document.
- Handle loading, empty, error and correction states.
- Inform the backend developer before any proposed contract change.

### Shared responsibilities

- Maintain one copy of this document in the GitHub repository.
- Both developers must use the same version.
- Discuss interface changes before implementing them.
- Update this document whenever an agreed interface change is made.
- Test the actual frontend-backend integration together.

---

## 16. Integration and acceptance checklist

The API integration is considered complete only after the following checks pass.

### Search API

- [ ] Normal single-term search returns valid JSON.
- [ ] Multi-term OR search works correctly.
- [ ] Multi-term AND search works correctly.
- [ ] Top-k limit works correctly.
- [ ] Offset and pagination preserve ranking order.
- [ ] Results follow score, document-length and document-ID tie-breaking rules.
- [ ] Empty and invalid queries return structured errors.
- [ ] No-result queries return an empty results array.
- [ ] Typo correction returns the corrected query when applicable.
- [ ] Original query can be searched again.
- [ ] Snippets and matched terms are returned.
- [ ] Latency is measured around search execution only.

### Statistics API

- [ ] Total document count is correct.
- [ ] Vocabulary size is correct.
- [ ] Index file size is reported.
- [ ] Last build time is reported when available.
- [ ] Index-not-ready state is handled correctly.

### Document API

- [ ] A valid document ID returns complete document content.
- [ ] An invalid document ID returns HTTP 404.
- [ ] Document IDs match those in search results.

### Frontend integration

- [ ] Search input communicates with the actual backend.
- [ ] OR/AND controls work.
- [ ] Results appear in backend ranking order.
- [ ] Result count and latency are displayed.
- [ ] Matched terms are highlighted safely.
- [ ] Typo correction notice works.
- [ ] Complete documents can be opened.
- [ ] Loading, empty, offline and error states work.
- [ ] Responsive layout works on phone and laptop.

---

## 17. Contract change policy

This document is the shared interface specification for MiniSearch Version 1.0.

Neither developer should independently rename an endpoint, request parameter or response field.

If a change becomes necessary:

1. Discuss the reason with the other developer.
2. Agree on the proposed change.
3. Update `API_CONTRACT.md`.
4. Commit the updated document to GitHub.
5. Ensure both implementations follow the updated version.
6. Test the integration again.

**Final principle: The frontend and backend may be developed independently, but they must behave as two parts of the same system.**
