# Constitution drift enforcement review 005

Started: 2026-08-22T15:53:09.3385376Z
Completed no later than: 2026-08-22T15:56:56.3241663Z
Target: `evals/constitution/005_REVIEW_TARGET.json`
Evaluator: independent subagent `/root/post_fix_review`
Verdict: **FAIL**

既知P1/P2はすべて解消し、targetの8 artifact hashも一致した。新規P2として、squash／rebase mergeではbranch上の`constitution_revision`がmain履歴から失われる運用境界が判明した。安全上はmode Bでfail-closedになるが通常運用不能となるため、今回と将来のanchor更新はmerge commit方式に限定する。基準は変えず006で別recordとして再評価する。

## Raw finding

> P2 — commit anchorはsquash/rebase mergeでmain履歴から失われる。今回のPRをmerge commit方式に限定するか、merge後main上のdurable commit SHAを別metadata commitで記録する必要がある。
