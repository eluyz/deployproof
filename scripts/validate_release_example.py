#!/usr/bin/env python3
"""CI-only validation of the release workflow example (requires PyYAML 6.0.3)."""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "examples" / "pages-deploy-and-verify.yml"
FIELDS = ("git_sha", "workflow_run_id", "run_attempt", "build_id")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def find_step(steps: list[dict], step_id: str) -> dict:
    result = [step for step in steps if step.get("id") == step_id]
    require(len(result) == 1, f"expected one step {step_id}")
    return result[0]


def exercise_identity_step(script: str, attempt: str) -> None:
    """Execute the example's identity script with synthetic build values."""
    sha = "abcde0123456789abcde0123456789abcde01234"
    run_id = "53001"
    expected = {
        "git_sha": sha,
        "workflow_run_id": run_id,
        "run_attempt": attempt,
        "build_id": f"{run_id}-{attempt}-{sha}",
    }
    with tempfile.TemporaryDirectory(prefix="deployproof-example-") as folder:
        root = Path(folder)
        (root / "dist").mkdir()
        output_file = root / "github-output"
        env = os.environ.copy()
        env.update(BUILD_SHA=sha, BUILD_RUN_ID=run_id,
                   BUILD_RUN_ATTEMPT=attempt, GITHUB_OUTPUT=str(output_file))
        outcome = subprocess.run(["bash", "-e", "-o", "pipefail", "-c", script],
                                 cwd=root, env=env, capture_output=True,
                                 text=True, timeout=30, check=False)
        require(outcome.returncode == 0,
                f"identity step failed: {outcome.returncode}: {outcome.stderr[-500:]}")
        manifest_file = root / "dist" / "deployproof.json"
        require(manifest_file.is_file(), "manifest not generated")
        actual = json.loads(manifest_file.read_text(encoding="utf-8"))
        require(actual == expected, f"wrong manifest for attempt={attempt}: {actual}")
        lines = output_file.read_text(encoding="utf-8").splitlines()
        require(all("=" in line for line in lines), "invalid job outputs")
        outputs = dict(line.split("=", 1) for line in lines)
        require(outputs == expected, "job outputs and public manifest differ")
    print(f"PASS: build-identity generator with attempt={attempt}")


def main() -> None:
    data = yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    require(isinstance(data, dict), "YAML must parse as a mapping")
    require("on" in data and "push" in data["on"]
            and "workflow_dispatch" in data["on"], "missing workflow triggers")
    require(data.get("permissions") == {"contents": "read"},
            "too-broad top-level permissions")
    build = data["jobs"]["build"]
    deploy = data["jobs"]["deploy"]
    require(deploy["needs"] == "build", "deploy must depend on build")
    require(deploy["permissions"] == {"contents": "read", "pages": "write", "id-token": "write"},
            "wrong deploy permissions")
    for key in FIELDS:
        require(build["outputs"][key] == "$"+"{{ steps.identity.outputs."+key+" }}",
                f"wrong job output: {key}")
    identity_step = find_step(build["steps"], "identity")
    require("python3 - <<'PY'" in identity_step["run"],
            "Python identity generator missing")
    for attempt in ("1", "2"):
        exercise_identity_step(identity_step["run"], attempt)
    verify_step = find_step(deploy["steps"], "proof")
    for arg, key in (("expected-sha", "git_sha"),
                     ("expected-run-id", "workflow_run_id"),
                     ("expected-run-attempt", "run_attempt"),
                     ("expected-build-id", "build_id")):
        require(verify_step["with"][arg] == "$"+"{{ needs.build.outputs."+key+" }}",
                f"untrusted verifier input: {arg}")
    require(verify_step["uses"] == "eluyz/deployproof@REPLACE_WITH_REVIEWED_RELEASE_COMMIT_SHA",
            "not-yet-public Action must stay an explicit placeholder")
    require(verify_step["with"]["site-url"] == "https://YOUR_USERNAME.github.io/YOUR_REPOSITORY/",
            "site URL must remain a placeholder")
    for job in data["jobs"].values():
        for step in job.get("steps", []):
            source = step.get("uses", "")
            if source.startswith("actions/"):
                require(re.fullmatch(r"actions/[^@]+@[0-9a-f]{40}", source),
                        f"official action not pinned: {source}")
    print("PASS: YAML parsed, build outputs trusted, Actions pinned, placeholders explicit")


if __name__ == "__main__":
    main()
