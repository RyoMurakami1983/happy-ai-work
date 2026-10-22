# Sidecars and distribution

## 契約

- sidecarの入力、出力、終了コード、working directory、resource pathをCLI単体で固定する。
- `externalBin`、capability、frontend呼び出し名、target tripleを同じ名前体系にする。
- secretは平文fileへ常設せず、必要なprocessへ実行時に渡す。

## Python sidecarの生存期間

頻繁なGUI操作ごとに重いPythonバックエンドを起動・終了しない。Tauriの[sidecar連携](https://v2.tauri.app/develop/sidecar/)は子processとの継続通信も扱え、毎要求の再起動はTauriの必須要件ではない。`execute`を`spawn`へ置き換えるだけでなく、起動箇所とhandleの所有者を確認する。要求handler内で毎回`spawn`すれば起動費用は繰り返される。

Python連携を設計・診断するときは[PythonのGUI起動費用](../../python/references/coding-practices.md#guiから使うpythonの起動費用)を読む。アプリ／セッション単位の再利用と軽い処理の分離を比較し、常駐化にはready・timeout・protocol・異常終了・子process回収を含める。単発CLIやEXE、one-file形式の一律禁止ではなく、用途に合う寿命を選ぶ。

下記のTauri application／install後gateでは、初回起動・最初の要求・継続操作を分けて実配布物で測定する。複数要求を含む代表フローの応答とprocess起動数を確認する。非同期化はUI停止の対策であり、起動待ち時間をなくす保証ではない。

## 昇格gate

1. raw CLI／binary
2. package後のsidecarを直接起動するsmoke
3. Tauri applicationからの代表フロー
4. bundle payload確認
5. install後の代表フロー
6. 必要ならclean Windows

各gateで同じ代表入力を使う。package後だけ壊れる場合は、bytecode／runtime差、相対path、resource、権限、環境変数、working directoryを比較する。

Node sidecarのpackagerやSEA方式はrepoのruntime要件とmaintenance状況で選び、旧skillの特定packageを既定にしない。clean環境を未確認なら、release準備完了ではなく未検証として残す。
