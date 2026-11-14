# v0.1.0 release gate (internal; NOT a release)

Status: **v0.1.0 PUBLIC PRERELEASE VERIFIED — RELEASE GATE PASSED FOR SCOPED TECHNICAL PREVIEW**. Cross-repository consumer installation remains **NOT TESTED**, and asset-integrity verification is outside scope.

Owner approved public visibility, MIT and display name **GitHub Pages Build Identity Check** on 2026-11-14. Repository visibility was independently verified as **PUBLIC** on 2026-11-14. This does not prove cross-repo installation.

Security-review scope: checked all 11 reachable main commits' changed-file lists,
22 historical changed-file contents and all 15 current candidate blobs for
common high-risk credential signatures (GitHub PAT/classic tokens, AWS access
keys, OpenAI-style keys, Slack tokens and private-key PEM headers). No
signatures matched. **This is a targeted pattern review, not proof that the
history is secret-free.** GitHub Actions workflow permissions and published
Pages manifest metadata require a final owner check before making the
repository public.

| Check | Evidence or status |
| --- | --- |
| Product scope: GitHub Pages identity-only | PASS — README and SECURITY.md explicitly state limits |
| Unit/local HTTP suite | PASS — 23 tests on GitHub CI, run 43515181573 |
| Actual Pages E2E | PASS — run 43515181535 |
| Release example YAML and manifest generation | PASS — PR CI 43518247242 on da289d68: PyYAML parse, synthetic build attempts 1 and 2, trusted job outputs |
| Rerun provenance | PASS — build outputs preserved across verifier job reruns; run 43506480136 |
| SHA-pinned Action reference in same private repo | PASS — run 43515181535 |
| External repo invokes public Action | **NOT TESTED** — no separately authorized consumer repo available; disclose explicitly in initial prerelease |
| MIT license choice | APPROVED 2026-11-14 — standard MIT file staged; publishing is not complete |
| Public repository and history review | PUBLIC verified; PARTIAL targeted history scan (11 main commits, 22 historical file versions, 15 release-candidate blobs), no common credential signatures detected. Not a comprehensive secrets audit |
| Trademark / existing project name overlap | MITIGATED — owner approved a distinct Action display name: GitHub Pages Build Identity Check; another project uses DeployProof. No legal clearance implied |
| Third-party security penetration test | NOT RUN — not promised for preview; explicit known limitations |
| GitHub version tag v0.1.0 | VERIFIED — tag resolves to `1c03c9d4ace3855bf12fc7672c6d6a60cc072b8f` (release commit) |
| Public GitHub Release | VERIFIED — [v0.1.0 prerelease](https://github.com/eluyz/deployproof/releases/tag/v0.1.0), GitHub release ID 445256970, published 2026-11-14 |
| GitHub Marketplace listing | NOT CREATED — optional after separate owner acceptance |

## Publication controls (historical approval confirmed)

1. Obtain explicit approval of MIT text and the public repository/name choice. Recheck the Action metadata `name` for Marketplace uniqueness; do not assume `DeployProof` is available.
2. Audit code, config, history and generated artifacts for secrets, private data, proprietary code and unintended personal identifiers.
3. Keep GitHub workflows, code, docs and release text in English. Update README with the actual published Action ref, license and release status.
4. Make the repository public in GitHub Settings only when authorized. This is not reversible with respect to previously downloaded code.

## After visibility changes

1. Pin the exact reviewed **release commit SHA**. Create a separate disposable consumer repository controlled by the owner (or use an authorized existing test repo); run the full example with `uses: OWNER/REPO@FULL_SHA`.
2. Verify the external workflow **downloads the Action** and reports IDENTITY_PASS, intentionally mismatching build ID and missing manifest. Include run links. Do not claim this before execution.
3. Finalize the versioned tag (`v0.1.0`) and release notes. Make sure release contents and tag SHA match the tested code.
4. Publish a GitHub release. Marketplace publication is optional and requires a **public repository**, a unique action metadata name, Marketplace terms, and release publication; do not assert acceptance without actual UI evidence.
5. Leave a verifiable link in project docs and track real uptake separately from release success.

If the third-party test is unavailable, label it as NOT TESTED in the release instead of silently calling it PASS. If name collision creates ambiguity, consider a distinct descriptive name such as "Pages Build Identity Check"; do not rename the repo/product without a recorded owner decision.

References:
- https://docs.github.com/en/actions/how-tos/create-and-publish-actions/publish-in-github-marketplace
- https://docs.github.com/en/actions/how-tos/create-and-publish-actions/release-and-maintain-actions

## Publication result — 2026-11-14 (verified)

- PUBLIC source repository: https://github.com/eluyz/deployproof
- Published **prerelease**, not GA: https://github.com/eluyz/deployproof/releases/tag/v0.1.0
- GitHub release id: 445256970; tag `v0.1.0` resolves exactly to `1c03c9d4ace3855bf12fc7672c6d6a60cc072b8f`
- CI-gated release run completed SUCCESS: https://github.com/eluyz/deployproof/actions/runs/43591619368
- Last main CI on release commit completed SUCCESS: https://github.com/eluyz/deployproof/actions/runs/43591619325
- Release includes explicit independent cross-repository installation: **NOT TESTED**
- Follow-up v0.1.0 SHA-pinned same-repo public Pages E2E: **PASS** — [run 43591796418](https://github.com/eluyz/deployproof/actions/runs/43591796418). Four expected result lines: `IDENTITY_PASS` for current source and pinned public v0.1.0 Action, `VERSION_MISMATCH` for intentionally wrong build ID, `MISSING_MANIFEST` for deliberately absent file; exact verdict assertions passed.
- GitHub Marketplace listing NOT submitted. No external users or adoption confirmed.

## Final scoped release decision — 2026-11-14

**GO_RELEASE / initial public prerelease only.** Preconditions verified:

- Repository is publicly visible; owner approved MIT and the distinct Action name.
- [Release publication workflow](https://github.com/eluyz/deployproof/actions/runs/43591619368) completed SUCCESS and proved public anonymous source access, 23 tests, correct generated manifest and metadata.
- GitHub [v0.1.0 release](https://github.com/eluyz/deployproof/releases/tag/v0.1.0) exists, is public, not a draft, and is explicitly flagged as **prerelease**; lightweight tag SHA equals the vetted release commit.
- Source-control follow-up [CI](https://github.com/eluyz/deployproof/actions/runs/43591796369) is green; [GitHub Pages E2E](https://github.com/eluyz/deployproof/actions/runs/43591796418) is green using a pinned `v0.1.0` Action commit SHA.
- **Independent consumer repository Action invocation = NOT TESTED**. Do not conflate same-repository remote Action invocation or anonymous source access with cross-repository installation.
- **User adoption = 0 verified; demand unknown.** GitHub Marketplace was not listed.
- `IDENTITY_PASS` checks only the deployment identity manifest; no guarantee about individual HTML/JS/CSS/data asset integrity, hashes or cryptographic proof.

These guardrails are intentional for a learning-first public technical preview. This is not a production security certification or unrestricted GO for a complete deployment-integrity product.
