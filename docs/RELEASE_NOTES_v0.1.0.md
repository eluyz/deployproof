# DeployProof v0.1.0 — release draft (NOT PUBLISHED)

**Release type:** Initial technical preview (open-source learning project).

DeployProof checks whether a live GitHub Pages website serves the deployment identity created by a specific build. It compares a small public JSON manifest with four trusted values originating in the build job: `git_sha`, `workflow_run_id`, `run_attempt` and `build_id`.

## Features
- Reusable composite GitHub Action with no third-party Python dependencies.
- Exact pass/fail result exposed as `steps.<id>.outputs.verdict`.
- Clear diagnostics for wrong build, missing or invalid manifest, HTTP/network error and invalid configuration.
- Bounded retries for eventual Pages propagation, no cross-host redirects, strict HTTPS github.io URL checks.
- SHA-pinned GitHub Actions example, build-provenance-safe even when deployment jobs are rerun.

## Verification evidence (internal)
- GitHub Actions unit/local HTTP suite: 23/23 PASS, run: https://github.com/eluyz/deployproof/actions/runs/43515181573
- Real public GitHub Pages E2E: PASS_IDENTITY and intentional mismatches/404 detected; run: https://github.com/eluyz/deployproof/actions/runs/43515181535
- Pinned commit Action reference from its **own private repository**: PASS.
- Independent **cross-repository** installation: NOT TESTED.

## Explicit limitations

A matching manifest is NOT proof that HTML/JS/CSS/data files are the newest versions, nor that an artifact is cryptographically signed. GitHub Pages custom domains are outside the supported scope; a newer legitimate deployment can produce a mismatch. Public manifest metadata is visible to anyone. No external user adoption is known.

## Publication checklist

This file is a **draft**, not a release. Before publishing: confirm MIT licensing and project/action name, review repository history for sensitive content, change visibility to public, test installation from a separate repository, create an immutable/reviewed v0.1.0 tag and publish GitHub release. GitHub Marketplace distribution is optional and subject to its separate agreements/requirements.
