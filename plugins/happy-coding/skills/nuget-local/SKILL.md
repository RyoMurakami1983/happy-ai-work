---
name: nuget-local
description: 自作NuGet packageをローカルfeedへpackし、consumer repoでsource・version・restore・buildを分離して検証する。未公開packageの動作確認、legacy packages.config、PackageReference、pack／consume失敗の切り分けで使う。
---

# Local NuGet workflow

producerとconsumerの失敗境界を混ぜず、package identity、version、source precedence、artifactを明示して検証する。

## ワークフロー

1. producer／consumerのSDK、project形式、target framework、NuGet config、central package managementを確認する。
2. package IDとテスト用versionを固定し、既存public packageとの衝突やdependency confusionを避ける。
3. package作成側では[pack.md](references/pack.md)を使い、Release build、pack、nupkg内容を確認する。
4. consumer側では[consume.md](references/consume.md)を使い、feed登録、参照追加、restore、build、testを順に確認する。
5. producer sourceを直接参照した状態とpackage経由を混同せず、consumerが実際に選んだsourceとversionを記録する。
6. 検証後は一時feed、config、cache、test versionを残すか削除するか明示する。

## 境界

- machine固有の絶対pathを共有`NuGet.Config`へcommitしない。
- `dotnet add package`等で表現できる操作はcommandを優先し、project file手編集はlegacy不整合の局所修正に限る。
- credential付きprivate feedは別の認証workflowとして扱い、secretをconfigへ書かない。
- package公開は扱わない。localでのpack／consume検証までとする。
