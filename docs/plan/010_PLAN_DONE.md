# PLAN 010 DONE：判断と次の一歩が伝わるレビュー

2026-09-27 / Issue #35

## ゴール・成功条件

レビューを読んだ利用者が、問題・推奨と理由・必要な判断・次の一歩を理解できるようにする。3Sは推奨理由を支える観点であり、項目数や短さを成功にしない。

根拠は [PRD](../prd/010_PRD.md)、[ドメインモデル](../domain/010_DOMAIN_MODEL.md)、[技術設計](../design/010_TECHNICAL_DESIGN.md)。名称・既存判定・独立性・受容根拠・実装許可の境界を維持する。改名、UI設計への拡張、他スキルの全面改修、インストール済みcacheの直接編集は対象外。

## 許可とHITLの扱い

2026-09-26の「まだ反映しないで計画書作成してから」に従って実装を停止し、計画を作成した。その後2026-09-27に「スキル変更後に閉じた空間でレビュー検証し、その後に問題なければ、プルリクしてマージまで進めて」と明示依頼を得た。

最新指示に従い、隔離した独立評価と品質検証をPR・マージの条件とする。AC-08の実利用理解はマージ後の観察として残し、自動採点で達成済みとしない。文書の回答例が以前より回答しやすいという利用者feedbackと、実際の変更後skillの効果は区別する。

## Sliceと検証

| Slice | Type・依存 | Done・first observation | RED / GREEN / Acceptance |
| --- | --- | --- | --- |
| 1：問題から判断・行動まで伝える | AFK、設計確認と基準固定に依存 | AC-01〜05、07。判断が必要な業務未合意と、不要な合意済み欠陥の対を最初に観測 | 現行版と改善版を同じpromptで独立生成し、固定rubricでblind採点。本文・referenceを一緒に改善する。現行版の失敗は捏造しない |
| 2：変更容易性と3Sで推奨を支える | AFK、Slice 1に依存 | AC-06。指定なし・指定あり・規模未提示の小変更を確認 | 同じ最終版で関連caseとSlice 1の回帰を評価し、focused check後にrepo品質入口を実行 |
| 検証基盤の補完 | AFK、独立設計確認で追加 | 旧recordを改変せず当時の実体を照合できる | `test_eval_history.py` で修正前5失敗を観測し、snapshot対応とappend-only実装後の成功を確認。現行版の古いhash拒否を維持 |

行動評価はCLIではなく独立生成担当と採点担当への隔離した依頼で実施する。条件ごとに新しいcontextを用意し、生成担当には本文・reference・promptだけ、採点担当には固定rubricと匿名回答だけを渡す。5件は同一条件のcontext内で共有するため、その限界を記録する。対象版はhashで固定。実装者は単一writer。

基準は [cases v2](../../evals/technical-design-review/cases.v2.json)、[TARGET v2](../../evals/technical-design-review/TARGET.v2.json)。Critical全件、禁止行為0、重大誤振分け0、通常12/15以上かつ主要3ケースで各2項目以上を実行前に固定。比較条件は [旧版snapshot](../../evals/technical-design-review/snapshots/v1/SKILL.md) と [候補hash](../../evals/technical-design-review/CANDIDATE.v2.json)。模範回答・他条件・採点基準を生成担当へ渡さない。

## コマンド

repo rootで実行する。公式quick_validateは実行環境のskill-creator同梱scriptを使う。

```powershell
uv run --no-project --python 3.14 --with PyYAML==6.0.3 python -m unittest discover -s tests -p test_eval_history.py -v
uv run --no-project --python 3.14 --with PyYAML==6.0.3 python scripts/validate_evals.py
git diff --check
uv run --script scripts/validate_quality.py
```

## 戻り条件

説明不足・不要な質問・判定との矛盾は該当sliceへ戻す。基準は結果を見て緩めず、再実行は新recordへ残す。構造変更が必要なら設計へ戻す。旧recordの照合障害は独立確認を受け、[ADR 0006](../adr/0006-evaluation-history-snapshots.md)に補足設計を残した。

## 進捗・証拠

- [x] 要求・モデル・設計・実装許可の確認
- [x] 独立設計確認と評価条件の事前固定
- [x] スキル本文とreferenceの変更
- [x] 履歴照合のRED／GREEN確認
- [x] 隔離したblind比較評価
- [x] 独立差分レビューと指摘修正・repo品質検証

ローカル実装は完了。PR・CI・マージは本計画の後続操作として、2026-09-27の利用者許可に従って進める。

固定した新基準で旧版はCritical13/13・通常11/15、新版はCritical13/13・通常15/15。両版とも禁止行為・重大誤振分け0。詳細な条件と限界は [評価record](../../evals/records/technical-design-review-explanations-002.json) に記録した。新しい説明基準による比較であり、旧版の過去評価は改変していない。

公式quick_validate成功。全品質入口はrepo/eval validator、80 unit tests、Ruff、ty、diff checkを通過。独立レビューのP2（部分的な履歴対応表を後から拡張できない）に対して、参照する変更可能な指示も初回snapshotへ含めた。修正後のfocused 7 testsとrepo validatorも成功。

実利用の理解確認（AC-08）は未実施。公開caseの検証を未見hold-outや統計的優位と呼ばない。raw回答と詳細採点はsession領域のみ、公開するのは固定case・対象hash・sanitize済みrecord。

## 成果物

```yaml
artifacts:
  - CONTEXT.md
  - docs/prd/010_PRD.md
  - docs/domain/010_DOMAIN_MODEL.md
  - docs/design/010_TECHNICAL_DESIGN.md
  - docs/plan/010_PLAN_DONE.md
  - docs/adr/0006-evaluation-history-snapshots.md
```
