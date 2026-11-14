#!/usr/bin/env python3
"""CI-only review of public onboarding links and GitHub issue-form schemas."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ISSUES = ROOT / ".github" / "ISSUE_TEMPLATE"
FORMS = ("bug_report.yml", "use_case.yml")


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def main() -> None:
    for filename in FORMS:
        document = yaml.safe_load((ISSUES / filename).read_text(encoding="utf-8"))
        require(isinstance(document, dict), f"invalid YAML mapping: {filename}")
        for key in ("name", "description", "title", "body"):
            require(document.get(key), f"missing {key}: {filename}")
        body = document["body"]
        require(isinstance(body, list) and len(body) >= 4,
                f"empty issue form body: {filename}")
        ids = set()
        safety = False
        for item in body:
            kind = item.get("type")
            require(kind in ("markdown", "dropdown", "textarea", "checkboxes"),
                    f"unknown issue form type: {kind}")
            require(isinstance(item.get("attributes"), dict), "missing form attributes")
            if kind != "markdown":
                ident = item.get("id")
                require(isinstance(ident, str) and ident not in ids,
                        f"duplicate or missing issue field id: {filename}")
                ids.add(ident)
                require(item["attributes"].get("label"), f"missing field label: {ident}")
            if kind == "checkboxes" and item.get("id") == "safety":
                options = item["attributes"].get("options", [])
                require(options and options[0].get("required") is True,
                        "public-issue safety checkbox must be required")
                safety = True
        require(safety, f"missing safety acknowledgement: {filename}")
        print(f"PASS: GitHub issue form YAML fields and privacy checkbox: {filename}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    quickstart = (ROOT / "docs" / "GETTING_STARTED.md").read_text(encoding="utf-8")
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    for doc_name, source in (("README.md", readme), ("GETTING_STARTED.md", quickstart),
                             ("CONTRIBUTING.md", contributing)):
        require("SECRET" not in source, "unexpected example secret placeholder")
        require("IDENTITY_PASS" in source or "identity" in source.lower(),
                f"missing scope language: {doc_name}")
    for linked in ("docs/GETTING_STARTED.md", "CONTRIBUTING.md"):
        require(linked in readme, f"README missing navigation: {linked}")
    for template in FORMS:
        require(f"template={template}" in readme or f"template={template}" in quickstart,
                f"missing public feedback link: {template}")
    require("needs.build.outputs" in quickstart, "source of trusted identity not documented")
    require("not" in quickstart.lower() and "asset" in quickstart.lower(),
            "identity-only boundary not documented")
    require("1c03c9d4ace3855bf12fc7672c6d6a60cc072b8f" in quickstart,
            "quickstart must pin reviewed v0.1.0 SHA")
    print("PASS: onboarding navigation, trusted build outputs, SHA and scope checks")


if __name__ == "__main__":
    main()
