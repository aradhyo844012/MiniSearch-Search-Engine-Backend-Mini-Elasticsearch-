
import argparse
import time
from datetime import datetime, timezone

from src.document_loader import load_documents
from src.index_builder import build_inverted_index
from src.index_storage import (
    INDEX_PATH,
    load_index,
    load_index_metadata,
    save_index
)
from src.search_engine import search
from src.benchmark import run_benchmark
from src.analyze import analyze_queries


def build_command():
    print("Loading documents...")

    documents = load_documents()
    print("Documents loaded:", len(documents))

    print("\nBuilding inverted index...")

    start_time = time.perf_counter()

    inverted_index, document_frequency, document_lengths = (
        build_inverted_index(documents)
    )

    build_time_ms = (time.perf_counter() - start_time) * 1000
    built_at = datetime.now(timezone.utc).isoformat()

    save_index(
        inverted_index,
        document_frequency,
        document_lengths,
        build_time_ms,
        built_at
    )

    print("\nIndex building completed!")
    print("Total documents:", len(document_lengths))
    print("Vocabulary size:", len(inverted_index))
    print("Build time:", round(build_time_ms, 3), "ms")


def search_command(query, mode, k, offset):
    if not INDEX_PATH.exists():
        print("Error: Index not found. Run the build command first.")
        return

    inverted_index, document_frequency, document_lengths = load_index()

    documents = load_documents()

    documents_by_id = {
        document["doc_id"]: document
        for document in documents
    }

    try:
        response = search(
            query=query,
            inverted_index=inverted_index,
            document_lengths=document_lengths,
            documents_by_id=documents_by_id,
            document_frequency=document_frequency,
            mode=mode,
            k=k,
            offset=offset
        )
    except ValueError as error:
        print("Error:", error)
        return

    print("\nSearch Results")
    print("======================")
    print("Original query:", response["query"])
    print("Corrected query:", response["correctedQuery"])
    print("Mode:", response["mode"])
    print("Total hits:", response["totalHits"])
    print("Latency:", response["latencyMs"], "ms")

    if not response["results"]:
        print("\nNo matching documents found.")
        return

    for result in response["results"]:
        print("\nDocument ID:", result["docId"])
        print("Title:", result["title"])
        print("Score:", result["score"])
        print("Matched terms:", result["matchedTerms"])
        print("Snippet:", result["snippet"])
        print("----------------------")


def stats_command():
    if not INDEX_PATH.exists():
        print("Error: Index not found. Run the build command first.")
        return

    inverted_index, document_frequency, document_lengths = load_index()
    metadata = load_index_metadata()

    print("\nMiniSearch Index Statistics")
    print("===========================")
    print("Total documents:", len(document_lengths))
    print("Vocabulary size:", len(inverted_index))
    print("Index size:", INDEX_PATH.stat().st_size, "bytes")
    print("Build time:", metadata["buildTimeMs"], "ms")
    print("Built at:", metadata["builtAt"])


def main():
    parser = argparse.ArgumentParser(
        description="MiniSearch Command-Line Interface"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # Build command
    subparsers.add_parser(
        "build",
        help="Build and save the search index"
    )

    # Search command
    search_parser = subparsers.add_parser(
        "search",
        help="Search the document collection"
    )

    search_parser.add_argument(
        "query",
        help="Words to search for"
    )

    search_parser.add_argument(
        "--mode",
        choices=["OR", "AND"],
        default="OR",
        help="Search mode"
    )

    search_parser.add_argument(
        "--k",
        type=int,
        default=10,
        help="Maximum number of results"
    )

    search_parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Number of results to skip"
    )

    # Stats command
    subparsers.add_parser(
        "stats",
        help="Display index statistics"
    )

    # Benchmark command
    subparsers.add_parser(
        "benchmark",
        help="Measure search performance"
    )

    # Analysis command
    subparsers.add_parser(
        "analyze",
        help="Analyze the document collection"
    )

    args = parser.parse_args()

    if args.command == "build":
        build_command()

    elif args.command == "search":
        search_command(
            args.query,
            args.mode,
            args.k,
            args.offset
        )

    elif args.command == "stats":
        stats_command()

    elif args.command == "benchmark":
        run_benchmark()

    elif args.command == "analyze":
        analyze_queries()


if __name__ == "__main__":
    main()
