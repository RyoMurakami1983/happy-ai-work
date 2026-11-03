# Skill portfolio

## 判断基準

公開skillは、利用者が独立した目的として依頼し、他skillと異なるworkflow・検証・riskを持つものに限定します。単なる詳細知識は`references/`、常時守るrepo契約は`AGENTS.md`、機械的な品質条件はCIへ置きます。

## 今回追加した公開skill

- 継続改善: `furikaeri`、`improvement-loop`、`skill-eval`
- Issue intake: `github-issue`、`happy-add-issue`
- 言語／ecosystem: `dotnet`、`python`、`typescript`、`rust`
- .NET専門workflow: `dotnet-framework-bridge`、`nuget-local`
- framework: `wpf`、`tauri`
- 横断workflow: `repo-onboarding`、`debug-and-fix`
- 業務理解の構造化収集: `business-understanding-survey`
- 回答フォーム生成: `html-questionnaire`
- 開発成果物: `to-prd`、`technical-design`、`implement`

## プレビュー配布

`happy-preview`には実利用検証中の`yohaku`を置く。通常pluginには同梱しない。基本検証後の試用と正式化は[ADR 0004](adr/0004-preview-plugin-distribution.md)に従う。

`to-prototype`はUI設計案の操作と状態を実装前に試し、反応を設計へ戻すプレビューskill。初版は共通のHTML土台と初期化・基本検証だけを提供し、案件の画面構成を共通テンプレートで固定しない。

`technical-design-review`はhappy-codingへ昇格する。実装前の設計案を目的・要件・契約から検証し、判定と戻り先を返す独立目的を持つ。設計を作る`technical-design`、実装差分を検査する`deep-review`とは入力と判定対象を分ける。[設計・試用条件](design/007_TECHNICAL_DESIGN_REVIEW.md)を参照する。

## Yohakuの境界

`yohaku`は、人が正しく理解・判断・行動できる情報量と見せ方を整える。文章の企画や主張・構成の深い推敲は対象外とし、領域固有の判断・検証は対象skillが担当する。実装の簡素化は依頼範囲にある場合だけ扱う。

homeの常設原則は`home-bootstrap/assets/AGENTS.md`、読者に合わせた調整はYohakuへ分ける。両者は単独でも使え、他の圧縮skillを必須にしない。配置と試用条件は[設計記録](design/005_YOHAKU.md)を参照する。

## 配布変更（2026-11-03）

`technical-design-review`は実利用と既存評価の範囲を整理し、通常配布へ移動する。未使用の`video-game-design`、`unity-beginner-development`は所有者の依頼で配布を終了する。過去の設計・評価・利用記録は保持し、削除した配布物はGit履歴から復元できる。[判断根拠・未確認範囲・移行](design/017_SKILL_DISTRIBUTION.md)を参照する。

## 既存skillへ統合したもの

| 旧skill | 統合先 | 理由 |
| --- | --- | --- |
| `safe-refactor` | `implement/references/safe-refactoring.md` | 実装中のrefactor modeであり、独立起動の利用実績が薄い |
| `deep-review-preflight` | `deep-review/references/preflight.md` | 同じレビュー目的の前処理 |
| `modularity-review` | `deep-review/references/modularity.md` | 深いarchitecture reviewの一観点 |
| `modern-cs`、`type-perf`、`cs-concurrency`、`.NET setup` | `dotnet/references/` | .NET作業中に必要時だけ読む詳細知識 |
| WPF MVVM、secure config | `wpf/references/` | WPFという一つの利用目的を分割しすぎない |
| Tauri setup、sidecar、Windows distribution | `tauri/references/` | 同じ配布経路の段階差 |
| local NuGet pack／consume leaf | `nuget-local/references/` | producer／consumer modeは一つのlocal package検証目的に属する |
| `empirical-prompt-tuning` | `skill-eval/references/prompt-evaluation.md` | behavioral評価という同じ利用目的の高度なmode |
| `implementation-eval-gate` | `implement/references/eval-checklist.md`と動的subagent | slice評価は実装工程内のroleであり、独立した利用目的ではない |

## Workflow再編

- `to-prototype`は操作可能な試作と観察からUI設計を検証する。画面方針を決める`ui-design`、質問への回答を収集する`html-questionnaire`とは目的と検証条件を分ける。HTMLの生成だけで設計合意や実装承認とは扱わない。
- `html-questionnaire`は、決まった質問から回答用のオフラインHTMLを生成する独立した目的を持つ。質問と要件の合意は`interview-with-docs`、現場に聞く内容の設計は`business-understanding-survey`が担当する。公開サイトやサーバー保存はフォーム生成の範囲に含めない。入力、出力、検証条件が異なるため、質問設計skillの`references/`には統合しない。
- `domain-modeling`は、合意済みの目的・要件からドメインのモデルと業務上の契約を導く。用語整理だけなら`CONTEXT.md`等を更新し、正式なモデル化が必要な場合はドメイン文書に条件・境界を残す。目的・要件の正本は`to-prd`、技術構造は`technical-design`が担当する。[再定義の判断記録](design/006_DOMAIN_MODELING.md)を参照する。
- 旧`design-and-plan`は、構造判断を行う`technical-design`と実行順を作る`implementation-plan`へ分割した。その後、実行順の計画は`implement`へ統合し、旧skillは配布外へアーカイブした。
- 旧`debug`は、原因説明で止まらず元症状をgreenへ戻す`debug-and-fix`へ置換した。
- 各skillは暗黙選択を維持する。書込みskillの安全性はskill discoveryを無効化せず、実際の操作前の権限確認で守る。

## Coding routerの廃止（2026-09-22）

利用者が使用しないため、`coding`の配布を終了する。個別skillを直接利用できるので代替routerは新設しない。関連する入口と専用の検証を除去する。`interview-with-docs`の用語整理／条件付きモデリングは、不要な正式モデリングを避ける独立した役割があるため維持する。設計レビューも必要な案件で個別に利用する。

## Writing skillsの廃止（2026-10-01）

所有者が使用していないため、`writing-plan`、`draft-writing`、`deep-edit`の配布を終了する。少数の合成課題4組による比較でも明確な追加価値は確認できなかったが、一般的な無効性や実行性能の改善を示す評価とは扱わない。代替の統合skillは新設せず、起動候補と保守対象を3つ減らす。過去の評価・判断記録は当時の記録として保持する。

## 移植しないもの

- `copilot-authoring`: 公式`skill-creator`と競合し、Copilot instructions／agent前提が残る。
- `pptx`: 大きな旧資産を移植せず、将来のwriting deliverablesとして新規設計する。
- `knowledge-capture`: 利用実績が薄く、`domain-modeling`、repo docs、外部knowledge pluginと重なる。
- GitHub PR／CI wrapper: 公式または導入済みGitHub pluginと重なる。IssueはAPI wrapperを再実装せず、現repoの実装backlogとHappy AI Workへの軽いfeedbackという異なるintake判断だけを公開skillとして持つ。
- 固定custom agent: Codexの動的subagentまたは独立再読を使う。

## 将来の昇格条件

`incubator/`から試用配布への条件は[ADR 0004](adr/0004-preview-plugin-distribution.md)に従います。通常pluginへの採用は、次を満たして判断します。

1. 異なる実作業で複数回使われた。
2. triggerを一文で他skillと区別できる。
3. 独自の判断、検証、riskがある。
4. referencesへの統合だけでは利用者が迷う。
5. realistic promptで期待する起動と非起動を確認した。
