
import json
import mimetypes
import os

from pathlib import Path
from urllib.parse import parse_qs, urlparse, unquote
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from src.document_loader import load_documents
from src.index_storage import INDEX_PATH, load_index, load_index_metadata
from src.search_engine import search


# =========================================
# PROJECT PATHS
# =========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

STATIC_DIRECTORIES = {
    "css",
    "js",
    "assets",
    "reports"
}


# =========================================
# SEARCH ENGINE DATA
# =========================================

INVERTED_INDEX = {}
DOCUMENT_FREQUENCY = {}
DOCUMENT_LENGTHS = {}
DOCUMENTS_BY_ID = {}


# =========================================
# MINISEARCH SERVER HANDLER
# =========================================

class MiniSearchHandler(BaseHTTPRequestHandler):

    # -------------------------------------
    # CORS HEADERS
    # -------------------------------------

    def send_cors_headers(self):

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

    # -------------------------------------
    # HANDLE PREFLIGHT REQUESTS
    # -------------------------------------

    def do_OPTIONS(self):

        self.send_response(204)

        self.send_cors_headers()

        self.end_headers()

    # -------------------------------------
    # SEND JSON RESPONSE
    # -------------------------------------

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

        self.send_header(
            "Content-Length",
            str(len(response))
        )

        self.send_cors_headers()

        self.end_headers()
        self.wfile.write(response)

    # -------------------------------------
    # SEND ERROR RESPONSE
    # -------------------------------------

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

    # -------------------------------------
    # SERVE FRONTEND FILES
    # -------------------------------------

    def serve_frontend(self, path):

        # Root URL serves index.html.
        if path == "/":
            relative_path = "index.html"

        else:
            relative_path = unquote(path).lstrip("/")

        requested_path = Path(relative_path)

        if not requested_path.parts:

            self.send_error_json(
                404,
                "ENDPOINT_NOT_FOUND",
                "The requested file does not exist."
            )

            return

        first_part = requested_path.parts[0]

        # Allow only index.html and approved static directories.
        if (
            first_part != "index.html"
            and first_part not in STATIC_DIRECTORIES
        ):

            self.send_error_json(
                404,
                "ENDPOINT_NOT_FOUND",
                "The requested endpoint does not exist."
            )

            return

        # Do not allow paths such as /index.html/other-file.
        if first_part == "index.html" and len(requested_path.parts) != 1:

            self.send_error_json(
                404,
                "ENDPOINT_NOT_FOUND",
                "The requested file does not exist."
            )

            return

        file_path = (
            PROJECT_ROOT / requested_path
        ).resolve()

        # Restrict access to the permitted frontend locations.
        if first_part == "index.html":

            allowed_root = PROJECT_ROOT.resolve()

        else:

            allowed_root = (
                PROJECT_ROOT / first_part
            ).resolve()

        try:

            file_path.relative_to(allowed_root)

        except ValueError:

            self.send_error_json(
                404,
                "ENDPOINT_NOT_FOUND",
                "The requested file does not exist."
            )

            return

        if not file_path.is_file():

            self.send_error_json(
                404,
                "ENDPOINT_NOT_FOUND",
                "The requested frontend file was not found."
            )

            return

        try:

            content = file_path.read_bytes()

            content_type, _ = mimetypes.guess_type(
                str(file_path)
            )

            # Ensure browsers interpret JavaScript and CSS correctly.
            if file_path.suffix == ".js":

                content_type = "text/javascript"

            elif file_path.suffix == ".css":

                content_type = "text/css"

            if content_type is None:

                content_type = "application/octet-stream"

            if (
                content_type.startswith("text/")
                or content_type in (
                    "application/javascript",
                    "application/json"
                )
            ):

                content_type += "; charset=utf-8"

            self.send_response(200)

            self.send_header(
                "Content-Type",
                content_type
            )

            self.send_header(
                "Content-Length",
                str(len(content))
            )

            self.end_headers()

            self.wfile.write(content)

        except OSError:

            self.send_error_json(
                500,
                "INTERNAL_SERVER_ERROR",
                "The requested frontend file could not be read."
            )

    # -------------------------------------
    # HANDLE GET REQUESTS
    # -------------------------------------

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

                doc_id = unquote(path[len("/doc/"):])

                self.handle_document(doc_id)

            else:

                self.serve_frontend(path)

        except Exception:

            self.send_error_json(
                500,
                "INTERNAL_SERVER_ERROR",
                "An unexpected server error occurred."
            )

    # -------------------------------------
    # SEARCH ENDPOINT
    # -------------------------------------

    def handle_search(self, parameters):

        query = parameters.get("query", [""])[0]

        mode = parameters.get("mode", ["OR"])[0]

        try:

            k = int(
                parameters.get("k", ["10"])[0]
            )

            offset = int(
                parameters.get("offset", ["0"])[0]
            )

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

            self.send_json(
                200,
                response
            )

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

    # -------------------------------------
    # STATS ENDPOINT
    # -------------------------------------

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

    # -------------------------------------
    # DOCUMENT ENDPOINT
    # -------------------------------------

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


# =========================================
# START MINISEARCH SERVER
# =========================================

def start_server():

    global INVERTED_INDEX
    global DOCUMENT_FREQUENCY
    global DOCUMENT_LENGTHS
    global DOCUMENTS_BY_ID

    # Check whether the search index exists.
    if not INDEX_PATH.exists():

        print("Error: Search index not found.")
        print("Run the index-building process first.")

        return

    # Load the existing inverted index.
    (
        INVERTED_INDEX,
        DOCUMENT_FREQUENCY,
        DOCUMENT_LENGTHS
    ) = load_index()

    # Load the original documents.
    documents = load_documents()

    DOCUMENTS_BY_ID = {
        document["doc_id"]: document
        for document in documents
    }

    # Render provides the PORT environment variable.
    # Locally, the server uses port 8000 by default.
    host = "0.0.0.0"

    port = int(
        os.environ.get("PORT", 8000)
    )

    server_address = (host, port)

    server = ThreadingHTTPServer(
        server_address,
        MiniSearchHandler
    )

    print()
    print("=========================================")
    print("       MINISEARCH SERVER RUNNING")
    print("=========================================")
    print()
    print(f"Host:        {host}")
    print(f"Port:        {port}")
    print(f"Search API:  /search")
    print(f"Stats API:   /stats")
    print(f"Document:    /doc/1479")
    print(f"Zipf Graph:  /reports/term_frequency_distribution.png")
    print()
    print("Press Ctrl+C to stop the server.")
    print()

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print("\nStopping MiniSearch server...")

    finally:

        server.server_close()


# =========================================
# MAIN ENTRY POINT
# =========================================

if __name__ == "__main__":

    start_server()
