# Windows ARM 実機の再検証

## 対象と現状

Git for Windowsのsh、PATH上のPython 3とGitleaksを使う試験である。ARM64のGit/Gitleaksと
x64エミュレーションのPython/Git Bashが混在する環境は、クラウドのWindows x64 CIと別に記録する。
この手順の作成だけではARM実機の再検証済みとしない。OS権限、セキュリティ設定、global Git設定を変更しない。

以前の実機では実Gitleaksの検出、mainガード、ローカルbare repoへのpushが成功していた。
追加の条件確認では通常ユーザー（Medium Mandatory Level）でGit BashとGitHub通信が成功し、
旧headの不在試験もPATH隔離fixtureで成功した。Gitleaks 8.30.1 ARM64は公式archive checksumと
既存exeの一致が確認された。実symlink作成だけはWinError 1314で未実行のままであり、
修正後headのARM試験結果は別途取得する。

## 最小手順（PowerShell、既存checkout内）

1. `git status --short` で既存変更があれば止める。CIで確認済みの正確なheadへ通常のfetch/checkoutで
   合わせ、`git rev-parse HEAD` を記録する。force、reset、実repoへのbootstrapは使わない。
2. 以下でtool実体・実行環境を記録し、shが正常起動することを先に確認する。

```powershell
Get-Command python, git, sh, gitleaks | Select-Object Name, Source
python -c "import platform,sys; print(sys.version); print(platform.machine())"
git --version
gitleaks version
sh -c 'exit 0'
$LASTEXITCODE
```

`sh` が `NtCreateDirectoryObject`、`0xC0000022` 等で起動できなければ、環境条件でblockedと記録して
止める。製品試験の成功/失敗に読み替えず、通常ユーザーの実行状態を確認する。OS権限設定は変更しない。

3. 修正済みのhappy-ai-work作業ツリーで、管理されたWindows検証環境から次を実行する。旧版のテストを含むcheckoutには適用しない。環境変数はこのPowerShell processだけで設定し、元の値へ戻す。

```powershell
$priorGitleaksTestBinary = $env:GITLEAKS_TEST_BINARY
try {
    $env:GITLEAKS_TEST_BINARY = (Get-Command gitleaks).Source
    python -m unittest discover -s tests -p test_project_protection.py -v
    $testExitCode = $LASTEXITCODE
} finally {
    $env:GITLEAKS_TEST_BINARY = $priorGitleaksTestBinary
}
$testExitCode
```

試験は隔離した一時repoにしかhookを導入しない。試験数と各結果、cleanup errorも含むログを記録する。
実symlink作成が権限不足なら、全体の合格を宣言しない。権限がある既存のWindows環境での実試験と、
当該ARM PCで未実行の条件を分けて報告する。権限設定の変更はこの手順の範囲外である。

## 試験の区別と期待する結果

- 通常の試験は正規名のPythonで専用スクリプトを起動し、成功・検出・故障の結果を模擬する。
  不在は空の検索パスで検査する。時間切れ時は操作が拒否され、子プロセスが終了し、再試行が成功することを確認する。
- 実Gitleaks試験は指定した正規名の実行ファイルを元の場所から使い、無害なダミーデータでcommitとpushを検証する。
- `test_external_config_symlink_is_rejected`: 実symlinkを作成する統合試験。
  link作成後にのみ一時configを切り替える。WinError 1314は元configを保全したまま
  `UNVERIFIED real Windows symlink` として失敗させる。skipにしない。
- `test_config_symlink_detection_mock_without_creation_privilege`: 権限不要の製品判定単体試験。
  これは実Windows symlink試験の代替合格ではない。
- `test_real_symlink_privilege_failure_is_not_reported_as_pass`: 1314を注入し、未確認が失敗として
  表示されconfigが残ることを確認する試験。実symlinkを検証した結果には数えない。

既存Windows CIのhead `489ac148c62bab8ecdc7742d9770384e9492d81f` では、実symlink試験は
mockなしで実行され成功している（quality run `41294340216`、Windows job `124811923512`）。
当時のCIは231試験、実Gitleaks統合だけ任意binary未指定で1件skipだった。
新しいheadでもWindows/Ubuntu CIの実symlink・全体結果と、任意の実Gitleaks統合の実行有無を確認する。
CI成功をARM PC固有の権限・エミュレーション条件の成功へ読み替えない。
