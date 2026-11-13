# Security policy

DeployProof is a small open-source learning project and is not yet a production release.

## Reporting a vulnerability

Do **not** publish exploit details, credentials or private repository information in public GitHub issues or comments. If GitHub's private vulnerability reporting is enabled for this repository, use that channel. Otherwise, contact the repository owner privately through GitHub and share only the minimum information needed to coordinate a secure report. No external security contact address is currently advertised.

## Trust boundaries

- The public JSON manifest is **not signed**. Checking identity strings does not establish cryptographic authenticity or prove other deployed assets are fresh.
- The verifier intentionally accepts only HTTPS GitHub Pages subdomains and relative manifest paths; redirects are rejected.
- Treat build IDs and source commit SHAs as **public** when putting them into a public Pages manifest.
- Never put GitHub tokens, credentials, private URLs, or personal data into manifests, workflow outputs or verbose logs.
- Workflow permissions should be minimal, and external Actions pinned to reviewed full commit SHAs.
- Keep in mind a new legitimate deployment can replace a previously expected manifest, producing a mismatch without a site malfunction.

## Supported preview scope

Python 3 on a GitHub Actions hosted Ubuntu runner, serving a static manifest on https://*.github.io/ without a custom domain. Local and GitHub Pages E2E tests do not cover all DNS, proxy, browser, cache and CDN behaviors.
