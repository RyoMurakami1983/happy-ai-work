---
name: coding
description: 要求整理から設計、計画、実装、検証、レビューまでを、必要な工程だけ選んで進める明示呼び出し専用の開発オーケストレーター。$coding と指定して、一連の開発作業を完了まで進めたいときに使う。
---

# Coding

開発依頼を分類し、必要なskillだけを順に使って、検証済みの成果まで閉じる。
固定パイプラインではなく、既に揃っている成果物と変更リスクから工程を省略する。

## 最初に固定するもの

- 依頼種別: feature / change / bug / CI failure / review
- ゴールと外部から観測できる成功条件
- 対象と対象外
- 利用できる仕様、issue、design、plan、再現手順
- 変更・外部操作についてユーザーから与えられた権限

各工程で次の短いledgerを更新する。

```text
current stage:
inputs / artifacts:
exit condition:
evidence:
next stage:
skipped stages and reasons:
return path:
```

## ルーティング

どの依頼種別でも、対象repoの構造、規約、検証commandが未知なら、分岐前に `repo-onboarding` で事実を集める。既に十分なrepo contextがある場合は省略する。

### Feature / Change

1. 実装を左右する未知があれば `interview-with-docs` を使う。
2. 利用者、目的、scope、acceptance criteriaを合意・保存する必要があれば `to-prd` を使う。小さなrepo内変更で契約が明確なら省略する。
3. 用語、境界、不変条件の曖昧さが設計を左右する場合だけ `domain-modeling` を使う。
4. module責務、interface、data flow、security boundary、技術選定の判断が必要なら `technical-design` を使う。既存構造内の局所変更なら省略する。
5. 複数の依存slice、HITL/AFK分離、実行順の合意が必要なら `implementation-plan` を使う。単一sliceなら省略する。
6. `implement` で実装し、内蔵eval gateを各sliceで通す。

### Bug

`debug-and-fix` へ渡す。原因が要求の曖昧さなら `interview-with-docs`、構造上の問題なら `technical-design` へ戻り、修正可能な契約になったら `debug-and-fix` または `implement` を再開する。

### CI failure

GitHub Actionsの失敗なら `ci-debug` を優先する。CI外でも同じ失敗が再現し、製品コードの根本原因を追う必要があれば `debug-and-fix` へ渡す。

### Review

差分全体の独立レビューは `deep-review` へ渡す。指摘修正まで依頼されている場合だけ、指摘確定後に `implement` または `debug-and-fix` を使う。

いずれの経路でも変更を作った場合、PR前、高risk、またはユーザーが独立レビューを求めたときは `deep-review` を使う。

## 遷移ルール

- `PASS`: 次のsliceまたは次工程へ進む。
- `FAIL`: 契約を変えず、同じ実装・修正工程へ戻る。
- `REPLAN_REQUIRED`: `technical-design`または`implementation-plan`へ戻る。
- 要求が未確定: 探索が必要なら `interview-with-docs`、PRDのscopeやacceptance criteriaが誤っていたなら `to-prd` へ戻る。
- blocker、権限が必要な操作、HITL判断がなければ、工程名を報告するためだけに停止しない。

## 完了条件

- 成功条件を満たす観測可能なevidenceがある。
- 実行した主要commandと結果を記録した。
- 変更範囲、残存risk、明示した対象外が説明できる。
- 保存したartifactがある場合はpathが存在する。
- PR作成や外部公開など、依頼されていない外部操作を勝手に追加していない。

## 注意点

- 子skillの手順をここで再実装しない。対象skillを選んだら、その`SKILL.md`を読み、責務を委譲する。
- PRD、technical design、implementation planを常に全部作らない。
- 工程を省略した場合は、ledgerに理由を1行で残す。
- `coding`は明示呼び出し専用であり、通常のcoding依頼へ暗黙発火させない。
