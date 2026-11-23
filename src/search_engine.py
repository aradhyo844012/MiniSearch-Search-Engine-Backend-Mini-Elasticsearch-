
import heapq
import time

from src.index_storage import load_index
from src.tokenizer import tokenize
from src.document_loader import load_documents
from src.typo_corrector import correct_query


def find_matching_documents(query_tokens, inverted_index, mode="OR"):
    matching_documents = set()

    if mode == "OR":
        for token in query_tokens:
            postings = inverted_index.get(token, {})
            matching_documents.update(postings.keys())

    elif mode == "AND":
        for position, token in enumerate(query_tokens):
            postings = inverted_index.get(token, {})
            current_documents = set(postings.keys())

            if position == 0:
                matching_documents = current_documents
            else:
                matching_documents.intersection_update(current_documents)

    else:
        raise ValueError("Mode must be OR or AND")

    return matching_documents


def calculate_scores(query_tokens, matching_documents, inverted_index):
    scores = {}

    unique_tokens = list(dict.fromkeys(query_tokens))

    for doc_id in matching_documents:
        score = 0

        for token in unique_tokens:
            postings = inverted_index.get(token, {})
            score += postings.get(doc_id, 0)

        scores[doc_id] = score

    return scores


def rank_documents(scores, document_lengths, k=10, offset=0):
    ranked_documents = heapq.nsmallest(
        offset + k,
        scores.keys(),
        key=lambda doc_id: (
            -scores[doc_id],
            document_lengths[doc_id],
            int(doc_id)
        )
    )

    return ranked_documents


def paginate_results(ranked_documents, k=10, offset=0):
    return ranked_documents[offset:offset + k]


def get_matched_terms(query_tokens, doc_id, inverted_index):
    matched_terms = []

    unique_tokens = list(dict.fromkeys(query_tokens))

    for token in unique_tokens:
        postings = inverted_index.get(token, {})

        if doc_id in postings:
            matched_terms.append(token)

    return matched_terms



def generate_snippet(content, matched_terms, context_length=100):
    if not matched_terms:
        return content[:context_length]

    lower_content = content.lower()
    first_position = -1

    for term in matched_terms:
        term = term.lower()
        search_position = 0

        while True:
            position = lower_content.find(term, search_position)

            if position == -1:
                break

            end_position = position + len(term)

            # Check whether the match starts at a word boundary.
            starts_at_boundary = (
                position == 0
                or not lower_content[position - 1].isalnum()
            )

            # Check whether the match ends at a word boundary.
            ends_at_boundary = (
                end_position == len(lower_content)
                or not lower_content[end_position].isalnum()
            )

            if starts_at_boundary and ends_at_boundary:
                if first_position == -1 or position < first_position:
                    first_position = position
                break

            search_position = position + 1

    if first_position == -1:
        return content[:context_length]

    start = max(0, first_position - context_length // 2)
    end = min(len(content), first_position + context_length)

    snippet = content[start:end].strip()

    if start > 0:
        snippet = "..." + snippet

    if end < len(content):
        snippet = snippet + "..."

    return snippet



def create_search_results(
    ranked_documents,
    scores,
    query_tokens,
    inverted_index,
    documents_by_id
):
    search_results = []

    for doc_id in ranked_documents:
        document = documents_by_id[doc_id]

        matched_terms = get_matched_terms(
            query_tokens,
            doc_id,
            inverted_index
        )

        snippet = generate_snippet(
            document["content"],
            matched_terms
        )

        result = {
            "docId": doc_id,
            "title": document["title"],
            "score": scores[doc_id],
            "snippet": snippet,
            "matchedTerms": matched_terms
        }

        search_results.append(result)

    return search_results


def search(
    query,
    inverted_index,
    document_lengths,
    documents_by_id,
    document_frequency=None,
    mode="OR",
    k=10,
    offset=0
):
    start_time = time.perf_counter()

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Search query cannot be empty")

    if not isinstance(mode, str):
        raise ValueError("Mode must be OR or AND")

    mode = mode.upper()

    if mode not in ("OR", "AND"):
        raise ValueError("Mode must be OR or AND")

    if not isinstance(k, int) or isinstance(k, bool) or not 1 <= k <= 100:
        raise ValueError("k must be between 1 and 100")

    if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
        raise ValueError("offset must be a non-negative integer")

    original_tokens = tokenize(query)

    if not original_tokens:
        raise ValueError("Search query must contain searchable words")

    if document_frequency is None:
        document_frequency = {}

    # Correct missing or rare query terms.
    query_tokens, corrected_query = correct_query(
        original_tokens,
        document_frequency
    )

    # Search using the corrected tokens.
    matching_documents = find_matching_documents(
        query_tokens,
        inverted_index,
        mode
    )

    scores = calculate_scores(
        query_tokens,
        matching_documents,
        inverted_index
    )

    total_hits = len(matching_documents)

    ranked_documents = rank_documents(
        scores,
        document_lengths,
        k,
        offset
    )

    paginated_documents = paginate_results(
        ranked_documents,
        k,
        offset
    )

    results = create_search_results(
        paginated_documents,
        scores,
        query_tokens,
        inverted_index,
        documents_by_id
    )

    latency_ms = (time.perf_counter() - start_time) * 1000

    return {
        "query": query,
        "mode": mode,
        "k": k,
        "offset": offset,
        "totalHits": total_hits,
        "correctedQuery": corrected_query,
        "latencyMs": round(latency_ms, 3),
        "results": results
    }


if __name__ == "__main__":
    inverted_index, document_frequency, document_lengths = load_index()

    documents = load_documents()

    documents_by_id = {
        document["doc_id"]: document
        for document in documents
    }

    # TEST 1: Normal AND-mode search
    print("\nTEST 1: AND-MODE SEARCH")
    print("=======================")

    search_response = search(
        query="python programming",
        inverted_index=inverted_index,
        document_lengths=document_lengths,
        documents_by_id=documents_by_id,
        document_frequency=document_frequency,
        mode="AND",
        k=5,
        offset=10
    )

    print("Query:", search_response["query"])
    print("Corrected query:", search_response["correctedQuery"])
    print("Mode:", search_response["mode"])
    print("Total hits:", search_response["totalHits"])
    print("Latency:", search_response["latencyMs"], "ms")

    print("\nSearch results:")

    for result in search_response["results"]:
        print("\n", result)

    # TEST 2: Typo correction
    print("\n\nTEST 2: TYPO CORRECTION")
    print("=======================")

    typo_response = search(
        query="pythn",
        inverted_index=inverted_index,
        document_lengths=document_lengths,
        documents_by_id=documents_by_id,
        document_frequency=document_frequency,
        k=5
    )

    print("Original query:", typo_response["query"])
    print("Corrected query:", typo_response["correctedQuery"])
    print("Total hits:", typo_response["totalHits"])

    for result in typo_response["results"]:
        print("\n", result)

    # TEST 3: Unknown words
    print("\n\nTEST 3: UNKNOWN WORDS")
    print("=====================")

    unknown_response = search(
        query="xyzabc",
        inverted_index=inverted_index,
        document_lengths=document_lengths,
        documents_by_id=documents_by_id,
        document_frequency=document_frequency
    )

    print("Original query:", unknown_response["query"])
    print("Corrected query:", unknown_response["correctedQuery"])
    print("Total hits:", unknown_response["totalHits"])

    # TEST 4: Empty query
    print("\n\nTEST 4: EMPTY QUERY")
    print("===================")

    try:
        search(
            query="",
            inverted_index=inverted_index,
            document_lengths=document_lengths,
            documents_by_id=documents_by_id,
            document_frequency=document_frequency
        )
    except ValueError as error:
        print("Validation error:", error)

    # TEST 5: Whitespace-only query
    print("\n\nTEST 5: WHITESPACE-ONLY QUERY")
    print("=============================")

    try:
        search(
            query="   ",
            inverted_index=inverted_index,
            document_lengths=document_lengths,
            documents_by_id=documents_by_id,
            document_frequency=document_frequency
        )
    except ValueError as error:
        print("Validation error:", error) 
