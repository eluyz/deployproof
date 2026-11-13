"""Local HTTP integration tests for the DeployProof preview."""
import contextlib
import importlib.util
import json
import os
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("deployproof_verify", Path(__file__).resolve().parents[1] / "scripts" / "verify.py")
verify_module = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = verify_module
spec.loader.exec_module(verify_module)

EXPECTED = {"git_sha": "abc123", "workflow_run_id": "100", "run_attempt": "2", "build_id": "site-2"}


class FakeSiteHandler(BaseHTTPRequestHandler):
    responses = {}
    def log_message(self, *args):
        pass
    def do_GET(self):
        route = self.path.split("?", 1)[0]
        seq = self.responses.get(route, [(404, b"missing")])
        status, body = seq.pop(0) if len(seq) > 1 else seq[0]
        self.send_response(status)
        if status == 302:
            self.send_header("Location", "http://127.0.0.1:9/unsafe")
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)


class DeployProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeSiteHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.site = f"http://127.0.0.1:{cls.server.server_port}/repo/"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        FakeSiteHandler.responses = {}

    def set_manifest(self, value, status=200, path="/repo/deployproof.json"):
        FakeSiteHandler.responses[path] = [(status, json.dumps(value).encode())]

    def check(self, **kwargs):
        return verify_module.verify(self.site, "deployproof.json", EXPECTED, attempts=1, delay_seconds=0, allow_test_loopback=True, **kwargs)

    def test_matching_identity(self):
        self.set_manifest(EXPECTED)
        self.assertEqual(self.check().kind, "IDENTITY_PASS")

    def test_wrong_run_same_sha(self):
        self.set_manifest({**EXPECTED, "workflow_run_id": "77"})
        self.assertEqual(self.check().kind, "VERSION_MISMATCH")

    def test_wrong_build_same_sha(self):
        self.set_manifest({**EXPECTED, "build_id": "outdated", "run_attempt": "1"})
        self.assertEqual(self.check().kind, "VERSION_MISMATCH")

    def test_missing_manifest(self):
        self.assertEqual(self.check().kind, "MISSING_MANIFEST")

    def test_wrong_repo_path(self):
        self.set_manifest(EXPECTED)
        other = verify_module.verify(self.site.replace('/repo/','/'), "deployproof.json", EXPECTED, attempts=1, allow_test_loopback=True)
        self.assertEqual(other.kind, "MISSING_MANIFEST")

    def test_asset_stale_is_not_checked(self):
        self.set_manifest(EXPECTED)
        FakeSiteHandler.responses["/repo/app.js"] = [(200, b"old bundle")]
        self.assertEqual(self.check().kind, "IDENTITY_PASS")

    def test_invalid_json(self):
        FakeSiteHandler.responses["/repo/deployproof.json"] = [(200, b"not JSON")]
        self.assertEqual(self.check().kind, "INVALID_MANIFEST")

    def test_missing_identity_field(self):
        self.set_manifest({"git_sha": EXPECTED["git_sha"]})
        self.assertEqual(self.check().kind, "INVALID_MANIFEST")

    def test_manifest_too_large(self):
        FakeSiteHandler.responses["/repo/deployproof.json"] = [(200, b"{" + b" " * (64 * 1024) + b"}")]
        self.assertEqual(self.check().kind, "INVALID_MANIFEST")

    def test_block_redirect(self):
        FakeSiteHandler.responses["/repo/deployproof.json"] = [(302, b"redirect")]
        self.assertEqual(self.check().kind, "HTTP_ERROR")

    def test_retry_after_stale_manifest(self):
        FakeSiteHandler.responses["/repo/deployproof.json"] = [(200, json.dumps({**EXPECTED,"build_id":"old"}).encode()), (200, json.dumps(EXPECTED).encode())]
        result = verify_module.verify(self.site, "deployproof.json", EXPECTED, attempts=2, delay_seconds=0, allow_test_loopback=True)
        self.assertEqual(result.kind, "IDENTITY_PASS")

    def test_non_public_address_rejected(self):
        with self.assertRaises(ValueError):
            verify_module.validate_url("https://127.0.0.1/repo/", "deployproof.json")

    def test_custom_domain_rejected_by_preview(self):
        with self.assertRaises(ValueError):
            verify_module.validate_url("https://example.com/", "deployproof.json")

    def test_credentials_rejected(self):
        with self.assertRaises(ValueError):
            verify_module.validate_url("https://user:pw@owner.github.io/repo/", "deployproof.json")

    def test_absolute_manifest_path_rejected(self):
        with self.assertRaises(ValueError):
            verify_module.validate_url("https://owner.github.io/repo/", "/deployproof.json")

    def test_encoded_dot_segments_rejected(self):
        with self.assertRaises(ValueError):
            verify_module.validate_url("https://owner.github.io/repo/%2e%2e/", "deployproof.json")

    def test_no_slash_at_end_rejected(self):
        with self.assertRaises(ValueError):
            verify_module.validate_url("https://owner.github.io/repo", "deployproof.json")

    def test_expected_fields_required(self):
        self.set_manifest(EXPECTED)
        invalid = verify_module.verify(self.site, "deployproof.json", {**EXPECTED,"build_id":""},attempts=1,allow_test_loopback=True)
        self.assertEqual(invalid.kind, "INVALID_CONFIG")

    def test_empty_username_is_rejected(self):
        with self.assertRaises(ValueError):
            verify_module.validate_url("https://@owner.github.io/repo/", "deployproof.json")

    def test_encoded_site_root_is_rejected(self):
        with self.assertRaises(ValueError):
            verify_module.validate_url("https://owner.github.io/%41/", "deployproof.json")

    def test_duplicate_identity_key_is_rejected(self):
        payload = json.dumps(EXPECTED).replace('"git_sha":', '"git_sha": "fake", "git_sha":', 1)
        FakeSiteHandler.responses["/repo/deployproof.json"] = [(200, payload.encode())]
        self.assertEqual(self.check().kind, "INVALID_MANIFEST")

    def test_verdict_output_written_on_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "github-output"
            with patch.dict(os.environ, {"GITHUB_OUTPUT": str(path)}):
                verify_module.emit_output(
                    verify_module.Result("VERSION_MISMATCH", "Different field(s): build_id")
                )
            self.assertEqual(path.read_text(encoding="utf-8"), "verdict=VERSION_MISMATCH\\n".replace("\\\\n", "\\n"))

    def test_mismatch_does_not_log_identity_values(self):
        self.set_manifest({**EXPECTED, "build_id": "observed-private-build"})
        result = self.check()
        self.assertEqual(result.kind, "VERSION_MISMATCH")
        self.assertNotIn("observed-private-build", result.details)
        self.assertNotIn("site-2", result.details)


if __name__ == "__main__":
    unittest.main()
