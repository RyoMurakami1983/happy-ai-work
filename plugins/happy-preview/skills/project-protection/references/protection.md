# 判断基準と検証境界

## ローカル

フックは `--no-verify` や設定変更で回避できる事故防止策であり、サーバー保護の代替ではない。
pre-commitは通常のmain commitを拒否する。featureで作業する。
detached HEADでのcommitは未対応で、branchを確認できなければscan前に拒否する。
pre-pushのstdinにある全refの宛先を検査し、`feature:main`、`HEAD:main`、複数ref、main削除を拒否する。
mainからfeatureへのpushは許可する。main以外の削除には履歴scanは不要。
既存hookの自動chain・上書き、global設定の変更はしない。
worktreeでは共通local設定を変更すると他worktreeにも影響する。planの対象と共有範囲を説明する。
管理資産とmanifestは追跡する。設定を共有するworktreeでも各checkoutの資産を確認する。
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
既存 `.githooks` 内の管理対象以外のファイルも、hooksPath変更で有効化しないよう競合とする。

planは共通Gitディレクトリと全worktreeのpathを示す。複数worktreeがすでにありhooksPathが
未導入の場合は、共有設定の初回変更を停止して手動調整へ戻す。導入済みrepoから作る新worktreeは
資産の追跡状態を確認して使う。既存worktreeを一律に変更する機能は持たない。
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
