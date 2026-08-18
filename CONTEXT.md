# Context

## Mission

仕事・学習・ライティング・コーディングを継続的に改善するためのCodexワークフローを、少人数で再利用・検証・更新できる形にする。

## Users

- 主利用者: リポジトリ所有者
- 副利用者: 信頼できる少人数の共同利用者

## Product boundaries

- CodexデスクトップアプリとCodex CLIを対象にする。
- Windowsを第一対象とし、Ubuntu CIとWSL2の早期検証を行う。
- `happy-core` は仕事・学習・ライティング・環境初期化を扱う。
- `happy-coding` は要件整理・設計・実装・評価・レビュー・CI対応を扱う。
- Copilot CLI連携は初版の必須機能にしない。

## Distribution

`happy-ai-work-marketplace` から `happy-core` と `happy-coding` を個別に導入する。各pluginのmanifestを正本とし、marketplaceは配布順と導入policyを管理する。
