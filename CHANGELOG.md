# Changelog

## [Unreleased] — main development (not in v0.1.0)

### Fixed

- Retry temporary HTTP 408, 429, 500, 502, 503 and 504 responses using the existing bounded attempt, delay and timeout settings; keep HTTP 403 and redirects fail-fast.
- Limit live GitHub Pages E2E deployment to the `main` branch and rerun it when verifier code changes. This prevents preview branches from overwriting the shared public test site.
- Added seven HTTP regression tests (30 total on `main`) and verified the current code against real GitHub Pages E2E: [CI](https://github.com/eluyz/deployproof/actions/runs/43822142520), [Pages E2E](https://github.com/eluyz/deployproof/actions/runs/43822142502).

**Release notice:** These retry changes are only on `main`. The published
`v0.1.0` prerelease is immutable and still points to
`1c03c9d4ace3855bf12fc7672c6d6a60cc072b8f`.
Consumers pinned to `v0.1.0` do **not** receive the new retry behavior.
No subsequent version has been released.

## [0.1.0] — Initial public technical preview (2026-11-14)

### Added

- GitHub Pages deployment identity checker as a zero-third-party-Python-dependency composite GitHub Action.
- Public `deployproof.json` comparison of source SHA, build workflow run ID, build attempt and build ID.
- Machine-readable output `verdict`, with explicit IDENTITY_PASS, VERSION_MISMATCH, MISSING_MANIFEST and error categories.
- Strict github.io URL checks, blocked redirects, bounded HTTP retries, input validation, JSON size limit and duplicate-key rejection.
- GitHub Actions test suite (23 local HTTP/unit tests) and synthetic real GitHub Pages E2E checks, including rerun regression.
- A complete example workflow, MIT license and security disclosure guidance.

### Known limits

- Identity match is not asset integrity, signature verification or a browser smoke test.
- Only direct HTTPS *.github.io sites are supported; custom domains and redirect-based addresses are unsupported.
- A public Action invoked from a DIFFERENT repository is not yet tested.
- No community adoption has been verified.

### Release status

See [GitHub Releases](https://github.com/eluyz/deployproof/releases) for the actual versioned release and exact tag SHA. This is an identity-only technical preview; independent third-party installation is not yet verified.
