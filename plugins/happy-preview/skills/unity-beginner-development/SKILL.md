---
name: unity-beginner-development
description: プレビュー（実利用検証中）。Unity初心者のゲーム試作・実装・不具合修正を、Editor、C# component、Scene、Prefab、入力、動作確認までつなぐ。Unityでゲームを作る・動かす依頼で使う。遊びの企画だけやUnity外の一般.NET開発には使わない。
---

# Unity Beginner Development

試用版。基本検証と模擬依頼を確認済みだが、実Unity projectでの検証はこれから。試用ではScene・Inspectorの接続と実行まで再現できるかを確認する。

小さな遊べる変更を、利用者がUnity上で再現・調整できる状態まで作る。C#ファイルだけで完成とせず、GameObjectへの接続、Inspectorの参照、Sceneの保存、実行時の結果を扱う。

## 進め方

1. 既存projectがあれば`ProjectSettings/ProjectVersion.txt`、`Packages/manifest.json`、`Packages/packages-lock.json`、既存Scene、入力方式、render pipeline、対象platformを確認する。新規なら作る遊び・入力機器・2D／3D・配布先に必要な不足だけを聞く。
2. [project-and-assets.md](references/project-and-assets.md)に従い、projectに合うEditorとpackageを使う。機能追加へEditor移行を無条件に混ぜない。新規も特定のLTS番号を固定せず、公式のサポート状況と教材・package互換性から選ぶ。
3. 操作→反応→目的または試行→再開のうち、今必要な最小部分を選ぶ。面白さやルールが未定なら`video-game-design`で詰めるが、既に明確な実装依頼を企画からやり直さない。
4. [components-and-input.md](references/components-and-input.md)を使い、既存Scene／Prefab／component構成に合わせて実装する。新しい抽象化やpackageは、今回の挙動に必要な場合だけ加える。
5. [verification.md](references/verification.md)に従い、コンパイル、Scene上の接続、Play Mode、必要なテスト、対象platformのbuild・実行を変更範囲に応じて確認する。できなかった段階は未確認と残す。

## 初心者への引継ぎ

変更したファイルに加え、次の情報を実際のproject名・object名で伝える。

- 開くSceneと、scriptを付けるGameObject
- 必要なcomponent、Inspectorで割り当てる参照・調整値
- Playして行う操作と、期待する画面の変化
- 実行済みの確認と、利用者がEditorで確認する残りの手順

Editorを操作できない場合は、接続操作を具体的に渡す。接続済み・実行済みとは報告しない。EditorのメニューやAPIは対象versionの公式資料で確認し、古い教材との差を説明する。

## 境界

- Unity生成の`.csproj`を通常の.NET projectとして改変しない。`dotnet build/test`だけでUnityの正常動作を認定しない。独立した.NET libraryや外部toolは`dotnet`が利用可能ならつなぎ、なければそのprojectの既存契約に従う。
- `implement`と組み合わせる場合は実装工程を複製せず、Unity固有の接続・検証契約を補う。
- ゲーム設計の変更で不具合を隠さない。実装上の制約で遊びを変える必要があれば、その影響を示す。
- 実装の成功と、人が楽しめることを分ける。build成功を面白さの証明にしない。
