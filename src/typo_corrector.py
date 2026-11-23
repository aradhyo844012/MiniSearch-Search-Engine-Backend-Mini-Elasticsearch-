
def edit_distance(word1, word2):
    """
    Calculate the minimum number of single-character
    insertions, deletions, and substitutions.
    """
    rows = len(word1) + 1
    columns = len(word2) + 1

    dp = []

    for row in range(rows):
        dp.append([0] * columns)

    for row in range(rows):
        dp[row][0] = row

    for column in range(columns):
        dp[0][column] = column

    for row in range(1, rows):
        for column in range(1, columns):
            if word1[row - 1] == word2[column - 1]:
                cost = 0
            else:
                cost = 1

            deletion = dp[row - 1][column] + 1
            insertion = dp[row][column - 1] + 1
            substitution = dp[row - 1][column - 1] + cost

            dp[row][column] = min(
                deletion,
                insertion,
                substitution
            )

    return dp[-1][-1]


def correct_query(query_tokens, document_frequency, rare_threshold=2):
    corrected_tokens = []

    for token in query_tokens:
        frequency = document_frequency.get(token, 0)

        if frequency > rare_threshold:
            corrected_tokens.append(token)
            continue

        if len(token) <= 4:
            max_distance = 1
        else:
            max_distance = 2

        best_candidate = token
        best_distance = max_distance + 1
        best_frequency = 0

        for candidate, candidate_frequency in document_frequency.items():
            if candidate == token:
                continue

            # Skip candidates whose lengths make a valid correction impossible.
            if abs(len(token) - len(candidate)) > max_distance:
                continue

            distance = edit_distance(token, candidate)

            if distance > max_distance:
                continue

            if (
                distance < best_distance
                or (
                    distance == best_distance
                    and candidate_frequency > best_frequency
                )
            ):
                best_candidate = candidate
                best_distance = distance
                best_frequency = candidate_frequency

        corrected_tokens.append(best_candidate)

    if corrected_tokens == query_tokens:
        return corrected_tokens, None

    corrected_query = " ".join(corrected_tokens)

    return corrected_tokens, corrected_query


if __name__ == "__main__":
    test_frequency = {
        "python": 394,
        "programming": 250,
        "algorithm": 180,
        "search": 300,
        "engine": 200,
        "apple": 40,
        "apply": 25
    }

    test_queries = [
        ["pythn"],
        ["programing"],
        ["algoritm"],
        ["python"],
        ["xyzabc"]
    ]

    for query_tokens in test_queries:
        corrected_tokens, corrected_query = correct_query(
            query_tokens,
            test_frequency
        )

        print("\nOriginal:", " ".join(query_tokens))
        print("Corrected:", corrected_query)
        print("Search tokens:", corrected_tokens)
