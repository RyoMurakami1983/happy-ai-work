---
name: implementation-plan
description: 合意済みの要求とtechnical designを、依存順、vertical slices、HITL/AFK、first test、検証command、戻り条件を持つ実装計画へ変える。新しいarchitectureを決めず、安全な実装順序を作りたいときに使う。
---

# Implementation Plan

合意済みの要求と構造判断から、`implement`が迷わず実行できる順序とslice contractを作る。
このskillは実行順を所有し、新しいarchitecture判断は行わない。

## 入力ゲート

次を確認する。

- ゴール、成功条件、対象外
- acceptance criteriaまたはbehavior list
- 既存repoのbuild / test / launch command
- 構造判断が必要な変更では、`technical-design`のhandoffまたは同等の決定
- 保存済みartifactのpath

要求が不足していれば `interview-with-docs` または `to-prd`、構造判断が不足していれば `technical-design` へ戻す。単一の明確なsliceなら、重いplanを作らず短いimplementation handoffだけでよい。

## ワークフロー

### 1. Behaviorと依存を整理する

- acceptance criteriaを外部から観測可能なbehaviorへ対応付ける。
- schema、contract、migration、consumer / provider等の実依存だけを列挙する。
- 依存しない作業と、順序を守る必要がある作業を分ける。

### 2. Vertical sliceへ分ける

1 sliceは1つのユーザー行動またはacceptance conditionを主語にする。最初のsliceは必要な層を薄く縦断するtracer bulletを優先する。

各sliceに含めるもの:

- done条件と対象外
- HITL / AFK
- 使用するpublic interface / test surface
- first testまたはdocs/config変更のverification
- RED command
- REDの期待失敗理由
- GREEN command
- acceptance command
- 前提と依存slice

DBだけ、UIだけ、testだけを先に広げるhorizontal sliceは避ける。

### 3. 実行順と戻り条件を決める

- 価値を早く観測でき、riskを早く潰せる順にする。
- 未確定のsliceを並列化しない。
- `FAIL`は同じsliceの実装修正へ戻す。
- `REPLAN_REQUIRED`はこのplan、または構造問題なら `technical-design` へ戻す。
- 要求の問題なら `interview-with-docs` または `to-prd` へ戻す。

### 4. Handoffを作る

```markdown
## Implementation Handoff

### Goal / Success Criteria / Out of Scope
### Design Artifacts
### Behavior List
### Dependencies
### Vertical Slices

| Slice | HITL/AFK | Depends on | Done | Test Surface | First Test | RED Command | RED Expectation | GREEN Command | Acceptance Command | Slice Out of Scope |
|---|---|---|---|---|---|---|---|---|---|---|

### Artifacts

artifacts:
  - docs/plan/NNN_PLAN.md

### Risks / Unknowns
### Return Conditions
```

上はplanだけを保存した例である。保存済みPRD / design等が実在する場合だけ、そのpathも追加する。

保存済み成果物がある場合は既知のpathをすべて列挙する。どの成果物も保存しない場合だけ `artifacts: conversation-only` とする。

進捗をrepoで追う価値がある場合、またはユーザーが保存を求めた場合は[NNN_PLAN_TEMPLATE.md](assets/NNN_PLAN_TEMPLATE.md)を使い、`docs/plan/NNN_PLAN.md`へ保存する。成果物の番号とpathは[WORK_ARTIFACTS.md](references/WORK_ARTIFACTS.md)に従う。

## 注意点

- 設計案を作り直さない。構造判断が必要なら `technical-design` へ戻す。
- 実装を始めない。
- planを詳細な作業日記にしない。
- PR、review、furikaeriを実装sliceへ混ぜない。

## 関連リソース

- [WORK_ARTIFACTS.md](references/WORK_ARTIFACTS.md) — artifactのpath、番号、handoff規約
- [NNN_PLAN_TEMPLATE.md](assets/NNN_PLAN_TEMPLATE.md) — 保存するplanのテンプレート
