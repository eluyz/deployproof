# GitHub Marketplace publication readiness — DeployProof

**Status: PREPARED, NOT PUBLISHED (2026-11-17).**

This checklist is for the **GitHub Action** named
**GitHub Pages Build Identity Check**, distributed from
[`eluyz/deployproof`](https://github.com/eluyz/deployproof).
It is not a paid GitHub App listing, a product-market-fit claim, or
permission to accept agreements on the owner's behalf.

## 1. Reconciled preflight evidence

| Check | Observed status | Evidence / limitation |
| --- | --- | --- |
| Public repository | **PASS** | GitHub repository API reports `public` |
| Exactly one Action metadata file in repository root | **PASS** | Recursive Git tree: `action.yml` only; no root `action.yaml` |
| Action name/description | **PRESENT** | `action.yml` name: `GitHub Pages Build Identity Check`; description specifies a Pages manifest and expected build identity |
| Branding | **PRESENT** | `check-circle` icon and blue color in `action.yml` |
| License | **PRESENT** | MIT `LICENSE`; this is not a legal review |
| Versioned GitHub Release | **PASS** | [`v0.1.0`](https://github.com/eluyz/deployproof/releases/tag/v0.1.0), public **prerelease**, not draft; exact commit `1c03c9d4ace3855bf12fc7672c6d6a60cc072b8f` |
| Source branch checks | **PASS (scoped)** | [main CI](https://github.com/eluyz/deployproof/actions/runs/43832712065): 33 local/unit HTTP tests plus CI document/fixture checks; [real Pages E2E](https://github.com/eluyz/deployproof/actions/runs/43822142502) passed on earlier `main` code |
| Cross-repository Action installation | **PASS (owner smoke only)** | [private owner consumer run](https://github.com/eluyz/deployproof-consumer-test/actions/runs/43600664871): successfully downloaded and invoked the SHA-pinned Action; run details not public |
| Verified third-party Pages deployments | **NOT VERIFIED** | No independent user's real build-and-deploy evidence |
| Marketplace name uniqueness | **NOT VERIFIED** | Only GitHub's Release Action publisher can confirm name eligibility; public search is insufficient |
| Marketplace Developer Agreement / owner 2FA | **NOT VERIFIED** | Only the authenticated owner can review and satisfy these account requirements |
| Marketplace listing and category | **NOT PUBLISHED** | No Marketplace-linked release or public listing verified |

**Known conflict risk:** An unrelated Marketplace Action has used the
product name `DeployProof`. Our **Action metadata display name** is different,
but this does **not** prove Marketplace name eligibility, trademark clearance
or permission to use someone else's branding. Do not rename to a potentially
conflicting name without checking the GitHub publisher.

## 2. Critical release/source distinction

The existing public `v0.1.0` tag still points to
`1c03c9d4ace3855bf12fc7672c6d6a60cc072b8f`.
That version retries HTTP 404, network errors and version mismatch.
It does **not** retry 408, 429, 500, 502, 503 or 504.

On `main`, bounded retries for these transient HTTP statuses were added
after the initial release; the current CI has **33 passing tests** and
the current-source Pages E2E passed. **This newer behavior is not in
`v0.1.0`** and must not be advertised as already released.

**Release choice requires owner review before publication:**

- **Reuse v0.1.0**, *only if* GitHub's authenticated UI permits
  attaching its existing prerelease to Marketplace without a new release.
  Describe the exact historical feature set; do not claim main-only fixes.
- **Publish a later patch version**, *only after* a separate release gate:
  check exact source SHA, rerun all CI and live Pages E2E, reconcile release
  notes and SHA-pinned examples, publish an actual versioned GitHub Release,
  and verify that tag and Marketplace status. Do not move or retarget
  `v0.1.0`, and do not invoke the prior auto-release workflow blindly.

GitHub's current official instructions describe going to `action.yml` and
using **Draft a release → Publish this Action to GitHub Marketplace**.
They do not establish in this audit whether an *existing prerelease* can
be retroactively listed. Check the actual authenticated UI before choosing.

## 3. Marketplace positioning: no invented uniqueness

**Suggested title (existing metadata):** GitHub Pages Build Identity Check

**One-sentence description:** Compare the publicly served GitHub Pages
build-identity manifest with four trusted build-job values after deployment.

**What it actually verifies:** `git_sha`, `workflow_run_id`,
`run_attempt` and `build_id` as exact JSON strings, with bounded retries,
unambiguous verdicts and strict GitHub Pages URL restrictions.

**What it does not verify:** Individual HTML/JS/CSS/data asset integrity,
signed provenance, arbitrary custom domains, CDN-wide freshness, successful
publication when the Pages service is blocked, or real user demand.

**Competitor caveat:** [Verify Deployment](https://github.com/marketplace/actions/verify-deployment)
already supports an `expected-content` HTTP check. With a unique build-ID
marker, it may detect a stale same-SHA attempt as well. Our exact four-field
comparison gives clearer semantics at the cost of an extra manifest and
build-job wiring. Read [Product Validation](PRODUCT_VALIDATION.md). This
difference has not been established as a strong user preference.

**Ideal initial audience:** Maintainers with GitHub Pages Actions pipelines
who want a strict check of the **identity manifest** served after a deploy,
and can generate that manifest from trusted build outputs.

## 4. Owner-only publication steps (DO NOT EXECUTE AUTOMATICALLY)

1. Open the [repository's `action.yml`](https://github.com/eluyz/deployproof/blob/main/action.yml)
   in the authenticated GitHub web interface. Locate the Marketplace
   publishing banner and choose **Draft a release**.
2. Review the **Release Action** validation; confirm GitHub accepts the
   current unique `name`. Do not assume availability from a search.
3. Personally review and accept the **GitHub Marketplace Developer
   Agreement**, if not already accepted, and complete GitHub's required
   **two-factor authentication**. No assistant acceptance is implied.
4. Inspect the version controls: determine whether the existing
   `v0.1.0` prerelease is eligible for Marketplace or a **new,
   separately approved, tested version** is necessary. Never create
   or retarget a release solely to pass a UI check.
5. Choose the most relevant **Primary Category** offered by the live
   GitHub publisher; any second category is optional. Category labels
   in the owner UI, not this document, are authoritative.
6. Review the actual release notes, MIT license, limitations and
   public installation instructions **before** checking the
   **Publish this Action to GitHub Marketplace** box.
7. After deliberate publication, independently confirm the Marketplace
   page URL, displayed release version, public Action metadata name,
   installation reference and source commit SHA. Save those links
   in the project journal. If no listing is created, keep
   `MARKETPLACE_NOT_PUBLISHED`.

[Official GitHub instructions](https://docs.github.com/en/actions/how-tos/create-and-publish-actions/publish-in-github-marketplace)
describe public/single-root-action/unique-name requirements and
authenticated release publishing.

## 5. Discovery experiment: measurement, not assumed adoption

**Pre-publication baseline, 2026-11-17:** 1 repository star, 0 forks,
0 non-pull-request issues and **0 independently verified user
deployments**. The source README and issue forms are public. GitHub Traffic
views/clones/referrers are **N/D** to this audit, not zero.

If the owner approves a targeted Marketplace listing, record **the actual
publication date and URL** and revisit after a consistent short interval
(e.g. 14 days):

- **Awareness only:** GitHub Insights → Traffic (14-day views, unique
  visitors, clones, referrers), stars, forks. These are *not* users.
- **Feedback/intent:** real independent issue/PR or public response
  containing an explicit stage: documentation only, test installation,
  real GitHub Pages deployment, or problem encountered.
- **Verified adoption:** a non-owner's publicly inspectable GitHub
  Actions run or independently verifiable example using the released
  Action with a real website. Private self-reports must be labeled
  unverified and must not expose credentials.
- **Value signal:** meaningful repeated real deployment use or a
  reported debugging improvement compared to a generic build-ID probe.

Do not add telemetry to the Action, fabricate installs or require a fixed
quota of pilots. No monitoring or reminder has been scheduled by writing
this document.

## Decision gates

- **GO_PREPARE:** requirements documented, source/release distinctions
  verified, CI evidence recorded, and install guidance available.
- **BLOCKED_TO_PUBLISH:** Marketplace unique name availability, owner
  agreement/2FA, eligible release selection and owner approval not
  confirmed in this audit.
- **NO-GO to new features by default:** no verified independent demand
  and no clear superiority over a simpler unique-build-ID HTTP check.
- **Not a product-wide NO-GO:** the public open-source technical preview
  can remain available while actual usage evidence is collected.

Owner approval for **publishing a Marketplace listing** is distinct from
approval to study its feasibility. This document records readiness only.
