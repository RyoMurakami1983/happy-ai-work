# Skill portfolio

## 判断基準

公開skillは、利用者が独立した目的として依頼し、他skillと異なるworkflow・検証・riskを持つものに限定します。単なる詳細知識は`references/`、常時守るrepo契約は`AGENTS.md`、機械的な品質条件はCIへ置きます。

## 今回追加した公開skill

- 継続改善: `furikaeri`、`skill-eval`
- 言語／ecosystem: `dotnet`、`python`、`typescript`、`rust`
- framework: `wpf`、`tauri`
- 横断workflow: `repo-onboarding`、`debug`

## 既存skillへ統合したもの

| 旧skill | 統合先 | 理由 |
| --- | --- | --- |
| `safe-refactor` | `implement/references/safe-refactoring.md` | 実装中のrefactor modeであり、独立起動の利用実績が薄い |
| `deep-review-preflight` | `deep-review/references/preflight.md` | 同じレビュー目的の前処理 |
| `modularity-review` | `deep-review/references/modularity.md` | 深いarchitecture reviewの一観点 |
| `modern-cs`、`type-perf`、`cs-concurrency`、`.NET setup` | `dotnet/references/` | .NET作業中に必要時だけ読む詳細知識 |
| WPF MVVM、secure config | `wpf/references/` | WPFという一つの利用目的を分割しすぎない |
| Tauri setup、sidecar、Windows distribution | `tauri/references/` | 同じ配布経路の段階差 |
| `empirical-prompt-tuning` | `skill-eval/references/prompt-evaluation.md` | behavioral評価という同じ利用目的の高度なmode |

## 移植しないもの

- `copilot-authoring`: 公式`skill-creator`と競合し、Copilot instructions／agent前提が残る。
- `pptx`: 大きな旧資産を移植せず、将来のwriting deliverablesとして新規設計する。
- `knowledge-capture`: 利用実績が薄く、`domain-modeling`、repo docs、外部knowledge pluginと重なる。
- GitHub PR／Issue／CI wrapper: 公式または導入済みGitHub pluginと重なる。
- 固定custom agent: Codexの動的subagentまたは独立再読を使う。

## 将来の昇格条件

`incubator/`の候補は、次を満たした場合だけ公開skillへ昇格します。

1. 異なる実作業で複数回使われた。
2. triggerを一文で他skillと区別できる。
3. 独自の判断、検証、riskがある。
4. referencesへの統合だけでは利用者が迷う。
5. realistic promptで期待する起動と非起動を確認した。
