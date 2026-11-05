#!/usr/bin/env python3
"""Deterministic security checks for the static GitHub Pages artifact."""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

EXPECTED_CSP = {
    "default-src": ["'none'"],
    "base-uri": ["'self'"],
    "object-src": ["'none'"],
    "form-action": ["'none'"],
    "frame-src": ["'none'"],
    "worker-src": ["'none'"],
    "media-src": ["'none'"],
    "manifest-src": ["'none'"],
    "img-src": ["'self'", "data:"],
    "script-src": ["'self'"],
    "style-src": ["'self'"],
    "style-src-attr": ["'none'"],
    "font-src": ["'self'"],
    "connect-src": ["'none'"],
    "upgrade-insecure-requests": [],
}


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.errors: list[str] = []
        self.csp: str | None = None
        self.referrer_policy: str | None = None
        self.release_downloads: set[str] = set()
        self.visible_hashes: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name.lower(): value or "" for name, value in attrs}

        for name in attributes:
            if name == "style":
                self.errors.append("Inline style attributes are not allowed by the site CSP.")
            if name.startswith("on") and len(name) > 2:
                self.errors.append(f"Inline event handler is not allowed: {name}.")

        if tag == "meta":
            if attributes.get("http-equiv", "").lower() == "content-security-policy":
                if self.csp is not None:
                    self.errors.append("More than one CSP meta policy was found.")
                self.csp = attributes.get("content", "")
            if attributes.get("name", "").lower() == "referrer":
                self.referrer_policy = attributes.get("content", "").lower()

        if tag == "script":
            if not attributes.get("src"):
                self.errors.append("Inline scripts are not allowed.")
            else:
                self._check_local_resource("script src", attributes["src"])

        if tag == "img" and attributes.get("src"):
            self._check_local_resource("image src", attributes["src"])

        if tag == "link" and attributes.get("href"):
            self._check_local_resource("link href", attributes["href"])

        if tag == "a":
            href = attributes.get("href", "")
            target = attributes.get("target", "").lower()
            rel = set(attributes.get("rel", "").lower().split())
            parsed = urlsplit(href)

            if parsed.scheme and parsed.scheme.lower() != "https":
                self.errors.append(f"Non-HTTPS link found: {href}")
            if target == "_blank" and not {"noopener", "noreferrer"}.issubset(rel):
                self.errors.append(f"New-tab link must use rel=noopener noreferrer: {href}")

            if "/releases/download/" in parsed.path:
                if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
                    self.errors.append(f"Release download must use HTTPS on github.com: {href}")
                if not parsed.path.startswith("/DebianS4/DC-LINUXOS/releases/download/"):
                    self.errors.append(f"Release download is outside the expected repository: {href}")
                self.release_downloads.add(parsed.path)

        if tag == "code":
            self._in_code = True
            self._code_text = ""

    def handle_data(self, data: str) -> None:
        if getattr(self, "_in_code", False):
            self._code_text += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "code" and getattr(self, "_in_code", False):
            value = self._code_text.strip()
            if re.fullmatch(r"[0-9a-fA-F]{64}", value):
                self.visible_hashes.append(value.lower())
            self._in_code = False

    def _check_local_resource(self, label: str, value: str) -> None:
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc or value.startswith("/") or ".." in Path(parsed.path).parts:
            self.errors.append(f"{label} must be a same-origin relative path: {value}")


def parse_csp(content: str) -> dict[str, list[str]]:
    directives: dict[str, list[str]] = {}
    for item in content.split(";"):
        tokens = item.strip().split()
        if not tokens:
            continue
        name = tokens[0].lower()
        if name in directives:
            raise ValueError(f"Duplicate CSP directive: {name}")
        directives[name] = tokens[1:]
    return directives


def main() -> int:
    artifact = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("website/dist")
    errors: list[str] = []

    if not artifact.is_dir():
        print(f"Build artifact directory not found: {artifact}", file=sys.stderr)
        return 1

    expected_root = {"assets", "index.html", "styles.css", "script.js", "favicon.ico"}
    actual_root = {entry.name for entry in artifact.iterdir()}
    for name in sorted(expected_root - actual_root):
        errors.append(f"Required build output is missing: {name}")
    for name in sorted(actual_root - expected_root):
        errors.append(f"Unexpected file or directory in public build: {name}")

    html_path = artifact / "index.html"
    if html_path.is_file():
        source = html_path.read_text(encoding="utf-8")
        parser = SiteParser()
        parser.feed(source)
        parser.close()
        errors.extend(parser.errors)

        if parser.referrer_policy != "no-referrer":
            errors.append("The document must retain the no-referrer policy.")
        if parser.csp is None:
            errors.append("A CSP meta policy is required.")
        else:
            try:
                csp = parse_csp(parser.csp)
                if csp != EXPECTED_CSP:
                    errors.append(f"CSP does not match the reviewed least-privilege policy: {csp}")
            except ValueError as exc:
                errors.append(str(exc))

        downloads = parser.release_downloads
        if not downloads:
            errors.append("No GitHub Release downloads were found.")
        for path in sorted(downloads):
            if path.endswith(".img.xz"):
                sidecar = path + ".sha256"
            elif path.endswith(".part00") or path.endswith(".part01"):
                sidecar = path.rsplit(".part", 1)[0] + ".sha256"
            else:
                continue
            if sidecar not in downloads:
                errors.append(f"Download has no matching SHA-256 sidecar link: {path}")

        if len(parser.visible_hashes) < 3:
            errors.append("Expected visible 64-character SHA-256 values are missing.")
    else:
        errors.append("Build artifact index.html is missing.")

    for name in expected_root - {"assets"}:
        file_path = artifact / name
        if file_path.is_file() and file_path.stat().st_size == 0:
            errors.append(f"Build output is empty: {name}")

    if errors:
        print("Site security checks failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Site security checks passed: CSP, referrer policy, same-origin assets, HTTPS downloads, SHA-256 links, and public artifact contents.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
