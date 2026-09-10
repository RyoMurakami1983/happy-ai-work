# happy-ai-work

> 仕事・学習・ライティング・コーディングを継続的に改善する Codex 用 skills／plugins／workspace template の母艦。

CodexデスクトップアプリとCodex CLIで再利用するワークフローを、通常配布の2つのpluginと試用用pluginとして管理します。

## Constitution

公式`happy-ai-work`の開発・評価・配布判断は[CONSTITUTION.md](CONSTITUTION.md)を正本とし、日常判断では[Constitution Summary](docs/CONSTITUTION_SUMMARY.md)を入口にします。個人philosophy、repo固有Mission、public利用先のdownstream Constitutionを分離し、村上さん固有の価値観をplugin利用先へ暗黙適用しません。

公開評価case、private eval、sealed hold-out、sanitize済み履歴の境界は[Evaluation assets](docs/EVALUATION_ASSETS.md)を参照してください。

## Plugins

| plugin | 用途 |
| --- | --- |
| `happy-core` | home／workspace初期化、文章の構成・下書き・推敲 |
| `happy-coding` | インタビュー、PRD、設計、実装、言語／framework支援、デバッグ、評価、レビュー、CI対応 |
| `happy-preview` | 正式採用前のskillsを任意導入して試用（実利用検証中） |

## 導入

GitHub上のrepoをmarketplaceとして登録し、必要なpluginを導入します。事前のcloneは不要です。

```powershell
codex plugin marketplace add https://github.com/RyoMurakami1983/happy-ai-work
codex plugin add happy-core@happy-ai-work-marketplace
codex plugin add happy-coding@happy-ai-work-marketplace
```

repoをclone済みの場合は、repoルートで `codex plugin marketplace add .` を実行してローカルのmarketplaceを登録することもできます。

Codexアプリではplugin画面から `Happy AI Work` を開き、必要なpluginを導入します。

## 主要skills

### happy-core

- `interview-me`: 重要な意思決定を具体例・反例まで質問で深掘り
- `home-bootstrap`: `~/.codex/AGENTS.md` の管理対象部分を安全に導入・更新し、Git指示とHooksの初期設定を案内
- `workspace-bootstrap`: repo用 `AGENTS.md` と最小基盤を対話的に準備
- `github-issue`: 現repoの後続作業を実行可能なGitHub Issueへ整理
- `happy-add-issue`: Happy AI Workへのfeedbackを母艦Issueへ安全に記録
- `writing-plan`: 読者と目的から文章構成を設計
- `draft-writing`: 合意済み構成から日本語初稿を作成
- `deep-edit`: 主張・構成・論理・読みやすさ・正確性の順に推敲
- `furikaeri`: 今日の実績からY／W／T、通常タスク、改善候補を整理
- `improvement-loop`: 選択済みの改善候補を次のタスク、検証、採否判断へつなぐ
- `skill-eval`: 既存skillのtriggerと振る舞いをrealistic scenarioで評価

### happy-coding

- 明示オーケストレーション: `$coding`（通常依頼には暗黙発火しない）
- 要求から実装: `interview-with-docs`、`business-understanding-survey`、`domain-modeling`、`to-prd`、`technical-design`、`implementation-plan`、`implement`
- 業務理解の収集: `business-understanding-survey`（資料の未知を、目的に合う確認・選択・比較・自由記述へ変換）
- 言語／ecosystem: `dotnet`、`python`、`typescript`、`rust`、`dotnet-framework-bridge`、`nuget-local`
- framework: `wpf`、`tauri`
- UI設計・評価: `ui-design`
- 調査・修正: `repo-onboarding`、`debug-and-fix`
- 品質: `deep-review`、`ci-debug`

`coding`は必要な工程だけを選ぶrouterです。PRD、technical design、implementation planを常に全部作るのではなく、入力artifactとriskに応じて省略します。

旧repoのleaf skillをそのまま並べず、独立した利用目的がない詳細は各skillの`references/`へ統合しています。移植判断は[docs/SKILL-PORTFOLIO.md](docs/SKILL-PORTFOLIO.md)を参照してください。

### happy-preview（試用版）

試したい場合だけ、marketplaceの`Happy Preview（試用版）`を導入してください。通常pluginへの同梱や既定導入は行いません。導入後のskillは通常どおり自動選択されます。

- [video-game-design](plugins/happy-preview/skills/video-game-design/SKILL.md): 宮本茂を軸に14名の知見から遊び・試作・観察を設計
- [unity-beginner-development](plugins/happy-preview/skills/unity-beginner-development/SKILL.md): Unity初心者の実装・Scene接続・動作確認
- [linux-deploy](plugins/happy-preview/skills/linux-deploy/SKILL.md): Linuxへの配置・更新を実測、データ権限の検証、失敗診断・再実行まで扱う

初版は基本検証と模擬依頼を確認済みで、実制作での検証はこれからです。試用時は「作りたかったもの、実際の成果、困った点、次に直すこと」を残します。ゲーム設計では試作へ渡せたか、Unityでは接続・実行できたかを確かめます。記録に実名や実案件の未加工データは不要です。

Linuxデプロイの初版は模擬判断と読取コマンドを確認し、実デプロイ・障害復旧は未検証です。[設計と試用条件](docs/linux-deploy-preview.md)に従い、確認漏れと修正再実行を減らせるかを確かめます。

実利用と修正後の確認を経て、採用したskillは通常pluginへ移します。移動先と導入変更はその際に案内します。配布・正式化・公式機能への移行方針は[ADR 0004](docs/adr/0004-preview-plugin-distribution.md)を参照してください。

## 作成途中のworkflow

未完成の案はplugin外の[incubator/](incubator/)で扱います。ここにある候補はインストールされません。旧`pptx`は移植せず、将来のwriting deliverablesを実利用から新規設計します。

## home用AGENTS.md

Codex全体へ適用する指示は、通常 `~/.codex/AGENTS.md` に置きます。Windowsでは `%USERPROFILE%\.codex\AGENTS.md` です。

`home-bootstrap` は既存内容を全置換せず、管理対象マーカー内だけを更新します。最初に必ずdry-runします。

適用時にはCodexのGit設定へ貼り付ける3つの指示文と自動マージの設定を案内します。Hooksは未設定を許容し、候補の影響と差分を確認してから明示承認された項目だけを設定します。

```powershell
uv run --no-project --python 3.14 python plugins/happy-core/skills/home-bootstrap/scripts/home_bootstrap.py --dry-run
```

## 開発

```powershell
uv run --script scripts/validate_quality.py
```

検証入口はPython 3.14と一時環境のPyYAML、Ruff、tyを固定versionで使用します。詳細は [repo quality validation](docs/development/QUALITY_VALIDATION.md) を参照してください。

WSL2の確認範囲は [docs/WSL2.md](docs/WSL2.md) を参照してください。

## ライセンス

MIT License
