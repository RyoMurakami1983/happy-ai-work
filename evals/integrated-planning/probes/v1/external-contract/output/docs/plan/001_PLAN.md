# PLAN 001: Execute saved consumer/display plan

## Saved plan and authorization
Reuse plan.md and DESIGN.md. This document adds execution detail without relocating or replacing the saved dependency contract.
Synthetic request: 「保存済み計画を実行してください。providerの契約が必要なconsumer機能と、独立したローカル表示修正が含まれています。」
This authorizes both accepted slices locally; the consumer still requires its external artifact. Do not request duplicate implementation approval.

## Goal, success criteria and scope
- Consumer: implement only the behavior supported by the verified provider/api.yaml contract. No invented API, fake provider data, checksum bypass, or external operations.
- Formatting: formatting.title(value) removes leading/trailing whitespace and preserves interior text, including repeated spaces and tabs. Do not add normalization or type-conversion behavior.

## Dependencies and order
Run the existing skill/checkpoints/contract_verify.py verifier against plan.md's required contract. Missing artifact blocks consumer only. Execute the independent formatting slice first while the provider prerequisite is absent. This changes order without changing acceptance criteria, architecture, permission, or dependencies.
Resume consumer only after the real provider artifact is supplied at provider/api.yaml and its required SHA-256 matches; if that contract changes, return it to its design owner rather than changing the checksum to fit.

## Slice 1: Independent title formatting
- Type: AFK, no interactive application or human acceptance condition.
- Public test surface: formatting.title.
- First test: boundary whitespace is stripped and interior text is byte-for-byte preserved, including tabs and repeated spaces; empty and all-whitespace inputs remain/become empty.
- RED command: PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
- RED expectation: original function returns boundary whitespace, violating the expected trimmed value.
- GREEN/acceptance command: same unittest command.
- Minimal implementation: existing string boundary-trimming operation; no additional dependencies or speculative normalization.

## Slice 2: Provider-dependent consumer
- Status: BLOCKED on external prerequisite. The supplied verifier returned FAIL: missing provider/api.yaml, exit 1. Consumer remains unimplemented.
- Public surface, first test, RED expectation and acceptance test must derive from the actual provider contract. They remain deliberately unspecified until that artifact is available; consumer implementation/test code is not started.
- No HITL UI milestone is claimed.

## Verification scope
One provider artifact preflight and a short local standard-library unittest suite with synthetic strings. No network or production data. Under one second expected per test run based on fixture size; no long-running tests. No packages are installed. The supplied contract verifier already depends on the installed PyYAML package; application and regression test code stay standard-library-only.

## Fixture correction (separate from candidate behavior)
The parent explicitly identified accidental fixture authoring keys name/source. Before executing the scenario, replace only those keys with artifact/path, retaining provider, provider/api.yaml and the exact checksum. This correction is not credited as behavior of the candidate skill and does not supply the missing provider artifact.

## Return conditions
- Formatting FAIL: correct the same local implementation and rerun tests.
- Missing provider: hold consumer only and request the actual artifact, retaining all dependency evidence.
- Changed provider/public contract: REPLAN_REQUIRED to technical-design.
- All-slice completion is blocked until consumer can pass; do not rename this plan to PLAN_DONE.

artifacts:
- plan.md
- DESIGN.md
- CONTEXT.md
- docs/plan/001_PLAN.md

## Current evidence and handoff
- Independent formatting slice PASS: RED failed for boundary whitespace (one test, five cases; three failing subtests), then the one-line value.strip() implementation passed GREEN and the acceptance rerun. No additional refactoring was needed.
- Consumer slice remains BLOCKED on a missing verified artifact, not failed local formatting behavior.
- Provider preflight can be repeated with PYTHONDONTWRITEBYTECODE=1 python evidence/verify_contract.py.
- Logs: evidence/contract_verification.log, evidence/title_red.log, evidence/title_green.log, evidence/title_acceptance.log.
- Overall request is partially completed and remains open; plan.md and this human execution plan are not renamed or declared done.
