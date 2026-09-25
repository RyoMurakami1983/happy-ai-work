# PLAN 008: 相談から成果物変更へ移る判断

## GOAL / Success Criteria

Issue [#33](https://github.com/RyoMurakami1983/happy-ai-work/issues/33) の共通着手判断を配布テンプレートへ反映する。相談中の誤着手を抑え、明確な変更依頼の進行を妨げない文面とし、home・repo・skillの責務を維持する。

## Out of Scope

- 全変更への計画・再承認の義務化。
- Issue #17のfinalization gateの再実装。
- 承認前の個人ホームへの適用。

## Progress

- [x] Issueと現行指示・テスト・文書規約の確認
- [x] PRDと設計の保存
- [x] Slice 1: 共通方針の着手判断を配布テンプレートへ融合
- [x] Slice 2: 相談・賛意・変更依頼の両方向を確認（公開caseと隔離した更新後の試行）
- [x] 個人ホームへの適用判断と、適用する場合の差分確認
- [x] Completion handoff

## Design Artifacts / Fixed Decisions

- [PRD 008](../prd/008_PRD.md)
- [Technical Design 008](../design/008_TECHNICAL_DESIGN.md)
- 着手判断はhomeテンプレートの第一項目へ融合し、6項目を維持する。
- repo固有規則と実装skillの詳細手順を複製しない。
- 個人ホームへの適用は配布テンプレート編集と別の判断とする。

## Behavior List

- 改善案の提示と分析依頼では読取調査と回答を進め、依頼されていないファイル変更をしない。
- 案への賛意の後に比較が続く場合、賛意だけを変更依頼とみなさない。
- 明確な修正依頼では、対象範囲の変更と検証まで進める。
- 変更中に目的や対象を変える未決事項が出た場合は、その判断だけを切り出す。

## Vertical Slices

### Slice 1: 共通方針を更新する

- Type: AFK
- Depends on: なし
- Done: `home-bootstrap/assets/AGENTS.md` の第一項目に段階判断があり、既存方針と6項目を保持する。
- Test surface: 配布テンプレート、`home_bootstrap.py --dry-run`、既存home-bootstrap test。
- First test: 更新後の管理領域を一時ファイルへ反映し、管理外内容を保持する既存testを確認する。
- RED command: 該当なし。文言変更のため、新しい文字列一致testを作らない。
- RED expectation: 該当なし。
- GREEN command: `uv run --script scripts/validate_quality.py`
- Acceptance command: 上記のfocused checkと、テンプレートの差分review。
- Out of scope: 個人ホームへの適用、repo固有指示の複製。

### Slice 2: 着手判断の両方向を確認する

- Type: AFK（独立behavioral実行が可能な場合）。不可の場合は未検証範囲を記録する。
- Depends on: Slice 1
- Done: 相談中の誤着手と変更依頼への過剰停止を、同じ観測基準で確認し、実施できた範囲を報告する。
- Test surface: 複数ターンの相談、賛意後の比較、明確な修正依頼のscenario。
- First test: scenarioごとに期待行動・禁止行動・ファイル書き込みの観測方法を先に固定する。
- RED command: 該当なし。AIの意味的行動を文字列testへ置き換えない。
- RED expectation: 該当なし。
- GREEN command: 独立実行が可能な場合は同一scenarioで旧版と更新版を比較する。
- Acceptance command: 実行結果と残存riskの確認。
- Out of scope: 静的文言reviewをbehavioral評価の成功と呼ぶこと。

## Individual Home Application

実ホームはrepo外の別対象。利用者が適用を明示した場合、`home-bootstrap` のdry-runで対象と差分を示し、承認範囲に従ってbackup付きで適用・再読する。配布テンプレートの更新だけではこの段階を完了扱いにしない。

## Verification So Far

- `evals/consultation-start/cases.v1.json` に相談・賛意・明確な修正依頼の3ケースを固定した。公開caseであり、未見hold-outとは呼ばない。
- `uv run --script scripts/validate_quality.py` はrepo validator、65件のunit test、Ruff、ty、`git diff --check`を通過した。
- `home_bootstrap.py --dry-run` は個人ホームの第一項目だけの差分を示し、書き込まなかった。
- 利用者の明示承認後に`--apply`で個人ホームの管理領域を更新し、元ファイルのbackupを作った。適用後、配布テンプレートとの一致を確認した。
- 公式`skill-creator`の`quick_validate.py`は通過した。
- 更新後の共通方針を読ませた独立作業者2名で、隔離した小規模試行を実施した。相談から追加の比較依頼へ続く2ターンでは設定ファイルを変更せず、誤字修正の明確な依頼では対象の`bold`だけを「大字」から「太字」へ修正し、JSON読込と`line_break`の保持を確認した。親作業者が両方の実ファイルを再読して照合した。
- この試行は公開caseによる更新後の各1回であり、旧版との比較、未見hold-out、統計的な効果の主張はしない。

## Return Conditions

- FAIL: 文面が相談を一律停止させる、または明確な変更依頼を毎回確認させるなら第一項目へ戻す。
- REPLAN_REQUIRED: 目的・対象・規則の配置が変わるならPRD／設計へ戻す。

```yaml
artifacts:
  - docs/prd/008_PRD.md
  - docs/design/008_TECHNICAL_DESIGN.md
  - docs/plan/008_PLAN.md
  - evals/consultation-start/cases.v1.json
```
