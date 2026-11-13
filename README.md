# DeployProof — GitHub Pages deployment identity check

DeployProof is a small Python-standard-library composite GitHub Action that checks whether a **public GitHub Pages deployment manifest** matches the identity produced by the build that was actually uploaded.

> **Technical preview, not released:** The private repository has passed GitHub Actions CI and controlled real GitHub Pages E2E tests. The public test page at https://eluyz.github.io/deployproof/ contains only generated test content. This repository is not yet available to external users as an installable public Action, and demand/adoption are unverified.

## What it verifies

The static site must serve `deployproof.json` containing **four string fields**:

```json
{
  "git_sha": "REPLACE_WITH_THE_BUILD_SOURCE_SHA",
  "workflow_run_id": "REPLACE_WITH_THE_BUILD_WORKFLOW_RUN_ID",
  "run_attempt": "REPLACE_WITH_THE_BUILD_WORKFLOW_ATTEMPT",
  "build_id": "REPLACE_WITH_A_BUILD_ID_GENERATED_BEFORE_UPLOAD"
}
```

The Action compares each field against a trusted expected value and fails with a machine-readable `verdict`. The available verdicts are `IDENTITY_PASS`, `VERSION_MISMATCH`, `MISSING_MANIFEST`, `INVALID_MANIFEST`, `INVALID_CONFIG`, `NETWORK_ERROR`, and `HTTP_ERROR`.

**What it does not verify:** `IDENTITY_PASS` is **not** a hash, signature, asset-integrity check, browser smoke test, or proof that JS/CSS/images/data are fresh. An attacker or misconfigured build can publish a matching manifest while other files are stale. A later legitimate deployment can also replace the expected build.

## Verified reference workflow

The actual `.github/workflows/pages-e2e.yml` is a **complete, working reference**, with SHA-pinned official Actions and explicit build-to-deploy identity outputs. It publishes only synthetic files, then verifies the public Pages URL with one positive and two deliberately negative controls.

Evidence: [real GitHub Pages E2E, including re-run](https://github.com/eluyz/deployproof/actions/runs/43514695315) and [unit tests on GitHub runners](https://github.com/eluyz/deployproof/actions/runs/43514695329).

**Rerun rule:** `github.run_attempt` in a *re-run verification job* may differ from the `run_attempt` that produced the deployed artifact. Therefore, pass expected identities **from the build step/job outputs**, not from the verifying job's current workflow context. A rerun of the verifier job must continue checking the artifact's actual build identity.

## Integration outline (for after the first public release)

1. Configure GitHub Pages to deploy from **GitHub Actions**.
2. Run your normal build (for example, generate `dist/index.html`).
3. Before uploading `dist`, generate `dist/deployproof.json` and export the identical values as outputs of the **build step**.
4. Expose those build step values as **build job outputs**. Upload the directory with a pinned `actions/upload-pages-artifact`.
5. After deploying via a pinned `actions/deploy-pages`, check the live URL using a reviewed, pinned full SHA of DeployProof. Do not reference a nonexistent published tag.

Build step example (a fragment to add **after** your build command):

```yaml
- name: Generate the public build identity
  id: identity
  shell: bash
  env:
    BUILD_SHA: ${{ github.sha }}
    BUILD_RUN_ID: ${{ github.run_id }}
    BUILD_RUN_ATTEMPT: ${{ github.run_attempt }}
  run: |
    python3 - <<'PY'
    import json
    import os
    from pathlib import Path
    sha, run, attempt = (os.environ[k] for k in
                         ("BUILD_SHA", "BUILD_RUN_ID", "BUILD_RUN_ATTEMPT"))
    identity = {
        "git_sha": sha,
        "workflow_run_id": run,
        "run_attempt": attempt,
        "build_id": f"{run}-{attempt}-{sha}",
    }
    Path("dist/deployproof.json").write_text(
        json.dumps(identity), encoding="utf-8"
    )
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as out:
        for key, value in identity.items():
            out.write(f"{key}={value}\n")
    PY
```

At the **build job** level, export the values to the downstream deploy job:

```yaml
outputs:
  git_sha: ${{ steps.identity.outputs.git_sha }}
  workflow_run_id: ${{ steps.identity.outputs.workflow_run_id }}
  run_attempt: ${{ steps.identity.outputs.run_attempt }}
  build_id: ${{ steps.identity.outputs.build_id }}
```

After deploying, your **deploy job** must declare `needs: build` and can check the public site:

```yaml
- name: Verify the deployed build
  id: deployproof
  uses: eluyz/deployproof@REPLACE_WITH_REVIEWED_FULL_40_CHARACTER_COMMIT_SHA
  with:
    site-url: https://OWNER.github.io/REPO/
    manifest-path: deployproof.json
    expected-sha: ${{ needs.build.outputs.git_sha }}
    expected-run-id: ${{ needs.build.outputs.workflow_run_id }}
    expected-run-attempt: ${{ needs.build.outputs.run_attempt }}
    expected-build-id: ${{ needs.build.outputs.build_id }}
    attempts: '5'
    delay-seconds: '2'
    timeout-seconds: '10'
```

After an Action step, other steps can use `steps.deployproof.outputs.verdict`. The Action returns exit status 0 only on `IDENTITY_PASS` and nonzero for every failure. Failure categories are exposed even when the Action exits nonzero, so a testing workflow can assert the exact kind rather than treating every failure as a correct negative test.

**Important:** The examples above are snippets and are not complete workflow YAML by themselves. The complete working workflow is `.github/workflows/pages-e2e.yml`; adapt its build and site URL to your own repository. The public Action reference above is intentionally **not yet installable** because this repo is still private and no public release exists.

## Compatibility and security boundaries

- Only `https://*.github.io/` hosts are accepted. Use the exact site root with a trailing slash; project Pages sites need `https://OWNER.github.io/REPO/`. Custom domains (and their redirects), HTTP, IPs, credentials and nonstandard ports are not supported in this preview.
- Manifest paths must be relative, without escapes/dot segments. HTTP redirects are not followed. Responses are limited to 64 KiB and duplicate JSON keys are rejected.
- Requests have bounded retries, intervals and timeouts. Retries address publication delay, **not** an assurance of CDN-wide freshness.
- The GitHub Pages manifest is public: the commit SHA, workflow run ID, attempt and build ID will be **public metadata**, even if the source repository is private. Never put secrets, tokens, internal URLs or personal data in it.
- The public manifest is untrusted input; expected identity values must originate from the trusted build job. No cryptographic provenance is established.
- The composite Action uses the runner's `python3` standard library. Review upstream runner/network settings and pinned Action dependencies before deploying production workloads.
- `actions/upload-pages-artifact@v4` omits dotfiles/dotdirectories unconditionally. `@v5` can opt in to hidden files, but defaults to excluding them. This project uses a normal `deployproof.json` to avoid exposing other hidden artifacts.

## Tests

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts tests
```

CI exercises a local loopback HTTP server, while the separate Pages E2E workflow tests an actual public HTTPS deployment, including intentionally failing checks and job re-runs. Passing these tests does not establish correctness for every site, custom domain, proxy or CDN configuration.

## License and status

MIT — see [LICENSE](LICENSE). **Technical preview:** private repository, no public release, no verified external installations or user adoption. Sensitive security issues should not be disclosed via public issue comments; see [SECURITY.md](SECURITY.md).
