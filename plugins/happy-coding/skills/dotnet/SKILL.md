---
name: dotnet
description: C#／.NETリポジトリのSDK・solution・project・build contractを読み、既存規約を尊重して実装・テスト・検証する。.NETコードの変更、環境構築、移行、ビルド診断で使う。WPF固有の画面設計はwpfを使う。
---

# .NET

.NETの一般知識を押し付けず、対象repoが宣言するSDK、target framework、analyzer、nullable、テスト基盤を先に特定する。

## ワークフロー

1. `global.json`、`.slnx`／`.sln`、`*.csproj`、`Directory.Build.*`、`Directory.Packages.props`、`.config/dotnet-tools.json`、`.editorconfig`を確認する。
2. SDK、target framework、package管理、build／testコマンドをrepoの正本から確定する。詳細は[project-contract.md](references/project-contract.md)を読む。
3. project／solution／package操作に対応する`dotnet` CLIがある場合は、構造を手書きする前にCLIを検討する。既存形式の無断移行はしない。
4. C#実装ではnullable、例外境界、resource lifetime、非同期、既存DI／logging規約を守る。必要なら[csharp-practices.md](references/csharp-practices.md)を読む。
5. 並行性または性能が変更理由なら、計測と所有権を先に固定し、[concurrency-and-performance.md](references/concurrency-and-performance.md)を読む。
6. repoが定義する順序でrestore、build、test、format／analyzerを実行し、未実行項目を明示する。

repoへ永続的な.NET規約を追加するよう依頼された場合だけ、[AGENTS.fragment.md](assets/AGENTS.fragment.md)を対象repoに合わせて最寄りの`AGENTS.md`へ統合する。

## 境界

- WPFのXAML、binding、MVVM、設定保護は`wpf`へ渡す。
- .NET Frameworkとモダン.NETの橋渡しは、実案件が生じた時点で独立skill化を再評価する。
- warning suppression、`NoWarn`、null-forgiving、reflectionを安易な逃げ道にしない。
- formatterやanalyzerで機械的に強制できるstyleを長い指示として重複させない。
