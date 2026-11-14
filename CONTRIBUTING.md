# Contributing to DeployProof

Thanks for helping improve a small open-source GitHub Pages deployment
**identity checker**. This project is an early technical preview; scope and
limitations are documented in [Getting Started](docs/GETTING_STARTED.md).

## Getting help or proposing a change

- First try the documented [Getting Started](docs/GETTING_STARTED.md)
  workflow and check [existing issues](https://github.com/eluyz/deployproof/issues).
- For incorrect behavior, open a [bug report](https://github.com/eluyz/deployproof/issues/new?template=bug_report.yml)
  with the exact verdict, minimal steps and **redacted** non-sensitive log
  snippets.
- For feedback, open a [use case / onboarding report](https://github.com/eluyz/deployproof/issues/new?template=use_case.yml).
  Say whether you actually used the Action on your own Pages deployment, only
  tried the synthetic smoke test, or merely read the docs. These are **different
  forms of evidence**; no user or installation counts are inferred from stars.
- For sensitive security reports, follow [SECURITY.md](SECURITY.md).
  **Never** paste tokens, private logs or exploit details into a public issue.

## Development

DeployProof's runtime uses Python's standard library. On a suitable Python 3
environment, run:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts tests
```

The separate CI-only YAML/template validators use pinned
`PyYAML==6.0.3`, installed by the GitHub Actions test workflow. Source
code, tests and documentation should remain in English. Prefer focused
changes with tests; do not weaken input validation, runner permissions or
the separation between **trusted build outputs** and public manifest content.

Before opening a pull request, explain what changes, link to a related
issue when appropriate, and include test evidence or identify what was
not tested. Maintainers evaluate changes against the narrowly supported
GitHub Pages scope and do not guarantee a response deadline.
