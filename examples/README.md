# Full workflow example

For the public v0.1.0 preview, the example **already pins** the Action to its
published full SHA:

`uses: eluyz/deployproof@1c03c9d4ace3855bf12fc7672c6d6a60cc072b8f`

The exact SHA corresponds to [v0.1.0](https://github.com/eluyz/deployproof/releases/tag/v0.1.0). An independent, owner-controlled private-repository **installation smoke test passed on 2026-11-14**, but this workflow example itself has not been run as a full build-and-deploy pipeline in that repository.

[pages-deploy-and-verify.yml](pages-deploy-and-verify.yml) demonstrates how to build a static site, create a public `deployproof.json`, upload it, deploy with GitHub Pages, and compare the **published artifact's** identity against trusted build job outputs.

**This is a template, not a fully configured production workflow, and not a
tested third-party *site deployment*.** The Action reference is pinned to the
reviewed [v0.1.0 commit](https://github.com/eluyz/deployproof/releases/tag/v0.1.0).
You still must adapt the demonstration build and site URL to your repository.
A separate owner-controlled installation smoke passed, but the complete
build-and-deploy workflow has not been tested in a different user's site.

To adapt it:

1. Enable **Settings → Pages → Build and deployment → Source: GitHub Actions** in the website repository.
2. Copy the example into that repository as `.github/workflows/pages.yml`.
3. Replace the demonstration HTML build step with the real build that writes to `dist/`; keep identity generation **after the build and before artifact upload**.
4. Replace `YOUR_USERNAME` and `YOUR_REPOSITORY` with your real values. The
   Action is already pinned to the reviewed v0.1.0 commit; update that SHA
   only after reviewing a future release.
5. Keep all expected IDs sourced from `needs.build.outputs`, not the verification job's `github.run_attempt`. Failed-job reruns may otherwise report a false mismatch.
6. Confirm the public manifest is reachable at `https://YOUR_USERNAME.github.io/YOUR_REPOSITORY/deployproof.json` and inspect the actual run logs.

The Action verifies **deployment identity only**, not individual JS/CSS/data assets. The manifest's SHA and workflow IDs are **public metadata** even for a private source repository. Never include secrets.

Validated against our **same-repository synthetic E2E tests**: [run 43515181535](https://github.com/eluyz/deployproof/actions/runs/43515181535). A separate owner-controlled repository installation smoke has now passed; the complete build-and-deploy example remains independently untested.


## Validating this template

CI parses the example with PyYAML 6.0.3 and executes its identity-generation
script with synthetic build IDs, including a rerun attempt. PyYAML is a
**test-only** dependency: DeployProof itself uses only Python's standard library.

Development validation commands:

    python3 -m pip install PyYAML==6.0.3
    python3 scripts/validate_release_example.py

These checks establish YAML parsing and generated identity behavior, **not**
a successful installation from a different public repository.

## Independent repository installation smoke (DP-M2-01)

[consumer-install-smoke.yml](consumer-install-smoke.yml) is a complete
**ready-to-copy workflow for a separate, empty test repository**. It checks
that the public, SHA-pinned `v0.1.0` Action can be downloaded and invoked
outside its source repository, then deliberately produces
`VERSION_MISMATCH` and `MISSING_MANIFEST` to verify exact errors.

To run it:

1. Create a separate private test repository named `deployproof-consumer-test`
   under your own GitHub account, with **no README, license or .gitignore**.
   Do not add this workflow to an unrelated existing project.
2. Copy the file into `.github/workflows/deployproof-consumer-smoke.yml`
   on the test repository's `main` branch. The initial push triggers the run;
   you can also use **Actions → DeployProof independent-repository installation
   smoke → Run workflow**.
3. Verify the external GitHub Actions run has a successful positive case
   and two deliberately failing Action steps whose verdict assertions pass.
   Save the exact run URL, source repository, commit SHA and status.
4. **DP-M2-01 DONE on 2026-11-14.** The real consumer-repository [run 43600664871](https://github.com/eluyz/deployproof-consumer-test/actions/runs/43600664871) passed (private run, visible to authorized collaborators). Its logs show external Action download at the reviewed v0.1.0 SHA, `IDENTITY_PASS`, expected `VERSION_MISMATCH` and `MISSING_MANIFEST` failures, with assertion steps succeeding.

The workflow reads expected values directly from our **public synthetic**
`deployproof.json` to exercise **installation and invocation only**. Those
values are **not trusted build provenance** and using them would be wrong
for verifying a real deployment. For production usage, generate the expected
values from the *trusted build job* as shown in
[pages-deploy-and-verify.yml](pages-deploy-and-verify.yml).

It requires no GitHub Pages configuration, no credentials, no write token,
no repository secrets and no checkout in the consumer repository. The Action
reference is the fully pinned, reviewed `v0.1.0` release SHA. The public
fixture may change after another Pages test deployment; rerun the smoke
check if a concurrent deployment causes a mismatch.

The workflow's YAML and fixture-loading step are tested **offline** in
DeployProof CI (with a local HTTP fixture). That is not equivalent to running
the Action in a separate GitHub repository.


### Maintainer smoke-test evidence (2026-11-14)

Owner-created **private** repository `eluyz/deployproof-consumer-test` ran the
standalone workflow under `.github/workflows/deployproof-consumer-smoke.yml`.
The independent runner downloaded `eluyz/deployproof@1c03c9d4ace3855bf12fc7672c6d6a60cc072b8f`.
The job completed **SUCCESS** with exact verdicts `IDENTITY_PASS`,
`VERSION_MISMATCH`, and `MISSING_MANIFEST`. The two intentionally
failing Action steps exited nonzero and were verified by assertions.
[Workflow run](https://github.com/eluyz/deployproof-consumer-test/actions/runs/43600664871)
(private; not publicly viewable). The fixture identity is deliberately read
from public test data and must **never** be used as proof of trusted
production build provenance. An owner-run smoke test does **not** establish
outside adoption.
