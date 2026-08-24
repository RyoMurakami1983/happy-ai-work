# Instruction finalization baseline

## Frozen revision

`ed96ec7` (`Python品質検証をuvで再現可能にする (#18)`), captured before Issue #17 implementation.

The full public baseline instructions remain addressable at this Git revision. The exact relevant file hashes are:

```text
AGENTS.md c3b508a000baa3dd363247653a0edb54ab2efcef2238df567434ac2135d8d9f6
plugins/happy-coding/skills/technical-design/SKILL.md 6471647088e2471cd6dc9052e71deac25e831dc79438d5e7e5f541b1c2aedbc7
plugins/happy-coding/skills/implementation-plan/SKILL.md 1983252b055c0a0b878231918a85398f98244dbc89d3fc0dad482dca0c8a55f7
plugins/happy-coding/skills/implement/SKILL.md e3e0d9fb779f09a8d4d3496b4bdc8895bc6a816653ce227a1f7690e35db11938
plugins/happy-coding/skills/implement/references/eval-checklist.md 6525c9662b88dcd03357991cc4419efc2721927db113a9842be1a7e0028e90c7
plugins/happy-coding/skills/deep-review/SKILL.md 2a190dbc214daafbb3862ae57e6fa697c2b137f1a68cb8e5c0aab84b416faad0
plugins/happy-coding/skills/deep-review/references/preflight.md 131be6eb54b702d7eb83bf6b673b3f3e0465a338a562d10680d25788b739a5e6
```

## Behavior-affecting baseline contract

- `technical-design` records significant adopted options, rejected options, reasons, and risks, then hands off design artifacts, structure decisions, unknowns, and return paths. It has no explicit normative／history separation or promotion test.
- `implementation-plan` maps Acceptance Criteria to observable behavior and creates slices. It has no source trace from durable targets to accepted decisions.
- `implement` compresses discussion to a necessary contract, checks speculative code and unnecessary abstractions, and returns when the contract changes. It has no explicit semantic check for rejected-alternative residue or over-minimization.
- `deep-review` compares the diff, requirements, tests, and repo instructions. Its preflight checks source-of-truth consistency, distribution, and duplicate invariants, but not instruction finalization explicitly.
- root `AGENTS.md` has no repository-wide invariant separating adopted durable instructions from discussion history.

This snapshot is the instruction condition supplied to baseline generators together with the public case prompts. It intentionally contains no expected answers or rubric.
