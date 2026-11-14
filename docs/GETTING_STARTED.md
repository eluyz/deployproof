# Getting started with GitHub Pages Build Identity Check

DeployProof checks whether the **publicly served GitHub Pages build identity**
matches the identity written into the build artifact **before upload**.

**Supported:** standard GitHub Pages `https://OWNER.github.io/` and
`https://OWNER.github.io/REPO/` sites, Python 3 on a GitHub Actions runner.
**Not supported:** custom domains, redirects, complete asset integrity, signed
artifacts or a browser smoke test. This is a `v0.1.0` technical preview.

## First real deployment — four steps

1. In your website repository, select **Settings → Pages → Build and deployment
   → Source: GitHub Actions**. Confirm the expected public site root:
   `https://OWNER.github.io/REPO/` for a project site, with the trailing slash.
2. Open the [complete Pages example](../examples/pages-deploy-and-verify.yml).
   Copy it to `.github/workflows/pages.yml` **in your own website repository**.
   Replace the illustrative HTML-building step with your real build, which
   must write to `dist/`. If your build output directory differs, update both
   the manifest path and upload path consistently.
3. Replace `YOUR_USERNAME` and `YOUR_REPOSITORY` with the actual Pages
   address. Replace the `uses` placeholder with the reviewed release SHA:

   ```yaml
   uses: eluyz/deployproof@1c03c9d4ace3855bf12fc7672c6d6a60cc072b8f
   ```

   Keep the four expected values wired to `needs.build.outputs` as in the
   sample. **Do not** derive expected identity from the deployed JSON itself:
   that would only compare the site against its own untrusted claim.
4. Commit the workflow and inspect its GitHub Actions run. The `build`
   job should generate `dist/deployproof.json` before artifact upload; the
   deployment job should serve that file at
   `https://OWNER.github.io/REPO/deployproof.json`, then return
   **`IDENTITY_PASS`** from the verifier. Confirm the manifest in a browser.

The complete example has been syntax-checked, and its manifest generator
executed offline with simulated build attempts 1 and 2. Our own synthetic
GitHub Pages E2E and a **separate owner-controlled repository installation
smoke** passed. A full real customer website integration remains
**unverified**. Expect to adjust the template for your build system.

## What the result means

| Verdict | Meaning / next check |
| --- | --- |
| `IDENTITY_PASS` | Four public manifest identity fields match the trusted build job outputs. **Not** asset integrity. |
| `VERSION_MISMATCH` | Served manifest differs from the expected build. Check whether another deployment replaced it or the verifier job was retried. |
| `MISSING_MANIFEST` | Public URL returned 404. Ensure `deployproof.json` is in the artifact root and the `/REPO/` base path is right. |
| `INVALID_MANIFEST` | JSON is invalid, too large, has duplicate keys or lacks required string fields. |
| `INVALID_CONFIG` | Fix inputs, HTTPS `*.github.io` URL, trailing slash, or relative manifest path. |
| `NETWORK_ERROR` / `HTTP_ERROR` | Investigate public reachability, timeouts, HTTP status or redirects. |

A matching manifest can coexist with **stale JS, CSS, images or data**. To
check those, add file hashes, real HTTP asset checks or browser tests
separately. DeployProof does not currently provide those guarantees.

## Common deployment mistakes

- **Wrong build attempt:** when rerunning only the deployment/verification
  job, GitHub's current `run_attempt` can differ from the attempt that
  produced the uploaded artifact. Use the **build job outputs** in the
  complete example, not `github.run_attempt` from the verifier job.
- **Wrong Pages base URL:** a project repo normally publishes under
  `/REPO/`; root `https://OWNER.github.io/` is not equivalent.
- **Hidden manifest:** use a flat `deployproof.json` at the upload root.
  Hidden paths can be omitted by Pages artifact upload options.
- **Custom domain or redirects:** this preview intentionally rejects
  non-`github.io` hosts and does not follow redirects; use the canonical
  GitHub Pages hostname for the check.
- **Private build metadata:** public Pages manifests expose SHA, run ID,
  attempt and build ID. Do not put secrets, tokens or private data there.

## Trial installation versus real verification

For an installation-only smoke test in a separate disposable repo, use
[consumer-install-smoke.yml](../examples/consumer-install-smoke.yml).
It deliberately reads **expected values from the public synthetic fixture**,
which is only acceptable for testing the Action's packaging/transport.
It does **not** prove the identity of a real build. Never copy that fixture
approach into a production verifier.

## Help and feedback

- [Report a reproducible bug](https://github.com/eluyz/deployproof/issues/new?template=bug_report.yml)
- [Describe a real use case or onboarding obstacle](https://github.com/eluyz/deployproof/issues/new?template=use_case.yml)
- [Contribution guidance](../CONTRIBUTING.md) and [security policy](../SECURITY.md)

Issues are **public**. Redact secrets, private URLs, private workflow logs
and personal data. Report sensitive vulnerabilities via the private-security
guidance, not a public issue. We do not collect telemetry through this Action.
