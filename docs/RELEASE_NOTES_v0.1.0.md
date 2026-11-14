# DeployProof v0.1.0 — Initial public technical preview

**Action display name:** GitHub Pages Build Identity Check (owner-approved; repository slug remains `eluyz/deployproof`).

**Release type:** Initial technical preview (open-source learning project).

DeployProof checks whether a live GitHub Pages website serves the deployment identity created by a specific build. It compares a small public JSON manifest with four trusted values originating in the build job: `git_sha`, `workflow_run_id`, `run_attempt` and `build_id`.

## Features
- Reusable composite GitHub Action with no third-party Python dependencies.
- Exact pass/fail result exposed as `steps.<id>.outputs.verdict`.
- Clear diagnostics for wrong build, missing or invalid manifest, HTTP/network error and invalid configuration.
- Bounded retries for eventual Pages propagation, no cross-host redirects, strict HTTPS github.io URL checks.
- SHA-pinned GitHub Actions example, build-provenance-safe even when deployment jobs are rerun.

## Verification evidence (scoped)
- GitHub Actions unit/local HTTP suite: 23/23 PASS, run: https://github.com/eluyz/deployproof/actions/runs/43515181573
- Real public GitHub Pages E2E: PASS_IDENTITY and intentional mismatches/404 detected; run: https://github.com/eluyz/deployproof/actions/runs/43515181535
- Pinned full-SHA Action reference from its **own repository**: PASS (tested before source became public).
- Independent **cross-repository** installation: NOT TESTED.

## Explicit limitations

A matching manifest is NOT proof that HTML/JS/CSS/data files are the newest versions, nor that an artifact is cryptographically signed. GitHub Pages custom domains are outside the supported scope; a newer legitimate deployment can produce a mismatch. Public manifest metadata is visible to anyone. No external user adoption is known.

## Public distribution

The repository is public under MIT, with the distinct Action display name **GitHub Pages Build Identity Check**. This version is a **prerelease** to reflect its limited scope and absence of verified independent installations. External cross-repository installation: **NOT TESTED**. A GitHub Marketplace listing has **NOT** been published; it is optional and requires additional steps.
