from src.document_loader import load_documents
from src.index_builder import build_inverted_index
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = PROJECT_ROOT / "data" / "index.json"


def save_index(inverted_index, document_frequency, document_lengths):
    index_data = {
        "inverted_index": inverted_index,
        "document_frequency": document_frequency,
        "document_lengths": document_lengths
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

if __name__ == "__main__":
    documents = load_documents()

    inverted_index, document_frequency, document_lengths = (
        build_inverted_index(documents)
    )

    save_index(
        inverted_index,
        document_frequency,
        document_lengths
    )

    loaded_index, loaded_frequency, loaded_lengths = load_index()

    print("\nIndex loaded successfully!")
    print("Vocabulary size:", len(loaded_index))
    print("Total documents:", len(loaded_lengths))

    print(
        "Original and loaded index match:",
        inverted_index == loaded_index
    )