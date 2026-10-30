# MiniSearch-Search-Engine-Backend-Mini-Elasticsearch-
A Python-based mini search engine with an inverted index, ranked search, and analytics dashboard.


# Mini Elasticsearch — Search Engine Backend

A Python-based mini search engine that demonstrates how search engines retrieve, rank, and analyze documents using an *inverted index*, term-frequency scoring, and a web-based analytics dashboard.

## Overview

Mini Elasticsearch is a lightweight educational project inspired by search engine fundamentals. It indexes text documents, searches for matching terms, ranks relevant results, and presents search analytics through a web interface.

The project demonstrates core concepts used in information retrieval without requiring a full Elasticsearch installation.

## Features

- *Inverted Index:* Maps terms to the documents in which they appear.
- *Ranked Search:* Ranks matching documents using term-frequency-based scoring.
- *Web Interface:* Search documents and view results through a browser.
- *Result Snippets:* Displays contextual text from matching documents.
- *Index Rebuilding:* Rebuilds the index when documents change.
- *Search History:* Records search queries and exposes history through the API.
- *Analytics Dashboard:* Displays search statistics and visualizations.
- *Zipf's Law Visualization:* Plots term frequency against rank to explore word-frequency patterns.

## Technology Stack

- Python 3
- Flask
- HTML
- CSS
- JavaScript
- Matplotlib
- Collections and regular expressions for indexing and text processing
