# .NET project contract

## 最初に確認する正本

- `global.json`: SDK選択とroll-forward方針
- `.slnx`／`.sln`: solution境界
- `*.csproj`: target framework、SDK、project／package reference
- `Directory.Build.props`／`Directory.Build.targets`: repo共通build規約
- `Directory.Packages.props`: central package management
- `.config/dotnet-tools.json`: local tool contract
- `.editorconfig`: analyzer severityとstyle

既存形式を尊重する。新規solutionでは利用可能なSDKとチーム方針を確認して`.slnx`を検討するが、依頼なしに既存`.sln`を移行しない。

## 検証

repo固有コマンドがなければ、変更範囲に応じて次を候補にする。

```powershell
dotnet restore
dotnet build --no-restore
dotnet test --no-build
dotnet format --verify-no-changes
```

同じsolution／configuration／runtimeを使い、ローカルとCIで対象がずれないようにする。失敗時はSDK不一致、restore、compile、test、analyzerのどこで止まったかを分離する。

起動中アプリや並列buildが同じ出力先を使う場合は、検証前に出力lockの競合を確認し、repoで認められた別出力先などで分離する。無断でアプリを終了しない。lockによる未実行をtest失敗と混同せず、同条件で再実行するときは理由を短く残す。必要な修正後の回帰確認は省かない。
