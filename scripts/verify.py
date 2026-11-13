#!/usr/bin/env python3
"""Check public GitHub Pages deployment identity, not asset integrity."""

import json
import os
import re
import sys
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

MAX_MANIFEST_BYTES = 64 * 1024
FIELDS = ("git_sha", "workflow_run_id", "run_attempt", "build_id")


class BlockRedirects(HTTPRedirectHandler):
    """Never follow redirects to an unexpected origin."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


@dataclass(frozen=True)
class Result:
    kind: str
    details: str
    retryable: bool = False

    @property
    def success(self):
        return self.kind == "IDENTITY_PASS"


def validate_url(site_url, manifest_path, *, allow_test_loopback=False):
    """Return the absolute manifest URL or raise ValueError.

    Production scope: GitHub Pages github.io domains only. DNS pinning and custom
    domain support are explicitly outside this preview's scope.
    """
    parsed = urlsplit(site_url)
    if not parsed.netloc or not parsed.hostname:
        raise ValueError("site-url must include a hostname")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("site-url must not contain credentials, query or fragment")
    if site_url != site_url.strip() or any(ord(c) < 33 for c in site_url):
        raise ValueError("site-url contains whitespace or control characters")
    if not parsed.path.endswith("/"):
        raise ValueError("site-url must end with '/' (including /repo/ for project Pages)")
    if not re.fullmatch(r"[a-zA-Z0-9.-]+", parsed.hostname):
        raise ValueError("invalid hostname")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("invalid port") from exc
    local = allow_test_loopback and parsed.hostname == "127.0.0.1" and parsed.scheme == "http"
    if local:
        if port is None:
            raise ValueError("local test requires explicit port")
    elif parsed.scheme != "https" or port not in (None, 443) or not parsed.hostname.endswith(".github.io"):
        raise ValueError("only HTTPS *.github.io sites are supported")
    if re.search(r"%(?:2f|5c|2e|3f|23)", parsed.path, flags=re.I):
        raise ValueError("encoded separators or dot segments are not supported")
    if any(p in (".", "..") for p in unquote(parsed.path).split("/")):
        raise ValueError("site-url must not contain dot segments")
    if not manifest_path or any(c in manifest_path for c in ("\\", "?", "#", ":")):
        raise ValueError("invalid manifest-path")
    if manifest_path.startswith("/") or any(p in ("", ".", "..") for p in manifest_path.split("/")):
        raise ValueError("manifest-path must be relative without dot segments")
    if re.search(r"%|[\x00-\x20]", manifest_path):
        raise ValueError("manifest-path must not contain encoded or whitespace characters")
    return urljoin(site_url, manifest_path)


def _read_manifest(url, timeout_seconds):
    opener = build_opener(BlockRedirects())
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "DeployProof-preview/0.1"})
    try:
        with opener.open(request, timeout=timeout_seconds) as response:
            if response.status != 200:
                return Result("HTTP_ERROR", f"HTTP status {response.status}")
            content = response.read(MAX_MANIFEST_BYTES + 1)
    except HTTPError as exc:
        if exc.code == 404:
            return Result("MISSING_MANIFEST", "HTTP 404: public manifest is missing", True)
        return Result("HTTP_ERROR", f"HTTP status {exc.code}")
    except (URLError, OSError, TimeoutError) as exc:
        return Result("NETWORK_ERROR", f"Network request failed: {type(exc).__name__}", True)
    if len(content) > MAX_MANIFEST_BYTES:
        return Result("INVALID_MANIFEST", "manifest exceeds 64 KiB limit")
    try:
        data = json.loads(content)
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
        return Result("INVALID_MANIFEST", "response body is not valid JSON")
    if not isinstance(data, dict) or not all(isinstance(data.get(key), str) for key in FIELDS):
        return Result("INVALID_MANIFEST", "manifest must contain four string identity fields")
    return data


def check_once(site_url, manifest_path, expected, *, timeout_seconds=10, allow_test_loopback=False):
    try:
        url = validate_url(site_url, manifest_path, allow_test_loopback=allow_test_loopback)
    except ValueError as exc:
        return Result("INVALID_CONFIG", str(exc))
    actual = _read_manifest(url, timeout_seconds)
    if isinstance(actual, Result):
        return actual
    different = [key for key in FIELDS if actual[key] != expected[key]]
    if different:
        fields = ", ".join(different)
        # IDs may be public, but do not echo manifest content or arbitrary secrets.
        return Result("VERSION_MISMATCH", f"Different field(s): {fields}", True)
    return Result("IDENTITY_PASS", "All four deployment identity fields match")


def verify(site_url, manifest_path, expected, *, attempts=5, delay_seconds=2, timeout_seconds=10, allow_test_loopback=False, sleep=time.sleep):
    if not (1 <= attempts <= 20 and 0 <= delay_seconds <= 30 and 1 <= timeout_seconds <= 30):
        return Result("INVALID_CONFIG", "retry or timeout inputs are outside allowed limits")
    if not all(isinstance(expected.get(k), str) and expected[k] for k in FIELDS):
        return Result("INVALID_CONFIG", "all four expected identity fields are required")
    last = None
    for index in range(attempts):
        last = check_once(site_url, manifest_path, expected, timeout_seconds=timeout_seconds, allow_test_loopback=allow_test_loopback)
        print(f"Attempt {index + 1}/{attempts}: {last.kind} - {last.details}", flush=True)
        if last.success or not last.retryable:
            return last
        if index < attempts - 1:
            sleep(delay_seconds)
    return last


def _env_int(name, default):
    try:
        return int(os.environ.get(name, str(default)))
    except ValueError:
        return -1


def main():
    expected = {
        "git_sha": os.environ.get("DP_EXPECTED_SHA", ""),
        "workflow_run_id": os.environ.get("DP_EXPECTED_RUN_ID", ""),
        "run_attempt": os.environ.get("DP_EXPECTED_RUN_ATTEMPT", ""),
        "build_id": os.environ.get("DP_EXPECTED_BUILD_ID", ""),
    }
    result = verify(
        os.environ.get("DP_SITE_URL", ""),
        os.environ.get("DP_MANIFEST_PATH", "deployproof.json"),
        expected,
        attempts=_env_int("DP_ATTEMPTS", 5),
        delay_seconds=_env_int("DP_DELAY_SECONDS", 2),
        timeout_seconds=_env_int("DP_TIMEOUT_SECONDS", 10),
    )
    print(f"RESULT: {result.kind} - {result.details}")
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
