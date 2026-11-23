
from collections import defaultdict

from src.document_loader import load_documents
from src.tokenizer import tokenize


def build_inverted_index(documents):
    """
    Build an inverted index from a collection of documents.

    Returns:
        inverted_index: term -> document ID -> term frequency
        document_frequency: term -> number of documents containing it
        document_lengths: document ID -> total number of tokens
    """

    inverted_index = defaultdict(dict)
    document_frequency = {}
    document_lengths = {}

    for document in documents:

        doc_id = document["doc_id"]
        content = document["content"]

        tokens = tokenize(content)

        # Store the total number of tokens in this document.
        document_lengths[doc_id] = len(tokens)

        # Count how many times each word occurs in this document.
        term_frequencies = {}

        for token in tokens:
            term_frequencies[token] = term_frequencies.get(token, 0) + 1

        # Add this document's term frequencies to the inverted index.
        for term, frequency in term_frequencies.items():
            inverted_index[term][doc_id] = frequency

            # Count how many documents contain this term.
            document_frequency[term] = (
                document_frequency.get(term, 0) + 1
            )

    return dict(inverted_index), document_frequency, document_lengths


if __name__ == "__main__":

    documents = load_documents()

    inverted_index, document_frequency, document_lengths = (
        build_inverted_index(documents)
    )

    print("Inverted index built successfully!")

    print("Total documents:", len(documents))
    print("Vocabulary size:", len(inverted_index))

    print("\nExample term: python")

    if "python" in inverted_index:
        print("Postings:", inverted_index["python"])
        print("Document frequency:", document_frequency["python"])
    else:
        print("The word 'python' was not found.")

    print("\nDocument length of first document:")
    first_doc_id = documents[0]["doc_id"]
    print(document_lengths[first_doc_id])
