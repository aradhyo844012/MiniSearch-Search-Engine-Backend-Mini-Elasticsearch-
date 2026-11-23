
import json
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = PROJECT_ROOT / "data" / "index.json"


def save_index(
    inverted_index,
    document_frequency,
    document_lengths,
    build_time_ms=None,
    built_at=None
):
    index_data = {
        "inverted_index": inverted_index,
        "document_frequency": document_frequency,
        "document_lengths": document_lengths,
        "build_time_ms": build_time_ms,
        "built_at": built_at
    }

    with open(INDEX_PATH, "w", encoding="utf-8") as file:
        json.dump(index_data, file, ensure_ascii=False)

    print("Index saved successfully!")


def load_index():
    with open(INDEX_PATH, "r", encoding="utf-8") as file:
        index_data = json.load(file)

    return (
        index_data["inverted_index"],
        index_data["document_frequency"],
        index_data["document_lengths"]
    )


def load_index_metadata():
    with open(INDEX_PATH, "r", encoding="utf-8") as file:
        index_data = json.load(file)

    return {
        "buildTimeMs": index_data.get("build_time_ms"),
        "builtAt": index_data.get("built_at")
    }


from src.document_loader import load_documents
from src.index_builder import build_inverted_index


if __name__ == "__main__":
    documents = load_documents()

    # Measure only the time spent building the inverted index.
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

    loaded_index, loaded_frequency, loaded_lengths = load_index()

    print("\nIndex loaded successfully!")
    print("Vocabulary size:", len(loaded_index))
    print("Total documents:", len(loaded_lengths))
    print("Build time:", round(build_time_ms, 3), "ms")
    print("Built at:", built_at)
    print(
        "Original and loaded index match:",
        inverted_index == loaded_index
    )
