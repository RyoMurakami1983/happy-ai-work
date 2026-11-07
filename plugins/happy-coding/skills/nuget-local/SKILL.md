---
name: nuget-local
description: 自作NuGet packageをローカルfeedへpackし、consumer repoでsource・version・restore・buildを分離して検証する。未公開packageの動作確認、legacy packages.config、PackageReference、pack／consume失敗の切り分けで使う。
---

# Local NuGet workflow

producerとconsumerを分け、package identity・version・source precedence・artifactを根拠にlocal pack／consumeを検証する。公開は扱わない。

1. 両repoのSDK、project形式、target framework、NuGet config、central package managementを確認する。
2. package ID・テストversionを固定し、public packageとの衝突とdependency confusionを避ける。
3. producerは[pack.md](references/pack.md)でRelease build→pack→nupkg内容を確認する。
4. consumerは[consume.md](references/consume.md)でfeed登録→参照追加→restore→build→testを確認する。source直参照とpackage経由を区別し、実際に選ばれたsource・versionを記録する。
5. 一時feed・config・cache・test versionの残置／削除を明示する。

machine固有の絶対pathを共有`NuGet.Config`へcommitしない。`dotnet add package`等のcommandを優先し、project手編集はlegacy不整合の局所修正に限る。credential付きprivate feedは別認証workflowとし、secretをconfigへ書かない。
