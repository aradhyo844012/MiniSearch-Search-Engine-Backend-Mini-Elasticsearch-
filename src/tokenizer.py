
def tokenize(text):
    """
    Convert text into lowercase tokens.

    Non-alphanumeric characters act as separators.
    """

    tokens = []
    current_word = ""

    for character in text:
        if character.isalnum():
            current_word += character.lower()

        else:
            if current_word:
                tokens.append(current_word)
                current_word = ""

    # Add the final word if the text doesn't end with a separator.
    if current_word:
        tokens.append(current_word)

    return tokens



if __name__ == "__main__":

    test_cases = [
        "Python is AMAZING!",
        "Hello, World! How are you?",
        "Python123 is version 3.12",
        "   multiple     spaces   ",
        "",
        "Error-handling and file_reading"
    ]

    for text in test_cases:
        print("\nInput:", repr(text))
        print("Output:", tokenize(text))
