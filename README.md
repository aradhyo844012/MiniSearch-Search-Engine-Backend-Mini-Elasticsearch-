# MiniSearch — Search Engine Backend

MiniSearch is a Python-based search engine backend designed to search through a collection of text documents. It uses an inverted index to find relevant documents efficiently, supports OR and AND search modes, ranks results using term frequency, and includes basic typo correction.

The project is being developed as a first-semester B.Tech CSE Applied AI OJT project at Polaris School of Technology.

## Features

- **Document loading:** Loads text documents using metadata stored in a CSV manifest.
- **Text tokenization:** Converts text into lowercase searchable terms.
- **Inverted indexing:** Stores the documents in which each term appears, along with its term frequency.
- **Index persistence:** Saves and loads the search index using JSON.
- **Search:** Supports OR and AND search modes.
- **Result ranking:** Ranks documents using term frequency, with document length and document ID as tie-breakers.
- **Pagination:** Supports result limits and offsets.
- **Typo correction:** Suggests corrections for misspelled or rare query terms using edit distance and document frequency.
- **Search snippets:** Returns a short text preview for each result.
- **REST API:** Provides endpoints for searching, retrieving document information, and viewing index statistics.
- **CLI:** Provides commands for building the index, searching, viewing statistics, benchmarking, and analysis.
- **Performance benchmarking:** Measures search latency across sample queries.
- **Document-frequency analysis:** Generates a CSV report and a log-log graph of term rank against document frequency.

## Technology Stack

- Python 3
- Python standard library for the search engine and HTTP API
- JSON for index storage
- Pandas for query-data analysis
- NumPy for numerical analysis
- Matplotlib for graph generation

## Project Structure

```text
MiniSearch/
│
├── data/
│   ├── corpus/                         # Text document collection
│   ├── manifest.csv                    # Document metadata
│   └── index.json                       # Generated search index
│
├── reports/
│   ├── term_frequency_analysis.csv
│   └── term_frequency_distribution.png
│
├── src/
│   ├── __init__.py
│   ├── document_loader.py
│   ├── tokenizer.py
│   ├── index_builder.py
│   ├── index_storage.py
│   ├── search_engine.py
│   ├── typo_corrector.py
│   ├── api_server.py
│   ├── cli.py
│   ├── benchmark.py
│   └── analyze.py
│
├── analysis_queries.txt
├── requirements.txt
├── API_CONTRACT.md
├── .gitignore
└── README.md
```

The `data/` directory contains the document collection and generated search index. These files are excluded from Git using `.gitignore`.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/aradhyo844012/MiniSearch-Search-Engine-Backend-Mini-Elasticsearch-.git

cd MiniSearch-Search-Engine-Backend-Mini-Elasticsearch-
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Add the dataset

Place the extracted dataset in the following structure:

```text
data/
├── corpus/
└── manifest.csv
```

The corpus should contain the `.txt` documents referenced by `manifest.csv`.

The dataset is not included in the Git repository.

### 4. Build the search index

```bash
python -m src.cli build
```

This loads the documents, builds the inverted index, and saves it to `data/index.json`.

## Running the Backend

Start the API server:

```bash
python -m src.api_server
```

The backend runs locally at:

```text
http://localhost:8000
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/search?query=python` | Search for documents |
| GET | `/stats` | Retrieve index statistics |
| GET | `/doc/{id}` | Retrieve a document by ID |

### Search Examples

**OR search**

```text
http://localhost:8000/search?query=python
```

Returns documents containing at least one query term.

**AND search**

```text
http://localhost:8000/search?query=python%20programming&mode=AND
```

Returns documents containing all query terms.

**Limit the number of results**

```text
http://localhost:8000/search?query=python&k=5
```

**Retrieve index statistics**

```text
http://localhost:8000/stats
```

**Retrieve a document**

```text
http://localhost:8000/doc/1479
```

For parameter details and response formats, refer to [API_CONTRACT.md](API_CONTRACT.md).

## Command-Line Interface

MiniSearch also provides a command-line interface.

| Command | Description |
|---|---|
| `python -m src.cli build` | Build and save the inverted index |
| `python -m src.cli search "python"` | Search the document collection |
| `python -m src.cli search "python programming" --mode AND` | Perform an AND search |
| `python -m src.cli stats` | Display index statistics |
| `python -m src.cli benchmark` | Run search performance benchmarks |
| `python -m src.cli analyze` | Run document-frequency analysis |

## Performance Benchmarking

The benchmark module measures search latency across multiple sample queries and repeated runs.

It reports:

- Average latency
- Median latency (p50)
- 95th-percentile latency (p95)
- Python version
- Operating system
- Number of indexed documents
- Vocabulary size

### Current Benchmark Results

The current benchmark was performed using the 2,500-document corpus.

**Environment:**
- Python version: 3.12.8
- Operating system: Windows 11
- Total documents: 2,500
- Vocabulary size: 2,423
- Queries tested: 8
- Runs per query: 20
- Total search runs: 160

**Overall results:**

| Metric | Result |
|---|---:|
| Average latency | 1.99 ms |
| Overall p50 | 0.281 ms |
| Overall p95 | 15.629 ms |

The typo-correction query (`pythn`) had a higher average latency of 14.001 ms because it requires additional candidate comparisons.

These measurements represent the tested 2,500-document dataset and environment.

## Document-Frequency Analysis

The analysis module reads queries from `analysis_queries.txt`, tokenizes them using the same tokenizer as the search engine, and examines document frequency across the indexed vocabulary.

It generates:

- `reports/term_frequency_analysis.csv`
- `reports/term_frequency_distribution.png`

The graph plots term rank against document frequency using logarithmic scales. NumPy is used to fit a trend line and calculate the R-squared value.

### Current Analysis Results

| Metric | Result |
|---|---:|
| Total unique indexed terms | 2,423 |
| Total queries | 12 |
| Total query terms | 19 |
| Trend-line slope | -1.2572 |
| R-squared | 0.9172 |

The negative slope indicates that document frequency generally decreases as term rank increases. The R-squared value indicates how closely the log-log data follows the fitted straight line.

## Testing

The project includes automated unit and API tests using Python's built-in `unittest` framework.

Run the complete test suite using:

```bash
python -m unittest discover -s tests -v
```

The latest recorded test run completed with **43 tests passing**.

## Current Development Status

The backend currently includes:

- Document loading
- Tokenization
- Inverted-index construction
- JSON index storage
- OR and AND search
- Result ranking and pagination
- Basic typo correction
- Search snippets
- Search, statistics, and document API endpoints
- CLI commands
- Performance benchmarking
- Document-frequency analysis
- Automated tests

The frontend is being developed separately by the other team member. Frontend-backend API integration and final end-to-end testing are the next development steps.

## Project Constraints

The search engine is implemented from scratch using Python rather than relying on existing full-text search engines such as Elasticsearch, Apache Lucene, or Whoosh.

The current implementation uses a local text corpus and a JSON-based inverted index.

## Team

MiniSearch is being developed by a two-member team as part of the Polaris School of Technology OJT programme.

- **Backend:** Python search engine, indexing, API, CLI, benchmarking, and analysis.
- **Frontend:** User interface and integration with the backend API.
