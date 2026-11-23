
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.index_storage import INDEX_PATH, load_index
from src.tokenizer import tokenize


PROJECT_ROOT = Path(__file__).resolve().parent.parent
QUERY_FILE = PROJECT_ROOT / "analysis_queries.txt"
REPORTS_DIR = PROJECT_ROOT / "reports"


def load_queries():
    """Load one search query per line from the input file."""
    if not QUERY_FILE.exists():
        raise FileNotFoundError(
            "analysis_queries.txt was not found in the project root."
        )

    query_data = pd.read_csv(
        QUERY_FILE,
        header=None,
        names=["query"],
        encoding="utf-8"
    )

    return query_data["query"].dropna().astype(str).tolist()


def analyze_queries():
    if not INDEX_PATH.exists():
        print("Error: Index not found. Run the build command first.")
        return

    print("Loading queries and search index...")

    queries = load_queries()

    inverted_index, document_frequency, document_lengths = load_index()

    if not queries:
        print("Error: No queries found in analysis_queries.txt.")
        return

    # Tokenize every query using MiniSearch's tokenizer.
    query_terms = []

    for query in queries:
        query_terms.extend(tokenize(query))

    if not query_terms:
        print("Error: No searchable terms found in the query file.")
        return

    # Count how frequently each term appears in the sample queries.
    query_frequency = Counter(query_terms)

    # Find the 10 most frequent query terms.
    top_query_terms = query_frequency.most_common(10)

    # Sort the complete vocabulary by document frequency.
    sorted_terms = sorted(
        document_frequency.items(),
        key=lambda item: (-item[1], item[0])
    )

    # Prepare data for the CSV report.
    report_data = []

    for rank, (term, frequency) in enumerate(sorted_terms, start=1):
        report_data.append({
            "rank": rank,
            "term": term,
            "document_frequency": frequency,
            "query_frequency": query_frequency.get(term, 0)
        })

    report_df = pd.DataFrame(report_data)

    # Create the reports directory if it does not exist.
    REPORTS_DIR.mkdir(exist_ok=True)

    csv_path = REPORTS_DIR / "term_frequency_analysis.csv"
    graph_path = REPORTS_DIR / "term_frequency_distribution.png"

    report_df.to_csv(csv_path, index=False, encoding="utf-8")

    # Prepare the top 10 query terms for display.
    print("\nTop 10 Query Terms")
    print("==================")

    for term, frequency in top_query_terms:
        df = document_frequency.get(term, 0)

        print(
            f"{term:<20} "
            f"Query frequency: {frequency:<5} "
            f"Document frequency: {df}"
        )

    # Prepare rank and document-frequency values for the graph.
    ranks = np.array(
        [row["rank"] for row in report_data],
        dtype=float
    )

    frequencies = np.array(
        [row["document_frequency"] for row in report_data],
        dtype=float
    )

    # Use logarithms to fit a straight line to the log-log data.
    log_ranks = np.log10(ranks)
    log_frequencies = np.log10(frequencies)

    slope, intercept = np.polyfit(
        log_ranks,
        log_frequencies,
        1
    )

    predicted_values = slope * log_ranks + intercept

    # Calculate R-squared to measure how well the line fits.
    residual_sum = np.sum(
        (log_frequencies - predicted_values) ** 2
    )

    total_sum = np.sum(
        (log_frequencies - np.mean(log_frequencies)) ** 2
    )

    r_squared = 1 - (residual_sum / total_sum)

    # Generate the log-log graph.
    plt.figure(figsize=(10, 6))

    plt.loglog(
        ranks,
        frequencies,
        marker=".",
        linestyle="none",
        markersize=4,
        label="Document frequency"
    )

    plt.loglog(
        ranks,
        10 ** predicted_values,
        linestyle="-",
        label="Linear trend"
    )

    plt.xlabel("Term Rank (log scale)")
    plt.ylabel("Document Frequency (log scale)")
    plt.title("MiniSearch: Document Frequency vs Term Rank")
    plt.legend()
    plt.grid(True, which="both", alpha=0.3)
    plt.tight_layout()

    plt.savefig(graph_path, dpi=300)
    plt.close()

    # Print analysis summary.
    print("\nVocabulary Analysis")
    print("===================")
    print("Total unique terms:", len(document_frequency))
    print("Total queries:", len(queries))
    print("Total query terms:", len(query_terms))
    print("Trend-line slope:", round(float(slope), 4))
    print("R-squared:", round(float(r_squared), 4))

    print("\nInterpretation")
    print("==============")

    print(
        f"The document-frequency distribution has a fitted "
        f"log-log slope of {slope:.4f}. "
        f"The R-squared value is {r_squared:.4f}, indicating "
        f"how closely the log-log data follows a straight line."
    )

    print(
        "A negative slope means that document frequency generally "
        "decreases as term rank increases."
    )

    print("\nReports saved successfully!")
    print("CSV:", csv_path)
    print("Graph:", graph_path)


if __name__ == "__main__":
    analyze_queries()
