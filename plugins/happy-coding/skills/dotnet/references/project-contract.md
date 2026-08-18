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
