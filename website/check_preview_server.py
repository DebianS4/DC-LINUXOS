#!/usr/bin/env python3
"""Integration checks for the local static preview server."""

from __future__ import annotations

import http.client
import os
import socket
import subprocess
import time
from pathlib import Path

SERVER_DIR = Path(__file__).resolve().parent


def reserve_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def request(port: int, path: str = "/", method: str = "GET") -> tuple[int, dict[str, str], bytes]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
    try:
        connection.request(method, path)
        response = connection.getresponse()
        body = response.read()
        headers = {name.lower(): value for name, value in response.getheaders()}
        return response.status, headers, body
    finally:
        connection.close()


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    port = reserve_port()
    environment = os.environ.copy()
    environment.pop("HOST", None)
    environment["PORT"] = str(port)
    process = subprocess.Popen(
        ["node", "server.js"],
        cwd=SERVER_DIR,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        deadline = time.monotonic() + 10
        while True:
            if process.poll() is not None:
                output, error = process.communicate()
                raise RuntimeError(f"Preview server exited early. stdout={output!r} stderr={error!r}")
            try:
                status, headers, body = request(port)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise TimeoutError("Preview server did not become ready within 10 seconds.")
                time.sleep(0.1)

        expect(status == 200 and b"<!doctype html>" in body.lower(), "GET / must serve the landing page.")
        expect(headers.get("x-content-type-options") == "nosniff", "nosniff header is required.")
        expect(headers.get("referrer-policy") == "no-referrer", "no-referrer header is required.")
        expect(headers.get("x-frame-options") == "DENY", "X-Frame-Options DENY is required.")
        expect("frame-ancestors 'none'" in headers.get("content-security-policy", ""), "CSP must block framing.")

        for path in ("/assets/dc-linux-logo.webp", "/manus-routes.json"):
            expect(request(port, path)[0] == 200, f"Public route must work: {path}")
        icon_resources = {
            "/favicon.ico": "image/x-icon",
            "/favicon.svg": "image/svg+xml",
            "/manifest.webmanifest": "application/manifest+json",
            "/assets/favicon-16x16.png": "image/png",
            "/assets/favicon-32x32.png": "image/png",
            "/assets/favicon-48x48.png": "image/png",
            "/assets/apple-touch-icon.png": "image/png",
            "/assets/pwa-192x192.png": "image/png",
            "/assets/pwa-512x512.png": "image/png",
        }
        for path, content_type in icon_resources.items():
            status, headers, body = request(port, path)
            expect(status == 200 and body, f"Icon resource must load: {path}")
            expect(headers.get("content-type", "").startswith(content_type), f"Unexpected Content-Type for {path}")
        for path in ("/server.js", "/package.json"):
            expect(request(port, path)[0] == 404, f"Source/config route must not be served: {path}")
        for path in ("/assets/%2e%2e/server.js", "/%2e%2e/README.md"):
            expect(request(port, path)[0] == 403, f"Traversal must be denied: {path}")

        expect(request(port, "/%ZZ")[0] == 400, "Malformed percent encoding must return 400.")
        expect(request(port, "/", "POST")[0] == 405, "Non-read methods must be rejected.")
        head_status, _, head_body = request(port, "/", "HEAD")
        expect(head_status == 200 and not head_body, "HEAD must return headers without a body.")
        expect(request(port)[0] == 200, "The server must remain available after rejected requests.")

        print("Preview server checks passed: allowlisted routes, blocked traversal, safe methods, and security headers.")
        return 0
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)


if __name__ == "__main__":
    raise SystemExit(main())
