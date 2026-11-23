
import unittest

from src.index_builder import build_inverted_index


class TestIndexBuilder(unittest.TestCase):

    def setUp(self):
        self.documents = [
            {
                "doc_id": "1",
                "content": "python python programming"
            },
            {
                "doc_id": "2",
                "content": "python search"
            }
        ]

    def test_inverted_index_creation(self):
        inverted_index, document_frequency, document_lengths = (
            build_inverted_index(self.documents)
        )

        self.assertEqual(
            inverted_index["python"],
            {"1": 2, "2": 1}
        )

        self.assertEqual(
            inverted_index["programming"],
            {"1": 1}
        )

        self.assertEqual(
            inverted_index["search"],
            {"2": 1}
        )

    def test_document_frequency(self):
        _, document_frequency, _ = build_inverted_index(
            self.documents
        )

        self.assertEqual(document_frequency["python"], 2)
        self.assertEqual(document_frequency["programming"], 1)
        self.assertEqual(document_frequency["search"], 1)

    def test_document_lengths(self):
        _, _, document_lengths = build_inverted_index(
            self.documents
        )

        self.assertEqual(document_lengths["1"], 3)
        self.assertEqual(document_lengths["2"], 2)

    def test_vocabulary_size(self):
        inverted_index, _, _ = build_inverted_index(
            self.documents
        )

        self.assertEqual(len(inverted_index), 3)


if __name__ == "__main__":
    unittest.main()
