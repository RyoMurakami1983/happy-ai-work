# 公開評価資産

繰り返し使うcaseの設計、公開昇格、廃止、保存境界を扱う場合に読む。このreferenceは配布plugin内で自己完結し、利用先にupstream repoの`docs/`や`evals/`が存在することを前提にしない。upstream maintainerはrepo側の評価資産文書とvalidatorも併用するが、downstream利用者へそのpathを要求しない。

## Caseを固定する

- 公開caseは`upstream eval`または`共通安全eval`へ分類し、`private eval`と呼ばない。
- happy path、near-miss／should-not-trigger、failure／missing-contextを最低セットにする。
- scenario、Critical、通常要件、禁止事項、観測方法、criteria versionを実行前に固定する。
- public repoへ保存したcaseは`holdout: false`とし、未見hold-outとして再利用しない。

## Sealed候補を扱う

sealed prompt、期待回答、rubric、raw responseはsession限定または利用者管理の非公開領域に置く。実行後は、ownerがsanitize済みcaseをpublicへ昇格するか、非公開維持／破棄を決める。昇格した時点から既知caseである。

## 比較を記録する

conditionごとのgeneratorを分離し、他条件の出力、rubric、期待判定、condition labelを渡さない。blind graderにはlabel対応を伏せる。implementer、generator、grader、evaluatorの役割とagent IDをsanitize済みrecordへ残す。

raw runをrepoへ保存しない。公開recordは対象revision、Constitution／profile／criteria／schema version、condition hash、時刻、A／B／C、判定、case別集計と必要最小のresponse hashを持つ新fileにする。再評価で既存recordを編集しない。

## Deterministic policy

upstream repoでは専用validatorでschema、公開hold-out、禁止path／field、明白なsecret pattern、append-only違反を検査する。配布先に同じscriptを要求しない。意味的なrubric採点、sanitizeの完全性、AI behaviorは機械testの責務にしない。
