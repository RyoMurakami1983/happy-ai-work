# PR #54 整理状況 — 2026-10-22

## 今回の判断

Issue #60の後続として、再利用できる比較準備・JSON表示基盤を残す。
旧案は10月3日のbaseline `ab32391c9612ad7983a4805040a6331ad5f576db` を対象としており、
#58の計画統合、#61の契約/checksum修正、#62の報告・検証通知修正を含まない。
旧lean候補と最新mainをそのまま比較すると、短文化以外の差が混ざる。
そのため旧案のbyteを変更せず、現行baselineを別versionへ固定し、新candidateは未作成として分離する。
現在の候補を採用済みと扱ったり、意味を保持できたと未検証で主張したりしない。

## 完了する範囲

- main `1854315e78454f1f3b98ad9f9ea9ce2217cbf013` をPR branchへ統合。配布pluginへの追加変更はしない。
- `snapshots/current-v2/` に同revisionのimplement全25 filesと必要なPRD/設計HTML参照依存と準備manifestを固定。
- 旧baseline/candidate・provenance・case・task・fixture・manifestのbyteを保持し、hash inventoryをappend-only領域へ追加。
- 準備scriptの既定をcurrent-v2 baselineへ変更。旧案は`--suite legacy-v1`でのみ選択。
  current-v2 candidateは未準備として出力前に拒否。新旧suite識別と未実行状態をSOURCEに残す。
- 12 public合成caseとJSONダッシュボードを再利用。新framework、model runner、配布versionは追加しない。
- 元の準備security testsをlegacy-v1へ明示的に適用し、現行入力の分離・履歴保持の回帰testsを追加。

## 検証

新規回帰testで、変更前に現行baseline不在・旧candidateの暗黙出力・suite識別欠落を再現した。
変更後のfocused検証では12 caseのcurrent baselineと旧2条件、未準備candidate拒否、hash/inventory保持を確認する。
全件品質入口・独立review・exact head CIの結果は、この記録の末尾とPR本文へ実測後に記載する。
これらはpackagingと合成testでありmodel behaviorの採点ではない。

## 残件と、次に必要な判断

1. 新candidateで検証する仮説・変更範囲を決め、現行baselineと同じ意味・安全境界を維持した案を別versionにする。
   旧caseだけで計画統合や#61/#62を網羅したとせず、必要なcaseを新versionで固定する。
2. 正式model/snapshot、effort、実行環境、規模、token/time/cost予算を確定する。旧72 runs案は承認済み予算ではない。
3. 尺度とanchorを事前登録し、独立grader、秘密採点資産への実read拒否、context/tool/logの隔離を確認する。
4. ダッシュボードの実ブラウザ描画・CSP/networkを検証する。既存DOM/JS合成試験で代用済みとしない。
5. 以上を満たして初めて別途許可された比較を実施する。現時点で性能改善・採用・実利用効果は未確認。

`012_*REVIEW.md`と`012_IMPLEMENTATION_VERIFICATION.md`の10月3日の報告は当時の入力・時点についての履歴。
そこにある公開前/CI未実行の記述を現在の状態と混同しない。旧レビューを現行candidateの保証として流用しない。
PRはDraftのまま。merge/close、Issue #60の完了、配布、課金/model評価の実行は今回の範囲外。

## 実測した整理結果

- Python 3.14.8のcanonical quality入口をoffline/cacheのみで実行: 全210 tests、repo/eval validator、Ruff 0.16.3、ty 0.0.74、diff check PASS（unit tests約22秒）。
- focused 16 tests PASS。元の7準備testsを維持し、9回帰testsを追加。
- 初回aggregateでは209 tests/lint/typeは成功したが、現行WORK_ARTIFACTSのPRD/設計HTML参照2箇所がsnapshot外だったためrepo validatorが失敗。
  同じmainの参照依存20 filesを追加し、installed bundleの相対link確認を追加後、全件を再実行して成功した。validatorや既存testは緩和していない。
- 独立read-only review: blocking findingなし。旧58 filesを元PR headと、現行45 files（implement 25 + HTML依存20）をmainとbyte照合。
  installed plan/PRD/designの3生成器の同梱例に対する `--check` もPASS。新しいskill entrypointはimplementのみ。
- 旧ダッシュボード/JSON契約/renderer/10月3日のreview記録は保持。配布pluginとmarketplaceは上記mainと同一。
- exact remote head・両OS CI・remote Constitution確認は公開後のPR本文を参照。モデル評価、実ブラウザ、導入先への配布は未実施。
