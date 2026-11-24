
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from src.document_loader import load_documents
from src.index_storage import INDEX_PATH, load_index, load_index_metadata
from src.search_engine import search


INVERTED_INDEX = {}
DOCUMENT_FREQUENCY = {}
DOCUMENT_LENGTHS = {}
DOCUMENTS_BY_ID = {}


class MiniSearchHandler(BaseHTTPRequestHandler):

    def send_json(self, status_code, data):
        response = json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(status_code)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def send_error_json(self, status_code, code, message):
        self.send_json(
            status_code,
            {
                "error": {
                    "code": code,
                    "message": message
                }
            }
        )

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        parameters = parse_qs(
            parsed_url.query,
            keep_blank_values=True
        )

        try:
            if path == "/search":
                self.handle_search(parameters)

            elif path == "/stats":
                self.handle_stats()

            elif path.startswith("/doc/"):
                doc_id = path[len("/doc/"):]
                self.handle_document(doc_id)

            elif path == "/":
                self.send_json(
                    200,
                    {
                        "message": "MiniSearch API is running",
                        "endpoints": [
                            "/search?query=python",
                            "/stats",
                            "/doc/1479"
                        ]
                    }
                )

            else:
                self.send_error_json(
                    404,
                    "ENDPOINT_NOT_FOUND",
                    "The requested endpoint does not exist."
                )

        except Exception:
            self.send_error_json(
                500,
                "INTERNAL_SERVER_ERROR",
                "An unexpected server error occurred."
            )

    def handle_search(self, parameters):
        query = parameters.get("query", [""])[0]
        mode = parameters.get("mode", ["OR"])[0]

        try:
            k = int(parameters.get("k", ["10"])[0])
            offset = int(parameters.get("offset", ["0"])[0])

        except ValueError:
            self.send_error_json(
                400,
                "INVALID_PARAMETER",
                "k and offset must be integers."
            )
            return

        if mode.upper() not in ("OR", "AND"):
            self.send_error_json(
                400,
                "INVALID_PARAMETER",
                "mode must be OR or AND."
            )
            return

        try:
            response = search(
                query=query,
                inverted_index=INVERTED_INDEX,
                document_lengths=DOCUMENT_LENGTHS,
                documents_by_id=DOCUMENTS_BY_ID,
                document_frequency=DOCUMENT_FREQUENCY,
                mode=mode,
                k=k,
                offset=offset
            )

            self.send_json(200, response)

        except ValueError as error:
            message = str(error)

            if "query" in message.lower():
                code = "INVALID_QUERY"
            else:
                code = "INVALID_PARAMETER"

            self.send_error_json(
                400,
                code,
                message
            )

    def handle_stats(self):
        try:
            index_size = INDEX_PATH.stat().st_size
            metadata = load_index_metadata()

            self.send_json(
                200,
                {
                    "totalDocuments": len(DOCUMENT_LENGTHS),
                    "vocabularySize": len(INVERTED_INDEX),
                    "indexSizeBytes": index_size,
                    "buildTimeMs": metadata["buildTimeMs"],
                    "builtAt": metadata["builtAt"]
                }
            )

        except (OSError, KeyError, ValueError):
            self.send_error_json(
                503,
                "INDEX_NOT_READY",
                "The search index or its metadata is not available."
            )

    def handle_document(self, doc_id):
        document = DOCUMENTS_BY_ID.get(doc_id)

        if document is None:
            self.send_error_json(
                404,
                "DOCUMENT_NOT_FOUND",
                "The requested document was not found."
            )
            return

        self.send_json(
            200,
            {
                "docId": document["doc_id"],
                "title": document["title"],
                "content": document["content"]
            }
        )


def start_server():
    global INVERTED_INDEX
    global DOCUMENT_FREQUENCY
    global DOCUMENT_LENGTHS
    global DOCUMENTS_BY_ID

    if not INDEX_PATH.exists():
        print("Error: Search index not found.")
        print("Run the index-building process first.")
        return

    INVERTED_INDEX, DOCUMENT_FREQUENCY, DOCUMENT_LENGTHS = load_index()

    documents = load_documents()

    DOCUMENTS_BY_ID = {
        document["doc_id"]: document
        for document in documents
    }

    server_address = ("localhost", 8000)

    server = ThreadingHTTPServer(
        server_address,
        MiniSearchHandler
    )

    print("MiniSearch API server is running!")
    print("Open: http://localhost:8000")
    print("Press Ctrl+C to stop the server.")

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\nStopping MiniSearch API server...")

    finally:
        server.server_close()


if __name__ == "__main__":
    start_server()
