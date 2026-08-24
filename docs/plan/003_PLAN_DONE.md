# PLAN 003

## GOAL

Instruction finalizationを設計handoff、plan、actual diff、DeepReview、behavioral evalへ責務分離し、非採用案の混入と必要constraintの過剰削除を防ぐ。

## Success Criteria

- finalized contractの生成・消費・戻り条件が既存skill境界に追加される。
- 恒久成果物の意味的混入と必要constraint欠落を実装・reviewで確認できる。
- wrapperからrepo-localへ決定を変えるscenarioと、過剰最小化、should-not-triggerを同一基準でbaseline/current比較する。
- focused validatorとrepo品質gateが通る。

## Out of Scope

- 全skillやREADMEへの一律横展開。
- 議論履歴の削除。
- 意味的判定の文字列validator化。

## Progress

- [x] Bootstrap / 前提確認
- [x] Slice 1: finalization contractと工程別gate
- [x] Slice 2: behavioral evalとadoption record
- [x] Slice 3: independent DeepReviewと修正
- [x] Completion handoff

## Design Artifacts / Fixed Decisions

- 主ownerは`technical-design`のhandoff境界。
- `implementation-plan`、`implement`、`deep-review`は異なる証拠を検査するconsumer／backstop。
- decision historyはdesign／ADR、規範contractは採用sourceだけ。
- traceはslice／主要artifact単位とし、行単位にしない。
- simple one-sliceへ重いcontractを強制しない。

## Finalized Contract / Target Trace

規範sourceとstatusの正本は`docs/design/003_TECHNICAL_DESIGN.md`の`Implementation Handoff`とする。planは次の主要targetだけを実装sliceへ渡す。

| Durable target | Normative source |
| --- | --- |
| `AGENTS.md` | `POLICY-INSTRUCTION-PROMOTION`, `AC17-TRACEABILITY`, `AC17-DURABLE-PLACEMENT` |
| `CONTEXT.md` | `AC17-DECISION-SEPARATION`, `AC17-NORMATIVE-HANDOFF` |
| `technical-design/SKILL.md`と`references/finalization-contract.md` | `DEC-FINALIZATION-GATE-OWNERSHIP`, `AC17-DECISION-SEPARATION`, `AC17-NORMATIVE-HANDOFF`, `AC17-TRACEABILITY`, `AC17-HISTORY-BOUNDARY` |
| `implementation-plan/SKILL.md`とplan template | `AC17-NORMATIVE-HANDOFF`, `AC17-TRACEABILITY`, `AC17-LIGHTWEIGHT-NEAR-MISS` |
| `implement/SKILL.md`とeval checklist | `AC17-BIDIRECTIONAL-REVIEW`, `AC17-DURABLE-PLACEMENT`, `AC17-OVER-MINIMIZATION` |
| `deep-review/SKILL.md`とpreflight | `AC17-BIDIRECTIONAL-REVIEW`, `AC17-HISTORY-BOUNDARY`, `AC17-OVER-MINIMIZATION` |
| public case、pilot、append-only record | `AC17-WRAPPER-SCENARIO`, `AC17-OVER-MINIMIZATION`, `AC17-BASELINE-CURRENT`, `SAFETY-EVALUATION-INTEGRITY` |

Exclusionsは`ALT-EARLY-DISCARD: rejected`、`ALT-DEEP-REVIEW-ONLY: rejected`、`ALT-DUPLICATE-FULL-RULE: rejected`、`NG-STRING-TEST-ONLY: non-goal`。`rejected`と`non-goal`を別途採用されたnegative requirementなしに恒久禁止へ昇格させず、詳細はdesign／ADRだけに置いて実装sliceへ再展開しない。Unknownはない。

## Behavior List

- [x] 非採用wrapper固有のlocator、責務、test seamを規範成果物へ昇格しない。
- [x] 採用案にも必要な恒久安全constraintは保持する。
- [x] 根拠不明の恒久変更は前段へ戻す。
- [x] DeepReviewが混入と欠落を独立検出する。
- [x] 単純な局所変更では通常workflowを維持する。

## Vertical Slices

### Slice 1: finalization contractと工程別gate

- Type: AFK
- Depends on: なし
- Done: root instruction、technical-design、plan、implement、deep-reviewに重複しない責務が入り、referenceへ詳細が集約される
- Test surface: repo validator、skill quick validation、diff review
- First test: docs-only変更のためREDを装わず、現行skillにfinalized contractとsemantic review観点がないことをbaseline snapshotで固定
- RED command: `rg -n "finalized_contract|finalization gate" plugins/happy-coding/skills`
- RED expectation: 対象workflowにfinalization contractが存在しない
- GREEN command: `uv run --script scripts/validate_quality.py`
- Acceptance command: `uv run --script scripts/validate_quality.py`
- Out of scope: behavioral adoption判定

### Slice 2: behavioral evalとadoption record

- Type: AFK
- Depends on: Slice 1
- Done: public case、baseline snapshot、target manifest、sanitize済みappend-only recordがあり、currentのCritical全通過・禁止0・重大な誤起動0を独立評価で確認する
- Test surface: `scripts/validate_evals.py`と独立subagent実行
- First test: 実装前baselineを同じ3 scenarioで独立実行する
- RED command: static REDなし。baseline独立responseを改善前証拠とする
- RED expectation: finalized contractの分離またはshould-not-triggerの少なくとも一部が曖昧
- GREEN command: `uv run --script scripts/validate_quality.py`
- Acceptance command: current Critical全通過、禁止0、重大な誤起動0、baseline比重大回帰なし
- Out of scope: raw response／transcriptのrepo保存

### Slice 3: independent DeepReviewと修正

- Type: AFK
- Depends on: Slice 1, Slice 2
- Done: 実装者と別のreviewerがIssue #17、finalized contract、diff、検証結果だけで重大指摘なし、または指摘修正後に再確認する
- Test surface: git diff、focused/full quality evidence
- First test: reviewerが混入、過剰削除、配置drift、eval妥当性を確認する
- RED command: static REDなし。独立review findingsを証拠とする
- RED expectation: actionable findingがあればFAILとして修正へ戻る
- GREEN command: `uv run --script scripts/validate_quality.py`
- Acceptance command: independent reviewerがPASSまたは重大な指摘なし
- Out of scope: PR作成、commit、Issue close

## Order Rationale

- 評価caseとbaselineを実装前に固定し、その後に一つのinstruction変更テーマだけを比較する。
- actual diffと評価recordが揃ってから独立reviewする。

## Risks / Unknowns

- なし。ownerは多層防御方針を承認済み。

## Artifacts

```yaml
artifacts:
  - docs/design/003_TECHNICAL_DESIGN.md
  - docs/adr/0003-finalization-gate-ownership.md
  - docs/plan/003_PLAN_DONE.md
  - evals/pilot/006/TARGET.json
  - evals/records/instruction-finalization-adoption-004.json
```

## Completion Evidence

- Behavioral eval: Pilot 006の独立2反復が各`Critical 11/11`、`Normal 5/5`、禁止行為0、重大誤起動0。
- Deterministic gate: `uv run --script scripts/validate_quality.py`がvalidator、50 tests、Ruff、ty、`git diff --check`を含めPASS。
- Independent review: hash chainとTARGET内部衝突の指摘を修正し、独立再レビューPASS。
- Adoption: `instruction-finalization-adoption-004`をMode A / adoptedとしてsanitize保存。raw回答と詳細gradingはsession限定で削除。

## Return Conditions

- FAIL: 同じsliceでinstruction、eval case、record、evidenceを修正する。
- REPLAN_REQUIRED: finalized contractの所有者または配置境界が変わる場合はtechnical-designへ戻す。
