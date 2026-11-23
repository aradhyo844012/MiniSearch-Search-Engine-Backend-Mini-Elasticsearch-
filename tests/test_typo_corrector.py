
import unittest

from src.typo_corrector import edit_distance, correct_query


class TestTypoCorrector(unittest.TestCase):

    def setUp(self):
        self.document_frequency = {
            "python": 100,
            "programming": 80,
            "algorithm": 60,
            "search": 90,
            "engine": 70
        }

    def test_edit_distance(self):
        self.assertEqual(edit_distance("python", "pythn"), 1)

    def test_multiple_edit_operations(self):
        self.assertEqual(edit_distance("kitten", "sitting"), 3)

    def test_correct_python_typo(self):
        tokens, corrected_query = correct_query(
            ["pythn"],
            self.document_frequency
        )

        self.assertEqual(tokens, ["python"])
        self.assertEqual(corrected_query, "python")

    def test_correct_programming_typo(self):
        tokens, corrected_query = correct_query(
            ["programing"],
            self.document_frequency
        )

        self.assertEqual(tokens, ["programming"])
        self.assertEqual(corrected_query, "programming")

    def test_common_word_is_not_corrected(self):
        tokens, corrected_query = correct_query(
            ["python"],
            self.document_frequency
        )

        self.assertEqual(tokens, ["python"])
        self.assertIsNone(corrected_query)

    def test_unknown_word_remains_unchanged(self):
        tokens, corrected_query = correct_query(
            ["xyzabc"],
            self.document_frequency
        )

        self.assertEqual(tokens, ["xyzabc"])
        self.assertIsNone(corrected_query)

    def test_closest_candidate_is_preferred(self):
        frequency = {
            "python": 100,
            "pythonic": 50,
            "programming": 80
        }

        tokens, corrected_query = correct_query(
            ["pythn"],
            frequency
        )

        self.assertEqual(tokens, ["python"])
        self.assertEqual(corrected_query, "python")

    def test_higher_frequency_wins_equal_distance(self):
        frequency = {
            "cat": 100,
            "bat": 80
        }

        tokens, corrected_query = correct_query(
            ["hat"],
            frequency
        )

        self.assertEqual(tokens, ["cat"])
        self.assertEqual(corrected_query, "cat")

    def test_no_correction_when_no_candidate_is_close(self):
        frequency = {
            "python": 100,
            "programming": 80,
            "algorithm": 60
        }

        tokens, corrected_query = correct_query(
            ["zzzzzz"],
            frequency
        )

        self.assertEqual(tokens, ["zzzzzz"])
        self.assertIsNone(corrected_query)


if __name__ == "__main__":
    unittest.main()
