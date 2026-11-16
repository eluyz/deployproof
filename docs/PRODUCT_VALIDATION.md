# DeployProof positioning: what its identity check adds

Status: **evidence review (2026-11-16)**. DeployProof v0.1.0 is a public
technical preview. This page is **not** a claim of market demand,
independent adoption, asset integrity or a feature comparison certified by
other maintainers.

## Decision question

Is there enough value in requiring a structured four-field build identity
manifest to justify more setup than an ordinary successful Pages deployment
or a generic HTTP expected-content check?

### What each option actually checks

| Case | GitHub Pages `actions/deploy-pages` | `KaliCZ/verify-deployment` | `eluyz/deployproof` |
| --- | --- | --- | --- |
| Deployment API/job reports success | Yes; deploys an uploaded Pages artifact and exposes `page_url` | Not a deployment action | Not a deployment action |
| Public URL returns a healthy response | Not an explicit documented post-deploy HTTP content check | Yes; URL polling and optional expected string | Yes; public JSON manifest fetch and four expected fields |
| Stale different SHA, when marker exists | Does not directly compare response identity | Detectable if checking expected SHA | Detectable from trusted expected SHA |
| Same SHA but different run attempt/build | Not directly checked on live URL | **SHA-only** expected text misses it; **unique build ID** text can detect it | Detectable when trusted expected `run_attempt` / `build_id` differ from public manifest |
| Published marker current, JS/CSS/data stale | Not an asset freshness check | May pass if health URL contains expected text | **May return `IDENTITY_PASS`** despite stale assets |
| Parsed identity-field semantics | No public-JSON matching feature documented | Checks whether arbitrary response text contains the expected string | Strict JSON parse, four exact string fields, bounded size, duplicate key rejection, error categories |
| Setup when site has no version marker | No extra marker, beyond normal Pages workflow | Needs an endpoint/content marker for SHA/build-specific freshness | Build must write `deployproof.json` before artifact upload and forward four trusted job outputs |

**Important competitor nuance:** A unique build ID can be checked with the
generic Action's `expected-content` string. Therefore detecting same-SHA
reruns is **not an exclusive DeployProof capability**. Structured field
comparison and specific failure categories are differences, but their
value to external users has **not** been validated.

## Controlled comparison (not third-party field evidence)

The synthetic example models one source revision used in *two build attempts*:

| Field | Published attempt 1 (stale) | Trusted expected attempt 2 |
| --- | --- | --- |
| `git_sha` | `aaaaaaaa…` (same SHA) | `aaaaaaaa…` (same SHA) |
| `workflow_run_id` | `53001` | `53001` |
| `run_attempt` | `1` | `2` |
| `build_id` | `53001-1-${SHA}` | `53001-2-${SHA}` |

If the published manifest is still from attempt 1:

1. A **SHA-only substring** check could pass because the source SHA is unchanged.
2. A **unique build-ID substring** check can fail, too, if the content
   includes the old ID rather than the new one. This is a viable simpler
   alternative using the competing Action.
3. DeployProof returns `VERSION_MISMATCH` and identifies changed fields
   (`run_attempt`, `build_id`) **when** the expected identity comes from
   the build job outputs, *not* from the published manifest.
4. If the manifest was updated but JS/CSS was not, DeployProof can still
   return `IDENTITY_PASS`. It is not an end-to-end asset integrity proof.

The repository's local HTTP tests implement this scenario, including a
contrived case where the expected build-ID text appears in an unrelated
JSON field. That illustrates an exact-field vs substring distinction but
**does not prove this is common in real Pages deployments**. Tests do not
run the competitor's actual GitHub Action.

## Integration cost and trust boundary

- Native deploy: no additional manifest or verification job.
- Generic string check: one health URL, optional expected string; a site
  still needs to expose the desired marker to test a specific build.
- DeployProof: generate four public identity strings as JSON **before**
  uploading the artifact, export those values as build job outputs,
  add a separate verification step and supply the Pages site URL.
- Reading expected identity from the published manifest is circular and
  **not valid production provenance verification**.
- GitHub Pages itself must deploy and serve the artifact; no verification
  Action can clear a stuck platform deployment or fix a browser cache.

See the [Getting Started guide](GETTING_STARTED.md) and the full
[Pages example](../examples/pages-deploy-and-verify.yml). Public manifests
expose SHA/run metadata; they must never contain secrets.

## Conclusion and next experiment

**Decision:** Maintain as a narrow, tested open-source technical preview.
**NO-GO** for adding new features, claiming differentiated demand, or
publishing a new release solely to counter low feedback. **Not** a NO-GO
for keeping the existing GitHub repository available.

Evidence still needed to prioritize expansion:

1. A real independent Pages maintainer reports a concrete case where
   the structured error categories solve debugging better than an
   ordinary expected-content probe.
2. Installation friction is observed from an actual consumer's real
   build/deploy workflow, not just our owner-controlled synthetic smoke.
3. Any Marketplace listing requires distinct owner approval of the
   developer agreement and a separate verified submission. It is a
   potential discovery channel, **not evidence of adoption**.

If the easier unique build-ID substring check proves equally useful,
**prefer a simpler solution** instead of manufacturing a new feature
advantage. Stars, clones, thread views and silence without confirmed
exposure are not verified usage.

## Public source evidence

- [GitHub `actions/deploy-pages` README](https://github.com/actions/deploy-pages):
  artifact deployment and `page_url` output; no documented post-deploy
  identity comparison.
- [Verify Deployment Marketplace page](https://github.com/marketplace/actions/verify-deployment)
  and [source `action.yml`](https://github.com/KaliCZ/verify-deployment/blob/main/action.yml):
  `curl -sf` and literal `grep -qF` against optional `expected-content`.
- [DeployProof checker](../scripts/verify.py) and
  [local HTTP regression tests](../tests/test_verify.py): actual
  four-field matching and negative/positive scenarios.
- [GitHub Pages custom-workflow docs](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages):
  build/upload/deploy flow, and required permissions.
