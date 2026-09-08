# Windows development loop

## repoの実行契約を確認する

lockfile、frontend manifestのscripts、Tauri dependency、`tauri.conf.*`を読み、repoが実際に使うpackage manager、dev script、Tauri majorを確定する。READMEとCIに実行方法があれば整合も確認する。特定のpackage manager、script名、生成物名を推測で固定しない。

反復開発では、確定したpackage managerからrepo既定のTauri dev scriptを実行することを第一候補にする。frontendのhot reloadとRust側の再コンパイルを同じ入口で扱えるためである。実行した入口と、確認できたfrontend／Rustの範囲を報告する。

## 実行方法の役割を分ける

| 入口 | 主な目的 | 注意点 |
| --- | --- | --- |
| dev起動 | 日常の反復開発、frontend更新、Rust変更後の代表フロー確認 | 配布物の成立は保証しない |
| frontend build／Rust build | 各層のcompile、lint、test、境界エラーの切り分け | Tauri applicationとしての統合動作は別に確認する |
| 生成済みEXEの直接確認 | build済み成果物の節目のsmoke、dev server非依存部分の確認 | 古い成果物の可能性があり、起動中は次のbuild出力をlockし得る。確認後は通常終了する |
| bundle／installer検証 | payload、install、起動、resource、権限、uninstallなど配布固有の確認 | 日常の実装loopには使わず、必要な昇格gateで実行する |

失敗を切り分けるときは入口を混ぜない。たとえばfrontend build、Rust build、dev起動、生成済みEXE、bundle／installerのどこで初めて失敗するかを記録する。

## 実行中バイナリによるアクセス拒否を診断する

再ビルドが出力ファイルの削除・置換でアクセス拒否になった場合、直ちにtoolchain障害と判断しない。エラーに表示された対象出力の絶対pathを使い、そのファイルを実行中のprocessがないか確認する。

PowerShellでは、対象pathを解決して実行ファイルpathが一致するprocessだけを列挙する。

```powershell
$lockedOutput = (Resolve-Path -LiteralPath '<errorに表示された出力path>').Path
Get-CimInstance Win32_Process |
    Where-Object { $_.ExecutablePath -eq $lockedOutput } |
    Select-Object ProcessId, Name, ExecutablePath, CommandLine
```

結果がない場合は、対象pathの誤り、権限不足、別processによるfile handle、security softwareなどを次の仮説にする。利用可能ならResource Monitorや組織で承認されたhandle確認toolで、同じ対象pathを調べる。

processを停止する前に、少なくとも次を確認する。

- `ProcessId`、`ExecutablePath`、`CommandLine`が今回の出力と一致する
- dev起動、手動smoke、testなど、そのprocessを起動した経路
- 停止による未保存状態、進行中test、他利用者への影響

まずapplicationの通常終了を優先する。強制停止が必要なら、確認済みの対象PIDだけを指定する。image名による一括停止や、Node、Rust、Tauri関連process全体の停止は行わない。停止後は同じbuild commandを再実行し、lockが原因だったかを確認する。
