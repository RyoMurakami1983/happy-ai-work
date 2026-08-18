# Pack local package

1. `*.csproj`、`.nuspec`、`Directory.Build.*`、`Directory.Packages.props`、`global.json`を確認する。
2. SDK-styleかlegacy projectか、pack対象libraryかを判定する。
3. 一意なprerelease versionと出力先を決める。
4. Release buildを通してからpackする。

SDK-styleの例:

```powershell
dotnet pack path/to/Library.csproj -c Release -o artifacts/local-feed -p:PackageVersion=0.0.0-local.1
```

legacy projectでは既存の`.nuspec`、MSBuild、`nuget.exe`手順を尊重する。生成後はnupkg内のtarget framework、assembly、dependency、props／targets、symbol／source metadataを確認する。test projectやapplicationを誤ってpackしない。
