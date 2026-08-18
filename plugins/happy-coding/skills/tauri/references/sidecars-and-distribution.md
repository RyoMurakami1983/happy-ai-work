# Sidecars and distribution

## 契約

- sidecarの入力、出力、終了コード、working directory、resource pathをCLI単体で固定する。
- `externalBin`、capability、frontend呼び出し名、target tripleを同じ名前体系にする。
- secretは平文fileへ常設せず、必要なprocessへ実行時に渡す。

## 昇格gate

1. raw CLI／binary
2. package後のsidecarを直接起動するsmoke
3. Tauri applicationからの代表フロー
4. bundle payload確認
5. install後の代表フロー
6. 必要ならclean Windows

各gateで同じ代表入力を使う。package後だけ壊れる場合は、bytecode／runtime差、相対path、resource、権限、環境変数、working directoryを比較する。

Node sidecarのpackagerやSEA方式はrepoのruntime要件とmaintenance状況で選び、旧skillの特定packageを既定にしない。clean環境を未確認なら、release準備完了ではなく未検証として残す。
