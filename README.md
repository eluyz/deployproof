# DeployProof (technical preview)

A minimal, dependency-free **composite GitHub Action** that checks whether a public GitHub Pages site exposes the expected deployment identity. It reads `deployproof.json` from the deployed site and compares four trusted identity fields.

> **Preview only:** This project has passed local loopback tests but has **not** been tested in a real GitHub Actions workflow or deployed to GitHub Pages. It is not yet released. No adoption or user demand has been verified.

## What this checks

- `git_sha`: source revision, **not sufficient by itself**
- `workflow_run_id`: workflow run that built the website
- `run_attempt`: attempt number for the same workflow run
- `build_id`: an identifier created by the build **before** uploading the site

A successful check is **`IDENTITY_PASS`, not `ARTIFACT_INTEGRITY_PASS`**. An up-to-date manifest can coexist with stale JS, CSS, images, or data files. Use asset-specific checks for those cases.

## Minimal example (not yet published)

First, create a manifest **in the directory that will be uploaded**, after the site has been built and before upload. For a Pages project under `/repo/`, the public manifest must appear at `https://owner.github.io/repo/deployproof.json`.

```yaml
# Example steps inside a GitHub Pages build job, after building ./dist.
- name: Create deployment identity manifest
  shell: bash
  env:
    BUILD_SHA: ${{ github.sha }}
    BUILD_RUN_ID: ${{ github.run_id }}
    BUILD_RUN_ATTEMPT: ${{ github.run_attempt }}
  run: |
    python3 - <<'PY'
    import json, os
    from pathlib import Path
    sha, run, attempt = (os.environ[k] for k in ("BUILD_SHA", "BUILD_RUN_ID", "BUILD_RUN_ATTEMPT"))
    manifest = {
      "git_sha": sha,
      "workflow_run_id": run,
      "run_attempt": attempt,
      "build_id": f"{run}-{attempt}-{sha}"
    }
    Path("dist/deployproof.json").write_text(json.dumps(manifest), encoding="utf-8")
    PY

- uses: actions/upload-pages-artifact@v4
  with:
    path: ./dist
```

After deploying the artifact, the verification step would be configured as follows. Replace `YOUR_ORG/deployproof@FULL_40_CHARACTER_COMMIT_SHA` **only when a reviewed version is actually published**. Pin its full commit SHA rather than using an unreviewed tag. The expected values must describe the **build artifact**, not an unrelated verification job:

```yaml
- name: Verify deployed build identity
  uses: YOUR_ORG/deployproof@FULL_40_CHARACTER_COMMIT_SHA # Not published; replace after release
  with:
    site-url: https://owner.github.io/repo/
    expected-sha: ${{ github.sha }}
    expected-run-id: ${{ github.run_id }}
    expected-run-attempt: ${{ github.run_attempt }}
    expected-build-id: ${{ github.run_id }}-${{ github.run_attempt }}-${{ github.sha }}
```

**Important:** The `expected-build-id` expression must match the build step exactly; in this example, both use `run_id-run_attempt-full_sha`. For a different build or workflow, transfer trusted IDs explicitly as job outputs or artifacts. Replace all placeholder URLs and Action references before using the workflow.

## Why use `deployproof.json` instead of `.well-known/deployproof.json`?

`actions/upload-pages-artifact@v4` unconditionally omits dotfiles and dot-directories. `@v5` supports `include-hidden-files`, which is disabled by default. An ordinary `deployproof.json` avoids unintentionally omitting the manifest and avoids publishing other hidden files.

## Local tests

```bash
python3 -m unittest discover -s tests -v
```

Tests use a local HTTP server and an explicit test-only loopback override. The shipped Action rejects HTTP, arbitrary hostnames, IP literals, credentials, absolute manifest paths, and redirects. A GitHub Actions CI workflow is included but has **not run** in a GitHub repository.

## Current constraints

- GitHub Pages `*.github.io` domains only; no custom domains in this preview.
- Requires Python 3 on the runner; designed for `ubuntu-latest` hosted runners.
- Strict manifest size limit: 64 KiB; all four identifiers must be strings.
- Supports bounded attempts, delay and timeout; retries missing/mismatched manifests and network errors.
- Concurrency and superseding deployments are not detected automatically. A mismatch can mean a newer deployment replaced the expected one, not that Pages malfunctioned.
- GitHub Actions runtime, CDN behavior, DNS edge cases, security scanning and public HTTPS deployment have **not** been tested.

## Status

**Local preview / educational experiment.** No installation instructions or release promises should be treated as evidence of a production-ready Action.
