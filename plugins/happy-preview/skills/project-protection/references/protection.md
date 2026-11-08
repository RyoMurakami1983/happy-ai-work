# 判断基準と検証境界

## ローカル

フックは `--no-verify` や設定変更で回避できる事故防止策であり、サーバー保護の代替ではない。
pre-commitは通常のmain commitを拒否する。featureで作業する。
detached HEADでのcommitは未対応で、branchを確認できなければscan前に拒否する。
pre-pushのstdinにある全refの宛先を検査し、`feature:main`、`HEAD:main`、複数ref、main削除を拒否する。
mainからfeatureへのpushは許可する。main以外の削除には履歴scanは不要。
既存hookの自動chain・上書き、global設定の変更はしない。
worktreeでは共通local設定を変更すると他worktreeにも影響する。planの対象と共有範囲を説明する。
実行資産とmanifestは共通Git管理ディレクトリの `project-protection/<内容hash>/` に置き、追跡しない。
`core.hooksPath` はその `hooks/` の絶対pathを指す。hookは自身のpathからguardを参照し、
Pythonの `-I` でcheckoutやPYTHONPATHからのimportを除外する。`.githooks` や
`.project-protection` がbranchで置換・削除されたり、post-checkoutを追加されても実行しない。
通常の `.git/` または全worktreeの外のGit管理領域を使い、追跡可能なディレクトリやsymlink／junctionを拒否する。
内容hashは版の識別用であり、doctorはmanifestだけでなく信頼済み配布資産との実byte一致と余分なファイルも確認する。
branchによる書換えから分離する設計であり、所有者や同じ権限のprocessに対するOSの改変禁止・sandboxではない。
絶対pathのためrepo移動時はdoctorが不合格になる。新しいpathへの設定変更は手動で差分を確認し、再導入する。
部分導入はdoctorで不合格とし、planが安全に追加できる欠落のみ補完する。
管理外変更はバックアップし、所有者が比較・調整してから新しい計画を作る。
既存内容を削除して再導入する操作を暗黙に行わない。

## 秘密検査

Gitleaksは候補として採用する。既存scannerがある場合は二重導入せず統合方針を決める。
実秘密を入力例・ログ・テストへ書かない。フックは出力を抑制しredactも指定する。
失敗・ツール不在は成功扱いしない。検出と実行エラーは同じ拒否結果になる。
検査成功は選択した設定・ルール・対象範囲で検出されなかったことを示すだけで、すべての秘密情報の不在を保証しない。

- commit前: `gitleaks git --pre-commit --staged` でindexを検査する。
- push前: 既存refは `remote_oid..local_oid`、新規refはlocal_oidから到達する全履歴を検査する。
  remote OIDが手元になければscan失敗として停止し、勝手にfetchしない。
  全refのmain拒否判定を先に行い、scanは送信refごとに行う。
- CI: full history checkout (`fetch-depth: 0`) と `gitleaks git --redact --no-banner` を候補とする。
  浅いcheckout、PR差分だけ、作業ツリーだけを全履歴検証と呼ばない。
  runnerとGitleaksを固定し、既存CIとrepo方針を確認して別途承認した差分として導入する。
  今回はCIファイルを自動生成しない。

## Remote

doctorのremote URL検出は保護検証ではない。remoteがなければ `remote_not_created`、
あっても `unverified` と出す。local_configurationのpassは資産・実行権限・設定一致だけを意味する。
secret_scanとlocal_validationは実行していないので `not_run` と出す。
ツール存在だけではversion、動作、秘密検出能力の合格としない。

読み取り権限のあるGitHub APIが使える段階では、認証要求や変更をせず、対象owner/repo、
default branch、mainのbranch protectionと適用rulesetsを読み取る。要求されるPR、required checks、
force push/deletion禁止、bypass対象、管理者への適用を別項目で評価する。
404を保護なしと断定しない。権限不足、プラン制約、timeout、認証なし、非GitHub remoteは
それぞれ理由を付けて未確認とする。この最小実装にはAPI呼び出しを含めない。
実repoへの導入、remote設定変更、push、公開はそれぞれユーザーの承認範囲で扱う。

## 試用条件

隔離repoで拒否と許可、送信先判定、ツール不在、ダミー検出、再実行、競合、worktree、
doctorの非破壊を確認する。実Gitleaks・GitHub API・Windows・利用者PCでの実機結果は別途記録する。
テンプレート連携、CI生成、remote読取の実装は後続課題とする。

新規Git初期化では計画に示す `git init --template= -b main` を使い、利用者のinitテンプレートから
未確認のhookをコピーしない。この選択も承認した計画の一部とする。
既存のworktree内 `.githooks` は新規導入で有効化も変更もしない。Git既定の `hooks/`、
既存hooksPath、trusted bundle内の管理対象以外のファイルは競合とする。
Git configのinclude／includeIfは、今は無効でもbranch変更後にhook設定を有効化し得るので手動調整へ戻す。
無関係なincludeも自動変更せず、現行設定を保つ。

planは共通Gitディレクトリと全worktreeのpathを示す。複数worktreeがすでにありhooksPathが
未導入の場合は、共有設定の初回変更を停止して手動調整へ戻す。導入済みrepoから作る新worktreeは
同じbundleを使う。各worktreeのdoctorでworktree固有のoverrideも確認し、1か所のpassを他worktreeの合格と呼ばない。
既存worktreeを一律に変更する機能は持たない。
remoteの存在はoriginに限定せず全remote名で確認し、URLは出力しない。

設定ファイルまたは祖先ディレクトリのsymlinkは競合とする。設定有効化ではGitの
`config.lock` を排他的に取得し、資産書込後のGit状態と資産を再検査する。別の設定変更や
既存ロックがあれば設定を保存したまま停止する。作成済み資産は削除して巻き戻さず、部分導入と
競合を再診断する。Gitのロックを無視する任意プロセスによるファイル差替えまで防ぐセキュリティ境界ではない。
CLIの終了コード0は診断処理の完了を示す。保護合格は各JSON項目で判断し、未実行を合格へ読み替えない。

## 秘密検査の実行時間

Gitleaksは1回の呼出しにつき既定60秒で停止する。timeoutではscannerと子Gitプロセスの
POSIX process group、またはWindowsのtaskkill /T /Fで通常の子processを含めて終了し、
秘密を含み得る出力を抑制したままcommit/pushを拒否する。
未完了の検査を成功や秘密なしとして扱わない。複数refのpushはrefごとの検査にこの上限を適用する。

遅いディスクや長い履歴では正常な検査も60秒を超えるため、同じcommit/pushを再試行するか、
そのコマンドだけ `PROJECT_PROTECTION_SCAN_TIMEOUT=300 git push ...` のように延長する。
値は整数1〜600秒で、未指定は60秒、範囲外・不正値は拒否する。無期限値は設けない。
グローバル設定や検査範囲を変更せず、検査を省略して進めない。最大600秒でも未完了なら、
別途同じ対象履歴を検査できる環境で原因を調べ、未確認として扱う。Windowsではtaskkillにも10秒の上限を設け、scannerが残っていればkillで停止する。taskkill自体が失敗した場合、このfallbackが停止するのは
scanner本体で、子process全体の終了は未確認とする。
終了処理の失敗も検査成功へ読み替えない。WindowsはGit for Windows、PATH上のPython 3と
Gitleaks実行ファイルを使う範囲を対象とし、GUI配布、特殊な子process、利用者PCは後続検証とする。

Windowsの一時path（短縮名を含む）とGitのroot表記は、API入口で両方をresolveして比較する。
repo配下の別フォルダをrootと誤認しない境界は維持する。Windows/Ubuntu CIでは同じ受入試験を実行し、
実Gitleaks統合試験は明示したテスト用binaryがある場合に実行する。

## 旧版からの移行

旧版のlocal `core.hooksPath=.githooks` は安全な実行領域ではない。未信頼branchをcheckoutする前に、
信頼済み配布元のinstallerから `plan <root> --migrate-legacy` を実行する。
対象・共通Git管理領域・新hooksPath・旧資産を削除しないことを確認し、承認後に
`bootstrap <root> --migrate-legacy --apply <plan_hash>` を実行する。

- 旧版はPR #67の既知guard・2つのhook・manifestと完全一致する場合だけ移行できる。
  checkout内のmanifestを書き換えても承認根拠にはならない。追加hook、欠落、変更、symlink／junctionは停止する。
- 共有worktreeが複数、global/worktree override、既存Git hookがある場合は一括変更しない。
- 新bundleを先に検証し、config.lockを使って設定を最後に変更する。途中失敗は旧設定と作成済み資産を残す。
  失敗中は旧hookの危険も残るため、通常commit/push/checkoutへ戻らず診断する。
- 旧追跡ファイルは削除・実行・chainしない。移行後のdoctorと実行確認が済んでから、所有者が別の差分で整理する。
- 既に旧資産が改変されているときは、そのhookを有効にしたままbranch切替で復旧しない。
  設定・ファイルを保存し、所有者と旧hookの無効化および既存機能の統合方針を確認して手動調整する。

installerと配布assets、Git/Python/Gitleaksとそれらの検索環境は信頼済みであることを前提とする。
PATHにcheckoutや空要素を含めない。guardはGit/Gitleaks/taskkillを絶対PATHのcheckout外ディレクトリから
絶対pathへ解決し、Windowsのcurrent directoryにある同名exeを選ばない。scannerにも同じPATHと
`NoDefaultCurrentDirectoryInExePath=1` を渡し、子Gitの暗黙current-directory検索を避ける。
任意のローカル設定・実行ファイル改変を防ぐ機能ではない。
Gitleaksのrepo内設定・ignore規則は引き続き対象repoの方針に従うため、悪意あるscanner設定による
検査弱化を防ぐ保証はない。server側の検査・保護と併用する。
