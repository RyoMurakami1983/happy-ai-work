# Context

## Mission

仕事・学習・ライティング・コーディングを継続的に改善するためのCodexワークフローを、少人数で再利用・検証・更新できる形にする。

## Users

- 主利用者: リポジトリ所有者
- 副利用者: 信頼できる少人数の共同利用者

## Product boundaries

- CodexデスクトップアプリとCodex CLIを対象にする。
- Windowsを第一対象とし、Ubuntu CIとWSL2の早期検証を行う。
- `happy-core` は仕事・学習・ライティング・環境初期化・ふりかえり・改善ループ・Issue intake・skill評価を扱う。Issue操作自体を再実装せず、実装backlogと軽いfeedbackの行き先を判断する。
- `happy-coding` は明示オーケストレーション、要件整理、technical design、implementation plan、実装、言語／framework支援、debug-and-fix、レビュー、CI対応を扱う。
- 未完成候補はplugin外の`incubator/`へ置き、実利用で価値を確認するまで配布しない。
- Copilot CLI連携は初版の必須機能にしない。

## Domain language

### Governance

- **個人philosophy**: リポジトリ所有者自身の変化を含むVision、Mission、Values。Happyの運用規則、repo固有のMission、個人の経歴とは区別する。
- **Happy Constitution**: 個人philosophyをHappyが自律判断に使える原則と統治境界へ翻訳した、version付きの判断基準。個人philosophyの全文複製ではない。
- **安全・評価整合性**: secret保護、破壊操作の抑止、独立評価、過去結果の非改ざんなど、upstream／downstreamの価値観で緩和できない共通境界。
- **upstream Constitution**: リポジトリ所有者の個人philosophyを、公式`happy-ai-work`の開発と配布判断へ翻訳したHappy Constitution。
- **downstream Constitution**: clone、fork、plugin利用先の所有者が、自身のphilosophyと優先順位を定義する判断基準。upstream固有の価値観を置換できるが、安全・評価整合性は緩和できない。
- **Constitution resolution**: 利用先ではdownstream Constitution、既存のrepo方針、共通の安全・評価整合性の順に責務を分けて判断すること。downstream Constitutionがなくてもupstream固有の価値観を暗黙適用しない。
- **判断プロファイル（トレードオフプロファイル）**: Constitutionを変更せず、特定の文脈で原則間の相対的な重み、尺度のanchor、具体例、判断理由を表すversion付きの基準。単一の点数や評価結果ではない。
- **private eval**: 組織固有の目的に対する「何が良いか」をscenario、rubric、期待結果、実測履歴として所有・管理し、AIの改善を測る評価資産。判断プロファイルそのものとは区別する。
- **upstream eval**: リポジトリ所有者が公開を承認し、公式`happy-ai-work`の改善を測る実評価。public repoに置けるが、plugin配布先では既定で適用しない。
- **共通安全eval**: 個人philosophyに依存せず、安全・評価整合性の共通境界を検証する公開評価。upstream／downstreamの双方へ適用する。
- **通常の運用改善**: 現行Constitutionの価値観と優先順位を変えず、観測、手順、表現、再現性を改善する変更。Happyが自律的に判断できる。
- **Constitution amendment**: 原則の追加、削除、意味、優先順位、または安全・独立性の境界を変える変更。リポジトリ所有者の明示判断を必要とする。
- **Constitution vNext**: 現行Constitutionを置き換える前の改訂案。旧基準との影響比較を伴い、壁打ちと明示承認が終わるまでは判断基準として有効にならない。
- **governance drift**: 個人philosophyまたはHappy Constitutionの意味のある変更について、他方へ反映するか不要とするかの同期判断が未完了な状態。単なる文言差やファイル時刻差ではない。
- **評価constitution**: 評価の独立性、基準固定、結果保存、改訂方法を定める不変条件。個々のscenarioや採点項目そのものとは区別する。
- **評価record**: 使用したConstitutionと評価基準のversion、固定済みscenario、観測結果、判定を結び付けた履歴。再評価しても過去recordを上書きしない。
- **通常評価（A）**: 固定済み基準でPASSまたはFAILを確定できる評価mode。
- **判定不能（B）**: 基準の曖昧さなどにより妥当な判定を出せず、証拠を保存して別versionでの再評価へ送る評価mode。
- **緊急例外（C）**: 納期または安全上の緊急性から暫定判断する評価mode。通常評価のPASSではない。

- **今日のタスク**: 実行日が今日に確定した行動。Notionが利用可能な運用では、今日の実行viewの正本とする。
- **次のタスク**: 実行可能だが、実行日が未確定または将来日に設定された行動。「明日のタスク」は、翌日の具体的な日付に確定した次のタスクである。
- **改善候補**: ふりかえりのWから導いたTのうち、通常の後続作業ではなく、process、道具、skill、plugin、docs、運用を良くする可能性がある行動候補。
- **改善実験**: 選択済みの改善候補を、改善仮説、反対仮説、最小実験、反証条件、完了条件を持つ次のタスクへ具体化したもの。
- **改善済み**: タスク登録や変更実行ではなく、効果を評価し、採用、継続、破棄、保留の判断まで終えた状態。
- **技術課題の正本**: repoで継続追跡する課題はGitHub Issueを正本とする。NotionにはIssue本文を複製せず、リンクとその日に実行する一歩を置く。

## Distribution

`happy-ai-work-marketplace` から `happy-core` と `happy-coding` を個別に導入する。各pluginのmanifestを正本とし、marketplaceは配布順と導入policyを管理する。
