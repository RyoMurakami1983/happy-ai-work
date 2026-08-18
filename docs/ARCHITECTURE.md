# Architecture

## 配布モデル

repo内marketplaceが2つのpluginを配布します。plugin間でskillを暗黙依存させず、利用可能なら別skillへhandoffする形にします。

## 指示の配置

- home共通方針: `~/.codex/AGENTS.md`
- repo共通方針: repoルートの `AGENTS.md`
- サブツリー固有方針: 必要なディレクトリの `AGENTS.md`
- 繰り返しworkflow: plugin内の `skills/<name>/SKILL.md`

## レビュー

固定agentファイルは配布しません。`deep-review` は利用可能なCodex subagentを動的に使い、利用できない環境では独立した再読パスへ切り替えます。Copilot CLIは将来の実験的オプションです。
