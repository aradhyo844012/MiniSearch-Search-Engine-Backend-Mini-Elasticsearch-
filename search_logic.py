
# MiniSearch - Basic Search Engine Logic

# Sample documents
documents = [
    {
        "id": 1,
        "title": "Python Programming",
        "content": "Python is a popular programming language"
    },
    {
        "id": 2,
        "title": "Web Development",
        "content": "Web development uses HTML CSS and JavaScript"
    },
    {
        "id": 3,
        "title": "Search Engine",
        "content": "A search engine helps users find information"
    }
]


# Convert text into individual words
def tokenize(text):
    words = text.lower().split()
    return words


# Create an inverted index
def build_index(documents):
    index = {}

    for document in documents:
        words = tokenize(document["content"])
        doc_id = document["id"]

        for word in words:

            if word not in index:
                index[word] = {}

            if doc_id not in index[word]:
                index[word][doc_id] = 0

            index[word][doc_id] += 1

    return index


# Search for documents
def search(query, index, documents):
    query_words = tokenize(query)

    scores = {}

    for word in query_words:
        if word in index:

            for doc_id in index[word]:

                if doc_id not in scores:
                    scores[doc_id] = 0

                scores[doc_id] += index[word][doc_id]

    # Arrange matching documents by score
    results = []

    for document in documents:
        doc_id = document["id"]

        if doc_id in scores:
            results.append({
                "title": document["title"],
                "content": document["content"],
                "score": scores[doc_id]
            })

    results.sort(key=lambda x: x["score"], reverse=True)

    return results


# Build the index
inverted_index = build_index(documents)

# Try searching
query = input("Enter your search query: ")

results = search(query, inverted_index, documents)

# Display results
if len(results) == 0:
    print("No results found.")

else:
    for result in results:
        print("--------------------")
        print("Title:", result["title"])
        print("Score:", result["score"])
        print("Content:", result["content"])

