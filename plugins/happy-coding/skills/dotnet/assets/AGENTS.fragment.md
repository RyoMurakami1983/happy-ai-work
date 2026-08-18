## .NET working agreement

- `global.json`、`Directory.Build.*`、`Directory.Packages.props`、project／solution形式をbuild contractとして尊重する。
- project、solution、package操作は、対応する`dotnet` CLIがある場合はCLIを優先する。
- nullable／analyzer警告は抑制より根本原因を修正する。
- 変更後は、このrepoが定義するrestore、build、test、format／analyzerを実行する。
