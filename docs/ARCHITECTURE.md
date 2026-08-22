# Architecture

## 配布モデル

repo内marketplaceが2つのpluginを配布します。plugin間でskillを暗黙依存させず、利用可能なら別skillへhandoffする形にします。

## 指示の配置

- 公式upstreamの原則と統治境界: root `CONSTITUTION.md`
- AIの日常参照と停止条件: `docs/CONSTITUTION_SUMMARY.md`
- 文脈依存の価値比較: `docs/governance/UPSTREAM_DECISION_PROFILE.md`
- home共通方針: `~/.codex/AGENTS.md`
- repo共通方針: repoルートの `AGENTS.md`
- サブツリー固有方針: 必要なディレクトリの `AGENTS.md`
- 繰り返しworkflow: plugin内の `skills/<name>/SKILL.md`
- 条件付きの詳細知識: 各skillの`references/`
- target repoへ導入する短い規約: 各言語skillの`assets/AGENTS.fragment.md`
- 機械的な強制: target repoのformatter、linter、analyzer、test、CI

CodexにはCopilotの`applyTo`付き`*.instructions.md`と同じ配布形式がないため、言語固有知識をskillへ、常時必要なrepo契約を最寄りの`AGENTS.md`へ分けます。

個人philosophyの全文、repo固有Mission、skill手順、評価scenarioはConstitutionへ混在させません。plugin利用先ではdownstream Constitutionを尊重し、存在しない場合もupstream固有価値を暗黙適用しません。

## Skill境界

- 公開skillは独立した利用目的と検証境界を持つものに限定します。
- 一つの目的の詳細modeは公開leaf skillではなく`references/`へ置きます。
- 未完成候補は`incubator/`へ置き、pluginから配布しません。
- portfolio判断は[SKILL-PORTFOLIO.md](SKILL-PORTFOLIO.md)を正本とします。

## Workflow orchestration

- `coding`は明示呼び出し専用のrouterとし、`agents/openai.yaml`で`allow_implicit_invocation: false`を指定します。
- routerは子skillの手順を複製せず、工程のentry / exit、skip理由、evidence、戻り先だけを管理します。
- PRDはwhy / who / what、technical designはhow、implementation planはorder、implementはcodeとslice gateを所有します。
- 工程内だけで使う評価役は公開leaf skillにせず、`implement/references/`と動的subagentへ置きます。
- `debug-and-fix`の並列調査は、red/green commandを固定した後のread-only evidence gatheringに限定します。

## レビュー

固定agentファイルは配布しません。`deep-review` は利用可能なCodex subagentを動的に使い、利用できない環境では独立した再読パスへ切り替えます。Copilot CLIは将来の実験的オプションです。
