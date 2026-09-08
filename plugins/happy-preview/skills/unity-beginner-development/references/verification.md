# 検証と完了の伝え方

Unity Editorの利用可否、対象platform module、既存テスト構成を最初に確認する。必要な段階は今回の変更から決め、全プロトタイプへ大規模なテスト基盤を追加しない。

GUIが使えなくてもEditor executableがあれば[batch mode](https://docs.unity3d.com/6000.0/Documentation/Manual/EditorCommandLineArguments.html)で可能な検証を調べる。同じprojectをGUI Editorで開いている間に別のbatch processを重ねない。

| 段階 | 分かること | まだ分からないこと |
| --- | --- | --- |
| 静的確認 | コード・参照設定の整合の一部 | Unity import、実コンパイル、画面動作 |
| Editor import／compile | 対象Editorで読み込める | 入力や遊びの成立 |
| Edit Mode test | 純粋なルールやEditor処理の期待結果 | 実際のScene接続・入力 |
| Play Mode／操作確認 | 接続したSceneの状態遷移・入力・再開 | 配布先固有の動作 |
| 対象platform buildと実行 | 実行物の起動と確認した挙動 | 全deviceの互換性・面白さ |

自動テストはスコア、勝敗、再開による状態リセットなど、壊れると影響する挙動へ使う。単にfield名や実装の行数を確認するテストを増やさない。既存Unity Test Frameworkのassemblyとplatform設定に従う。[Edit Mode vs. Play Mode](https://docs.unity3d.com/Packages/com.unity.test-framework@1.4/manual/edit-mode-vs-play-mode-tests.html)

操作確認は、開くScene、使う入力、開始→主操作→結果→再開の具体的な手順で行い、Consoleの関連エラーを確認する。実装した境界（空中入力、連打、二重加点等）だけを追加で調べる。

配布が目的なら、対象platformのSceneと設定を確認し、生成物の起動まで進める。[Build profiles](https://docs.unity3d.com/6000.0/Documentation/Manual/build-profiles.html)はUnity 6の入口であり、旧版へメニュー名をそのまま当てはめない。

Editorがない環境では、読めたコードと設定、実行できなかったimport・compile・Play Mode・buildを分けて報告する。推測した成功ログを作らず、Editorで行う最短の接続・確認手順を渡す。人によるプレイ観察は別の検証として、未実施なら未実施のまま残す。
