#!/usr/bin/env python3
"""CI-only, offline validation of the independent consumer smoke example.

Requires PyYAML 6.0.3 in CI. Does not install the Action cross-repository;
that evidence requires a run in a separately authorized consumer repository.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "examples" / "consumer-install-smoke.yml"
ACTION = "eluyz/deployproof@1c03c9d4ace3855bf12fc7672c6d6a60cc072b8f"
SITE_URL = "https://eluyz.github.io/deployproof/"
EXPECTED = {
    "git_sha": "a" * 40,
    "workflow_run_id": "53001",
    "run_attempt": "2",
    "build_id": f"53001-2-{'a' * 40}",
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def step_by_id(steps: list[dict], sid: str) -> dict:
    matches = [step for step in steps if step.get("id") == sid]
    require(len(matches) == 1, f"expected one step id={sid}")
    return matches[0]


def verify_fixture_parser(script: str) -> None:
    class Handler(BaseHTTPRequestHandler):
        manifest = EXPECTED

        def log_message(self, *args) -> None:
            pass

        def do_GET(self) -> None:
            require(self.path == "/deployproof.json", "unexpected test fixture route")
            payload = json.dumps(self.manifest).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(payload)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        def run(manifest: dict) -> tuple[subprocess.CompletedProcess, str]:
            Handler.manifest = manifest
            with tempfile.TemporaryDirectory(prefix="deployproof-consumer-") as folder:
                output_path = Path(folder) / "github-output"
                env = os.environ.copy()
                env["FIXTURE_URL"] = (
                    f"http://127.0.0.1:{server.server_port}/deployproof.json"
                )  # Explicit test-only loopback override, not in published workflow.
                env["GITHUB_OUTPUT"] = str(output_path)
                proc = subprocess.run(
                    ["bash", "-e", "-o", "pipefail", "-c", script],
                    env=env, capture_output=True, text=True, timeout=20,
                    check=False,
                )
                data = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
                return proc, data

        good, outputs = run(EXPECTED)
        require(good.returncode == 0, f"valid fixture failed: {good.stderr[-300:]}")
        parsed = dict(line.split("=", 1) for line in outputs.splitlines())
        require(parsed == EXPECTED, "consumer fixture outputs differ")
        invalid, _ = run({**EXPECTED, "build_id": "tampered"})
        require(invalid.returncode != 0, "tampered fixture should be rejected")
        print("PASS: consumer fixture parser executes against local HTTP")
        print("PASS: expected fixture values and tampered build rejection")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def main() -> None:
    workflow = yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    require(isinstance(workflow, dict), "consumer workflow YAML must be a mapping")
    require("on" in workflow, "GitHub on trigger missing")
    require("push" in workflow["on"] and "workflow_dispatch" in workflow["on"],
            "consumer smoke must support push + manual dispatch")
    require(workflow.get("permissions") == {"contents": "read"},
            "consumer workflow must keep read-only permissions")
    jobs = workflow["jobs"]
    require(set(jobs) == {"consumer-smoke"}, "only test job should exist")
    steps = jobs["consumer-smoke"]["steps"]
    fixture = step_by_id(steps, "fixture")
    require(fixture.get("env", {}).get("FIXTURE_URL") ==
            SITE_URL + "deployproof.json", "unexpected public test fixture URL")
    require("python3 - <<'PY'" in fixture["run"], "test parser is missing")
    verify_fixture_parser(fixture["run"])

    positive = step_by_id(steps, "positive")
    wrong = step_by_id(steps, "wrong_build")
    missing = step_by_id(steps, "missing_manifest")
    for item in (positive, wrong, missing):
        require(item.get("uses") == ACTION, "must use the reviewed published full SHA")
        require(item["with"]["site-url"] == SITE_URL,
                "unexpected production target in consumer smoke")
        for input_name, field in (
            ("expected-sha", "git_sha"),
            ("expected-run-id", "workflow_run_id"),
            ("expected-run-attempt", "run_attempt"),
        ):
            expected_output = "$"+"{{ steps.fixture.outputs."+field+" }}"
            require(item["with"][input_name] == expected_output,
                    f"wrong fixture output for {input_name}")
    require(
        positive["with"]["expected-build-id"] ==
        "$"+"{{ steps.fixture.outputs.build_id }}",
        "positive test build ID must match fixture",
    )
    require(wrong.get("continue-on-error") == "true",
            "wrong-build check must be an expected failure")
    require(wrong["with"]["expected-build-id"] == "deliberately-wrong-build-id",
            "wrong build fixture must be wrong deliberately")
    require(missing.get("continue-on-error") == "true",
            "missing-manifest check must be an expected failure")
    require(missing["with"].get("manifest-path") ==
            "missing-consumer-smoke-manifest.json",
            "missing manifest path changed")
    assert_steps = [step for step in steps if step.get("name", "").startswith("Assert ")]
    require(len(assert_steps) == 3, "each outcome must have a verdict assertion")
    all_assertions = "\n".join(step["run"] for step in assert_steps)
    for verdict in ("IDENTITY_PASS", "VERSION_MISMATCH", "MISSING_MANIFEST"):
        require(verdict in all_assertions, f"missing exact assertion: {verdict}")
    print("PASS: consumer workflow syntax, SHA pin and three exact-verdict assertions")
    print("NOTE: external cross-repository Action invocation remains NOT TESTED")


if __name__ == "__main__":
    main()
