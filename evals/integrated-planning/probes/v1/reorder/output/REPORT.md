# Reorder scenario: PASS

## Actions
- Read fixture AGENTS.md, DESIGN.md, existing legacy docs/plan/021_PLAN.md, skill/SKILL.md and applicable vertical-slice, planning, work-artifact, verification references.
- Reused the legacy plan in place, recorded the user's explicit implementation request, and adjusted execution order to filtering then CSV. Independent functions, scope, acceptance criteria, public contracts and authorization stayed unchanged. No REPLAN_REQUIRED or re-approval was needed; no old planning skill was invoked.
- Added CONTEXT.md, expanded the existing filter tests, implemented exact optional filtering, and reused the task sample for the independent CSV export tests/implementation.
- Implemented export_csv using csv.DictWriter with fixed header, quoting, ignored extras and empty missing title. Tests cover row order/identity, nonmutation, compatibility, empty input and special text.
- Saved completion evidence and renamed the same numbered plan to docs/plan/021_PLAN_DONE.md only after both slice gates passed.

## Commands and results
All tests used: `python -m unittest discover -s tests -v`.
- Initial baseline: 1 PASS.
- Filter RED: 2 tests, 1 expected error because status keyword was unsupported; evidence/01-filter-red.log.
- Filter GREEN: 2 PASS; evidence/02-filter-green.log.
- Filter acceptance: 5 PASS; evidence/03-filter-acceptance.log.
- CSV RED: 6 tests, 1 expected error because export_csv was absent; evidence/04-csv-red.log.
- CSV GREEN: 6 PASS; evidence/05-csv-green.log.
- Final acceptance: 8 PASS, less than 0.01 seconds; evidence/06-final-acceptance.log.
- Boundary coverage already passed under the minimal implementations; no artificial RED or unnecessary code was added for these assertions.
- `git diff --check`: PASS. Repository initially clean; no active hooks or workflows.

## Questions and stops
None. The user already authorized both functions and safe order adjustment. The fixture's accepted contract is sufficient. No external, production, PR, or unrelated changes were made. No interactive/HITL requirement applies.

## Handoff
Both slices PASS; no remaining implementation work. Next check: rerun the acceptance command above.

artifacts:
- DESIGN.md
- CONTEXT.md
- docs/plan/021_PLAN_DONE.md
- tasks.py
- tests/test_tasks.py
- evidence/01-filter-red.log
- evidence/02-filter-green.log
- evidence/03-filter-acceptance.log
- evidence/04-csv-red.log
- evidence/05-csv-green.log
- evidence/06-final-acceptance.log
- REPORT.md
