
import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from src import api_server


class TestMiniSearchAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Prepare a small test index and document collection.
        api_server.INVERTED_INDEX = {
            "python": {"1": 2, "2": 1},
            "programming": {"1": 1}
        }

        api_server.DOCUMENT_FREQUENCY = {
            "python": 2,
            "programming": 1
        }

        api_server.DOCUMENT_LENGTHS = {
            "1": 3,
            "2": 2
        }

        api_server.DOCUMENTS_BY_ID = {
            "1": {
                "doc_id": "1",
                "title": "Python Programming",
                "content": "Python Python Programming"
            },
            "2": {
                "doc_id": "2",
                "title": "Python Basics",
                "content": "Python Basics"
            }
        }

        # Create a temporary index file for the stats endpoint.
        cls.temp_directory = tempfile.TemporaryDirectory()
        cls.index_path = Path(cls.temp_directory.name) / "index.json"
        cls.index_path.write_text("{}", encoding="utf-8")

        cls.index_path_patch = patch.object(
            api_server,
            "INDEX_PATH",
            cls.index_path
        )

        cls.metadata_patch = patch.object(
            api_server,
            "load_index_metadata",
            return_value={
                "buildTimeMs": 12.5,
                "builtAt": "2026-11-23T10:00:00+00:00"
            }
        )

        cls.index_path_patch.start()
        cls.metadata_patch.start()

        # Start the test server on an available local port.
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0),
            api_server.MiniSearchHandler
        )

        cls.server_thread = threading.Thread(
            target=cls.server.serve_forever,
            daemon=True
        )

        cls.server_thread.start()

        cls.base_url = (
            f"http://127.0.0.1:{cls.server.server_port}"
        )

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.server_thread.join()

        cls.index_path_patch.stop()
        cls.metadata_patch.stop()
        cls.temp_directory.cleanup()

    def make_request(self, path):
        url = self.base_url + path

        try:
            with urlopen(url) as response:
                body = json.loads(
                    response.read().decode("utf-8")
                )
                return response.status, body

        except HTTPError as error:
            body = json.loads(
                error.read().decode("utf-8")
            )
            return error.code, body

    # -------------------------
    # Successful API requests
    # -------------------------

    def test_root_endpoint(self):
        status, body = self.make_request("/")

        self.assertEqual(status, 200)
        self.assertEqual(
            body["message"],
            "MiniSearch API is running"
        )

    def test_search_endpoint(self):
        status, body = self.make_request(
            "/search?query=python"
        )

        self.assertEqual(status, 200)
        self.assertEqual(body["totalHits"], 2)
        self.assertEqual(len(body["results"]), 2)

    def test_lowercase_search_mode(self):
        status, body = self.make_request(
            "/search?query=python&mode=or"
        )

        self.assertEqual(status, 200)
        self.assertEqual(body["mode"], "OR")

    def test_stats_endpoint(self):
        status, body = self.make_request("/stats")

        self.assertEqual(status, 200)
        self.assertEqual(body["totalDocuments"], 2)
        self.assertEqual(body["vocabularySize"], 2)
        self.assertEqual(body["indexSizeBytes"], 2)

    def test_document_endpoint(self):
        status, body = self.make_request("/doc/1")

        self.assertEqual(status, 200)
        self.assertEqual(body["docId"], "1")
        self.assertEqual(
            body["title"],
            "Python Programming"
        )

    # -------------------------
    # Invalid request handling
    # -------------------------

    def test_missing_query(self):
        status, body = self.make_request("/search")

        self.assertEqual(status, 400)
        self.assertEqual(
            body["error"]["code"],
            "INVALID_QUERY"
        )

    def test_invalid_search_parameter(self):
        status, body = self.make_request(
            "/search?query=python&k=0"
        )

        self.assertEqual(status, 400)
        self.assertEqual(
            body["error"]["code"],
            "INVALID_PARAMETER"
        )

    def test_non_integer_k(self):
        status, body = self.make_request(
            "/search?query=python&k=abc"
        )

        self.assertEqual(status, 400)
        self.assertEqual(
            body["error"]["code"],
            "INVALID_PARAMETER"
        )

    def test_non_integer_offset(self):
        status, body = self.make_request(
            "/search?query=python&offset=abc"
        )

        self.assertEqual(status, 400)
        self.assertEqual(
            body["error"]["code"],
            "INVALID_PARAMETER"
        )

    def test_negative_offset(self):
        status, body = self.make_request(
            "/search?query=python&offset=-1"
        )

        self.assertEqual(status, 400)
        self.assertEqual(
            body["error"]["code"],
            "INVALID_PARAMETER"
        )

    def test_invalid_mode(self):
        status, body = self.make_request(
            "/search?query=python&mode=XYZ"
        )

        self.assertEqual(status, 400)
        self.assertEqual(
            body["error"]["code"],
            "INVALID_PARAMETER"
        )

    # -------------------------
    # Not found handling
    # -------------------------

    def test_missing_document(self):
        status, body = self.make_request("/doc/999")

        self.assertEqual(status, 404)
        self.assertEqual(
            body["error"]["code"],
            "DOCUMENT_NOT_FOUND"
        )

    def test_unknown_endpoint(self):
        status, body = self.make_request("/unknown")

        self.assertEqual(status, 404)
        self.assertEqual(
            body["error"]["code"],
            "ENDPOINT_NOT_FOUND"
        )


if __name__ == "__main__":
    unittest.main()
