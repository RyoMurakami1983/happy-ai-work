# Editor・project・asset

既存projectの導入、依存変更、asset操作で読む。以下のURLは2026-09-06に確認した資料の版であり、採用するEditor／packageの固定指定ではない。実作業では対象versionの公式資料へ合わせる。

## versionと依存

- 既存projectのEditor版を先に読む。版の違うEditorで開くとimportやserializationの変更が起き得る。移行が必要なら変更範囲と戻せる状態を用意する。新規はHubで使えるEditor、教材、platform module、必要packageの対応を確認する。
- 「初心者なら常に最新LTS」を規約にしない。Unity公式はreleaseの用途を区別しているため、[release support](https://unity.com/releases/unity-6/support)で現時点の条件を確認する。
- [projectを開く公式説明](https://docs.unity3d.com/ja/2021.2/Manual/GettingStartedOpeningProjects.html)のversion指定とdowngradeの注意を参照する。古い説明のUI位置は現在版へ読み替える。
- manifestの要求とlockの解決結果は異なる。[Package lock files](https://docs.unity3d.com/kr/6000.0/Manual/upm-conflicts-auto.html)に従いlockを共有する。依存不具合でlockを無条件に削除したり手編集したりせず、まず互換性と解決エラーを調べる。

## assetの参照を守る

- `.meta`はGUIDを持つ。[Asset metadata](https://docs.unity3d.com/6000.0/Documentation/Manual/AssetMetadata.html)に従い、assetと対応するmetaを一緒に追跡・移動する。metaを作り直してMissing Scriptを直そうとしない。
- `Assets`、`Packages`、`ProjectSettings`と既存ignore規約を確認する。再生成される`Library`や`Temp`などを配布物へ無差別に加えない。既存ignoreやassetの扱いを全面置換しない。
- scene上のPrefab instance変更とPrefab assetの変更を分ける。[Prefab instance Inspector](https://docs.unity3d.com/ja/current/Manual/prefab-instance-inspector-reference.html)を参照し、他のinstanceへ反映される範囲を確認して必要なoverrideだけを適用する。
- Scene／Prefabの大きなYAMLを推測で生成せず、既存形式・GUID・参照を確認する。Editorを使えるならそこで接続・保存する。使えなければ小さなコード変更と具体的な接続手順で引き継げる。
