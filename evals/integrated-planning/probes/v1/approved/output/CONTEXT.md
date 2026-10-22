# Context

The accepted local Python contract is `DESIGN.md`. `tasks.py` contains independent task-list and CSV-text functions. Task rows and their order are preserved; neither API mutates inputs. CSV uses Python standard-library `csv.DictWriter`. The user explicitly authorized both implementations and local verification. Production, storage changes, external actions, and PR creation are outside scope.
