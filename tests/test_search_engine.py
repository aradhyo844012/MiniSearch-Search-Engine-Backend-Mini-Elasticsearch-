
import unittest

from src.search_engine import search


class TestSearchEngine(unittest.TestCase):

    def setUp(self):
        self.inverted_index = {
            "python": {
                "1": 2,
                "2": 1,
                "3": 1
            },
            "programming": {
                "1": 1,
                "3": 1
            },
            "search": {
                "2": 2
            }
        }

        self.document_frequency = {
            "python": 3,
            "programming": 3,
            "search": 3
        }

        self.document_lengths = {
            "1": 10,
            "2": 5,
            "3": 8
        }

        self.documents_by_id = {
            "1": {
                "doc_id": "1",
                "title": "Python Programming",
                "content": "Python Python Programming"
            },
            "2": {
                "doc_id": "2",
                "title": "Python Search",
                "content": "Python Search Search"
            },
            "3": {
                "doc_id": "3",
                "title": "Programming with Python",
                "content": "Python Programming"
            }
        }

    def run_search(self, query, **kwargs):
        return search(
            query=query,
            inverted_index=self.inverted_index,
            document_lengths=self.document_lengths,
            documents_by_id=self.documents_by_id,
            document_frequency=self.document_frequency,
            **kwargs
        )

    def test_or_search(self):
        response = self.run_search("python")

        self.assertEqual(response["totalHits"], 3)
        self.assertEqual(
            [item["docId"] for item in response["results"]],
            ["1", "2", "3"]
        )

    def test_and_search(self):
        response = self.run_search(
            "python programming",
            mode="AND"
        )

        self.assertEqual(response["totalHits"], 2)
        self.assertEqual(
            [item["docId"] for item in response["results"]],
            ["1", "3"]
        )

    def test_term_frequency_ranking(self):
        response = self.run_search("python")

        self.assertEqual(
            response["results"][0]["docId"],
            "1"
        )

        self.assertEqual(
            response["results"][0]["score"],
            2
        )

    def test_document_length_tie_breaking(self):
        response = self.run_search("python")

        self.assertEqual(
            response["results"][1]["docId"],
            "2"
        )

        self.assertEqual(
            response["results"][2]["docId"],
            "3"
        )

    def test_pagination(self):
        response = self.run_search(
            "python",
            k=1,
            offset=1
        )

        self.assertEqual(response["totalHits"], 3)
        self.assertEqual(len(response["results"]), 1)
        self.assertEqual(response["results"][0]["docId"], "2")

    def test_matched_terms(self):
        response = self.run_search("python programming")

        first_result = response["results"][0]

        self.assertEqual(
            first_result["matchedTerms"],
            ["python", "programming"]
        )

    def test_invalid_query(self):
        with self.assertRaises(ValueError):
            self.run_search("")

    def test_invalid_mode(self):
        with self.assertRaises(ValueError):
            self.run_search("python", mode="INVALID")

    def test_invalid_k(self):
        with self.assertRaises(ValueError):
            self.run_search("python", k=0)

    def test_invalid_offset(self):
        with self.assertRaises(ValueError):
            self.run_search("python", offset=-1)


if __name__ == "__main__":
    unittest.main()
