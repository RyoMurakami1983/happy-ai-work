# Constitution drift enforcement review 003

Started: 2026-08-22T15:38:38.3025371Z
Completed no later than: 2026-08-22T15:44:06.4409359Z
Target: `evals/constitution/003_REVIEW_TARGET.json`
Evaluator: independent subagent `/root/post_fix_review`
Verdict: **FAIL**

既知のshallow checkout、profile追加drift source、`uv.lock`は解消した。新規P1として、content hashだけで照合済みcommitを特定すると、変更後に同じcontentへrevertしてから再変更した履歴でdrift開始をresetできると判明した。修正要件は、照合済みConstitution commit SHAをsync recordへ保存し、そのcommit以後の最古変更を使うこと。基準は変更せず、004で別recordとして再評価する。

## Raw finding

> P1 — 同一content hashへのrevertでConstitution drift clockをresetできる。履歴D（再変更1日前）、C（recorded内容へrevert 2日前）、B（最初の未解消変更11日前）、A（実際のreconciled commit）では、CとAのcontent hashが同じためCをbaselineと誤認し、Dの時刻を返す。content hashだけでなくreconciled commit SHAを同期recordへ保存する必要がある。
