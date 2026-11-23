
import unittest

from src.tokenizer import tokenize


class TestTokenizer(unittest.TestCase):

    def test_lowercase_conversion(self):
        self.assertEqual(
            tokenize("PYTHON IS AMAZING"),
            ["python", "is", "amazing"]
        )

    def test_punctuation_removal(self):
        self.assertEqual(
            tokenize("Hello, World!"),
            ["hello", "world"]
        )

    def test_numbers(self):
        self.assertEqual(
            tokenize("Python123 version 3.12"),
            ["python123", "version", "3", "12"]
        )

    def test_multiple_spaces(self):
        self.assertEqual(
            tokenize("   hello     world   "),
            ["hello", "world"]
        )

    def test_empty_string(self):
        self.assertEqual(
            tokenize(""),
            []
        )

    def test_hyphens_and_underscores(self):
        self.assertEqual(
            tokenize("error-handling file_reading"),
            ["error", "handling", "file", "reading"]
        )

    def test_repeated_words(self):
        self.assertEqual(
            tokenize("python python search"),
            ["python", "python", "search"]
        )


if __name__ == "__main__":
    unittest.main()
