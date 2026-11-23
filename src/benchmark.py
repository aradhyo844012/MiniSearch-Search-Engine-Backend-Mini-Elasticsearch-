
import platform
import statistics
import sys
import time

from src.document_loader import load_documents
from src.index_storage import INDEX_PATH, load_index
from src.search_engine import search


# Representative queries for the first benchmark.
TEST_QUERIES = [
    "python",
    "search engine",
    "error handling",
    "programming",
    "data structures",
    "pythn",
    "machine learning",
    "algorithm"
]

# Number of times each query will be executed.
RUNS_PER_QUERY = 20


def percentile(values, percentile_value):
    """Return the requested percentile from sorted values."""
    sorted_values = sorted(values)

    position = (percentile_value / 100) * (len(sorted_values) - 1)
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(sorted_values) - 1)

    if lower_index == upper_index:
        return sorted_values[lower_index]

    fraction = position - lower_index

    return (
        sorted_values[lower_index] * (1 - fraction)
        + sorted_values[upper_index] * fraction
    )


def run_benchmark():
    if not INDEX_PATH.exists():
        print("Error: Index not found. Run the build command first.")
        return

    print("Loading index and documents...")

    inverted_index, document_frequency, document_lengths = load_index()
    documents = load_documents()

    documents_by_id = {
        document["doc_id"]: document
        for document in documents
    }

    all_latencies = []

    print("\nMiniSearch Benchmark")
    print("====================")
    print("Python version:", sys.version.split()[0])
    print("Operating system:", platform.platform())
    print("Total documents:", len(documents))
    print("Vocabulary size:", len(inverted_index))
    print("Queries:", len(TEST_QUERIES))
    print("Runs per query:", RUNS_PER_QUERY)

    for query in TEST_QUERIES:
        latencies = []

        for _ in range(RUNS_PER_QUERY):
            start_time = time.perf_counter()

            search(
                query=query,
                inverted_index=inverted_index,
                document_lengths=document_lengths,
                documents_by_id=documents_by_id,
                document_frequency=document_frequency,
                mode="OR",
                k=10,
                offset=0
            )

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            latencies.append(elapsed_ms)

        all_latencies.extend(latencies)

        print("\nQuery:", query)
        print("Average latency:", round(statistics.mean(latencies), 3), "ms")
        print("p50 latency:", round(percentile(latencies, 50), 3), "ms")
        print("p95 latency:", round(percentile(latencies, 95), 3), "ms")

    print("\nOverall Results")
    print("================")
    print("Total search runs:", len(all_latencies))
    print("Average latency:", round(statistics.mean(all_latencies), 3), "ms")
    print("Overall p50:", round(percentile(all_latencies, 50), 3), "ms")
    print("Overall p95:", round(percentile(all_latencies, 95), 3), "ms")


if __name__ == "__main__":
    run_benchmark()
