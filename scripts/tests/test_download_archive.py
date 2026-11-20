"""Exercise the Docs downloader against a local HTTP server."""

import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import subprocess
import tempfile
from threading import Thread
import unittest


DOWNLOAD = Path(__file__).resolve().parents[1] / "download-archive.sh"


class TestDownloadArchive(unittest.TestCase):
    def download(self, responses, archive):
        requests = []

        class Handler(BaseHTTPRequestHandler):
            timeout = 2

            def do_GET(self):
                status, length, body = responses[min(len(requests), len(responses) - 1)]
                requests.append(self.path)
                self.send_response(status)
                self.send_header("Content-Length", str(length))
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_args):
                pass

        with HTTPServer(("127.0.0.1", 0), Handler) as server:
            thread = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05})
            thread.start()
            try:
                result = subprocess.run(
                    [
                        "bash",
                        str(DOWNLOAD),
                        f"http://127.0.0.1:{server.server_port}/archive",
                        str(archive),
                    ],
                    env={**os.environ, "no_proxy": "127.0.0.1"},
                    capture_output=True,
                    text=True,
                    timeout=12,
                )
            finally:
                server.shutdown()
                thread.join()
        return result, len(requests)

    def test_retries_truncated_response_and_replaces_partial_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "archive.tar.gz"
            result, requests = self.download(
                [(200, 100, b"ab"), (200, 2, b"cd")], archive
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(requests, 2)
            self.assertEqual(archive.read_bytes(), b"cd")

    def test_http_error_fails_after_bounded_retries(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "archive.tar.gz"
            result, requests = self.download([(404, 2, b"no")], archive)
            self.assertEqual(result.returncode, 22, result.stderr)
            self.assertEqual(requests, 4)
            self.assertFalse(archive.exists())
