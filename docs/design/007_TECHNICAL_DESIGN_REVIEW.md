# Technical Design Review skill

作成日: 2026-09-22

## 目的と根拠

利用者の「設計レビュースキル整理」の参照会話と新設・スキル検証の依頼に基づき、実装前の設計案を独立検証する。参照会話、添付の「目的駆動設計とAIコードレビュー_蒸留資料_v1.0.md」、既存technical-designのreview-ready contractを確認した。添付資料の本文は配布物へ複製しない。

Constitution 1.0.0の正確さ、評価整合性、人間の所有権、最小差分を具体化する通常改善。原則の優先順位や既存評価基準の意味は変更しない。

## 採用した責務

- `technical-design-review` は目的・要件からモデル・契約・技術構造・検証までの対応を検証し、根拠付き指摘、判定、戻り先を所有する。
- `technical-design` は設計作成とreview readiness、`deep-review` は実装差分の検査を所有する。新スキルはどちらも置き換えない。
- 要件や根拠の不足をレビューで補完せず、論点に応じてinterview-with-docs、to-prd、domain-modeling、technical-designへ返す。参照会話の周辺skill全面改修は今回の範囲に含めない。
- 通常の自動選択を維持する。詳細観点はskill内referenceに置き、upstreamのdocsや他pluginへのファイルリンクを実行時の依存にしない。
- [ADR 0004](../adr/0004-preview-plugin-distribution.md)に従いhappy-previewへ配置する。正式配布の候補はhappy-coding。模擬依頼の成功を実利用済みと扱わない。

## 受入条件と配置

| ID | 観測できる条件 | 配置理由 |
| --- | --- | --- |
| DR-01 | 実装前レビューと設計作成・差分レビューの担当を区別する | descriptionとcodingの入口で誤った工程へ渡さない |
| DR-02 | 合意済み目的・要件・ACから構造・検証への対応と契約の破綻を確認する | SKILL.mdとreferenceで具体的なレビューを可能にする |
| DR-03 | 各指摘に出典、影響する条件、発生条件、弊害、最小修正、戻り先を残す | 原則名や好みだけの不合格を防ぐ |
| DR-04 | 不足を発明せずBLOCKED、設計上の破綻はREVISE、重大問題のない範囲だけPASS系とする | SKILL.mdで誤った実装移行を防ぐ |
| DR-05 | 条件付きPASSは軽微な条件と権限ある所有者の受容根拠を追える | 未受容riskを承認済みにしない |
| DR-06 | 対象版と独立性を記録し、旧PASSを変更後へ無条件に流用しない | 判定の有効範囲と再確認範囲を示す |
| DR-07 | 小変更や単純CRUDへモデル文書・分割・重い書式を強制しない | 費用と目的に比例したレビューにする |
| DR-08 | レビューのみでは設計・コードを修正しない | レビュアーと設計者の責務を保つ |

## 検証と試用

公開の架空caseで、具体的な設計欠陥、小変更、根拠不足、条件付きPASS、近接する別依頼を検証する。caseと基準は実行前に固定し、独立generatorには期待回答・rubricを渡さず、独立graderが生成結果を採点する。raw回答は一時領域に置き、公開記録はsanitizeした集計だけとする。

公開case・対象hash・結果はevals/technical-design-reviewとevals/recordsに保存する。これは試用前のboundedな振る舞い確認であり、自動選択率、未見hold-out、既存手法より優れることの検証ではない。

実利用では、異なる設計案件で指摘の妥当性、必要な差し戻し、過剰な分割要求、条件付き判定の受容記録、修正後の再確認を観察する。複数の実作業の記録と残る制約を基に所有者が正式採用を判断する。

2026-09-22の独立forward testでは、5件の必須条件20/20、通常条件6/6を満たし、確認範囲で禁止行為・重大な誤適用は0だった。同時引受の保証欠落をREVISE、未合意の保持・閲覧条件をBLOCKED、局所変更をPASS、受容済みの軽微な条件をPASS_WITH_CONDITIONSに分けた。設計作成・実装差分・モデル・UI・業務理解への振り分けも確認した。自動発見精度と実利用は未検証。

公式quick_validateとrepo品質入口（62 tests、repo validator、Ruff、ty、diff check）が成功した。対象版と独立性、ケース別集計、限界は[評価記録](../../evals/records/technical-design-review-preview-001.json)、事前固定した条件は[TARGET](../../evals/technical-design-review/TARGET.v1.json)、再利用する依頼と基準は[cases](../../evals/technical-design-review/cases.v1.json)を参照する。
