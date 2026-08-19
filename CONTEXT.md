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

- **今日のタスク**: 実行日が今日に確定した行動。Notionが利用可能な運用では、今日の実行viewの正本とする。
- **次のタスク**: 実行可能だが、実行日が未確定または将来日に設定された行動。「明日のタスク」は、翌日の具体的な日付に確定した次のタスクである。
- **改善候補**: ふりかえりのWから導いたTのうち、通常の後続作業ではなく、process、道具、skill、plugin、docs、運用を良くする可能性がある行動候補。
- **改善実験**: 選択済みの改善候補を、改善仮説、反対仮説、最小実験、反証条件、完了条件を持つ次のタスクへ具体化したもの。
- **改善済み**: タスク登録や変更実行ではなく、効果を評価し、採用、継続、破棄、保留の判断まで終えた状態。
- **技術課題の正本**: repoで継続追跡する課題はGitHub Issueを正本とする。NotionにはIssue本文を複製せず、リンクとその日に実行する一歩を置く。

## Distribution

`happy-ai-work-marketplace` から `happy-core` と `happy-coding` を個別に導入する。各pluginのmanifestを正本とし、marketplaceは配布順と導入policyを管理する。
