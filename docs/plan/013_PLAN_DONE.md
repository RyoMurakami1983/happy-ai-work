# Plan 013: UI設計のメンタルモデルと参照導線 (#63)

## 契約・範囲

正本は [Issue #63](https://github.com/RyoMurakami1983/happy-ai-work/issues/63)（2026-10-25取得）。利用者からスキルの修正・検証と独立レビューを依頼済み。既存main `3d0fb7c9ac2ac3fa42893520702ad9dbc176c807` から専用branchで作業する。既存2 worktreesはclean、open PRなしを確認した。

写真アプリの改修、push、PR作成、merge、導入、HOME設定・memory変更は対象外。既存の人間中心設計とruntime検証を補強する文書変更で、新しい構造判断がないため別PRD・設計書は作らない。

## 単一slice・根拠と配置

| Issueの受け入れ条件 | 変更対象・責務 | 確認方法 |
| --- | --- | --- |
| メンタルモデル・外的一貫性を判断の起点にする | ui-design本文、principles、checklist | 順序・根拠区分・例外条件の整合性レビュー |
| UI作成・操作変更時の条件付き参照と設計再利用 | implement / technical-design本文 | UI通常例、非UI・軽微変更・合意済み設計の合成probe |
| 予測→採用操作→確認、物理入力・本人受入との区別 | ui-designの出力・runtime reference | 画像ビューア通常例と安全・a11y・業務条件の境界例 |

原則はui-designに集約し、technical-designは構造、implementは実装・検証を所有する。参照のための新規文書・一律承認は追加しない。plugin payload変更の既存規約によりhappy-codingのみpatchを上げる。

## 検証と戻り条件

文書sliceにRED/GREENを装わず、変更3 skillsの公式quick_validate、repo/eval validator、既存unit tests・Ruff・ty・diff checkの標準入口、plugin version gateを使う。文言一致だけの新testは作らない。

実行前固定した5つの公開可能な合成promptで旧版/変更版を別実行者に渡し、通常UI、安全性との衝突、非UI、軽微修正、合意済み設計の再利用を探索確認する。rubricや他条件出力はgeneratorへ渡さない。raw回答はrepo外に置き、結果はsanitizeした要約だけを残す。これは実app・物理gesture・本人受入・自動選択精度・統計的な効果の証明ではない。

独立reviewerは差分、ACと検証結果を確認し、修正せず指摘を返す。矛盾や不要な停止は同じsliceで修正し、要求・scopeの変更が必要な場合だけ戻す。

## 検証結果・handoff

- 変更3 skillsの公式 `skill-creator/scripts/quick_validate.py`: PASS。
- canonical `uv run --offline --python <既存Python 3.14.1> --script scripts/validate_quality.py --offline`: PASS。repo/eval validator、210 tests実行（Windowsのsymlink利用不可により4 skip）、Ruff 0.16.3、ty 0.0.74、diff check。PyYAML 6.0.3と各toolは既存cacheを一時領域へ再利用し、依存・lockfile・HOME設定・導入済みpluginは変更していない。
- 初回はsandbox既定一時pathへの書込みで失敗。TEMP指定後もlocal bare Git fixtureのpushで4 ERROR（exit 128）となった。同じ4件は制約外でPASSし、同条件のoffline全件再実行でもPASS。実GitHubへのpushはしていない。testの変更・削除・緩和なし。
- `validate_constitution.py --check-remote`: healthy。既存Gitleaks 8.30.1の `dir . --redact --timeout 60`: no leaks。
- 独立差分レビュー `/root/independent_review`: PASS、重大な指摘なし。IssueのAC、本文とreferenceの整合、責務、不要な停止、探索probeの限界を確認した。

### 探索probeの観測

旧版 `/root/probe_a`、変更版 `/root/probe_b` に同じ5つの仮想依頼を渡した。基準は出力前に固定し、条件間でgeneratorを分離した。graderは実装者でありblind比較ではない。各条件1回、hold-outなし、統計的な効果や最終採用を判定するbenchmarkではない。raw回答・ローカルpathは公開成果物へ転記していない。

| 仮想依頼 | 旧版と変更版の観測 |
| --- | --- |
| Windows写真ビューアのカレンダー・複数選択・拡大移動をtechnical-designで設計 | 両版とも具体操作とcomponent責務を提案。変更版ではui-designのruntime referenceを参照し、自動runtime・Precision Touchpad実入力・本人評価の区別と未確認を明示。旧版の当該回答は本人評価の未確認を明示していない |
| 医療画像の慣れた即削除と対象ID確認・監査・keyboard利用の衝突 | 両版とも即削除を採用せず、安全な選択・確認・取消を提案。変更版は変更理由と操作の手掛かり、未確認の復元機能を約束しない点も明示 |
| UI不変のハッシュ高速化 | 両版とも既存計画・testを再利用し、UI設計・追加承認を強制しない |
| 表示文言とアクセシブル名の誤字だけを修正 | 両版とも局所修正と影響する確認に留め、別設計書・一律承認を増やさない |
| 参照済みの合意済み複数選択設計をimplementへ渡す | 両版とも再設計・再承認せず、代表操作とfeedbackを確認する方針を示す |

基本操作を旧版でも提案できたため、一般的な品質改善効果は主張しない。今回の成果は、Issueの原則・参照導線・証拠の境界を実行規約へ明示し、上記の限定シナリオで余計な停止が増えないことを探索確認した範囲である。

### 残る範囲

写真アプリの実装・runtime、物理gestureの操作感、利用者本人の受け入れ、導入済みplugin更新とfresh sessionの読込、自動skill選択精度、Ubuntu/GitHub Actionsは未実施。スキル変更のローカル検証・レビューは完了し、実装を止める判断事項はない。配布・導入・mergeは依頼外として残す。

artifacts: `docs/plan/013_PLAN_DONE.md`。差分は専用branchで確認する。`validate_plugin_versions.py --base origin/main --head HEAD` はPASS（happy-coding 0.6.2 → 0.6.3）。これは配布側の整合性確認であり、導入・session読込の証明ではない。
