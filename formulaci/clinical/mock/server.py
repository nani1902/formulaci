"""Tiny stdlib HTTP server for the mock calculator pages (binds to 127.0.0.1 only)."""
from __future__ import annotations

import functools
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PAGES = Path(__file__).with_name("pages")
TARGETS = Path(__file__).with_name("targets.yaml")


class _Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):  # keep test output quiet
        pass


def make_server(port: int = 0, host: str = "127.0.0.1") -> ThreadingHTTPServer:
    """Create (not start) the server; ``port=0`` picks a free port (see ``server.server_port``)."""
    handler = functools.partial(_Handler, directory=str(PAGES))
    return ThreadingHTTPServer((host, port), handler)


def serve_in_thread(port: int = 0) -> tuple[ThreadingHTTPServer, str]:
    """Start the server on a daemon thread; return it and its base URL. Call ``.shutdown()``."""
    srv = make_server(port)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_port}"
