# Context

This local Python fixture exposes task-list functions in `tasks.py`. The accepted contract is `DESIGN.md`. A task is an input mapping; filtering preserves original rows and their order. CSV is returned as text, with `id,status,title` columns using Python's standard-library CSV writer. Storage, GUI, production operations, and PR creation are outside scope.

Current request is planning only. Approval of the design does not authorize implementation. No code or test execution is part of this request.
