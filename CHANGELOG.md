# Changelog

## [Unreleased] — planned v0.1.0 (not published)

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

The repository remains private and no v0.1.0 tag or GitHub release has been created. This changelog documents a candidate, not a released product.
