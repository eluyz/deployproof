# Full workflow example

[pages-deploy-and-verify.yml](pages-deploy-and-verify.yml) demonstrates how to build a static site, create a public `deployproof.json`, upload it, deploy with GitHub Pages, and compare the **published artifact's** identity against trusted build job outputs.

**This is a template, not a fully configured production workflow and not a tested third-party installation.** DeployProof is private and has no published release yet, so `uses: eluyz/deployproof@REPLACE_WITH_REVIEWED_RELEASE_COMMIT_SHA` is intentionally unresolved.

To try it **after publication**:

1. Enable **Settings → Pages → Build and deployment → Source: GitHub Actions** in the website repository.
2. Copy the example into that repository as `.github/workflows/pages.yml`.
3. Replace the demonstration HTML build step with the real build that writes to `dist/`; keep identity generation **after the build and before artifact upload**.
4. Replace `YOUR_USERNAME`, `YOUR_REPOSITORY`, and the Action commit SHA with your real values.
5. Keep all expected IDs sourced from `needs.build.outputs`, not the verification job's `github.run_attempt`. Failed-job reruns may otherwise report a false mismatch.
6. Confirm the public manifest is reachable at `https://YOUR_USERNAME.github.io/YOUR_REPOSITORY/deployproof.json` and inspect the actual run logs.

The Action verifies **deployment identity only**, not individual JS/CSS/data assets. The manifest's SHA and workflow IDs are **public metadata** even for a private source repository. Never include secrets.

Validated against our **same-repository synthetic E2E tests**: [run 43515181535](https://github.com/eluyz/deployproof/actions/runs/43515181535). Copying into an independent repository has **not** yet been tested.


## Validating this template before publication

CI parses the example with PyYAML 6.0.3 and executes its identity-generation
script with synthetic build IDs, including a rerun attempt. PyYAML is a
**test-only** dependency: DeployProof itself uses only Python's standard library.

Development validation commands:

    python3 -m pip install PyYAML==6.0.3
    python3 scripts/validate_release_example.py

These checks establish YAML parsing and generated identity behavior, **not**
a successful installation from a different public repository.
