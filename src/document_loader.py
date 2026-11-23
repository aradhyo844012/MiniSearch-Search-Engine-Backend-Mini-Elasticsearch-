
import csv
from pathlib import Path


# Find the main project directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Define the locations of our dataset.
DATA_DIR = PROJECT_ROOT / "data"
CORPUS_DIR = DATA_DIR / "corpus"
MANIFEST_PATH = DATA_DIR / "manifest.csv"


def load_documents():
    """
    Read document information from the manifest
    and load the contents of each text file.
    """

    documents = []

    with open(MANIFEST_PATH, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            doc_id = row["doc_id"]
            filename = row["filename"]
            title = row["title"]

            file_path = CORPUS_DIR / filename

            with open(file_path, "r", encoding="utf-8") as text_file:
                content = text_file.read()

            document = {
                "doc_id": doc_id,
                "title": title,
                "filename": filename,
                "category": row["category"],
                "doc_type": row["doc_type"],
                "word_count": int(row["word_count"]),
                "content": content
            }

            documents.append(document)

    return documents


if __name__ == "__main__":
    documents = load_documents()

    print("Documents loaded successfully!")
    print("Total documents:", len(documents))

    if documents:
        print("\nFirst document:")
        print("ID:", documents[0]["doc_id"])
        print("Title:", documents[0]["title"])
        print("Content preview:", documents[0]["content"][:200]) 
