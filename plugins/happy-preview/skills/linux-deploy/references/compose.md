# Composeでの配置・更新

OSやツールの導入・更新時は公式資料で対象バージョンの対応を確認する。この文書はインストールコマンドのコピーではなく、デプロイ時の判断を扱う。

## 適用前

- 対象ホストのDocker contextを確認する。接続先がリモートならbind mountのパスはDockerホスト側で解決される。手元にあるパスで代用しない。
- OSのリポジトリとユーザーランドのCPUに合う導入方式、イメージの対応platformを確認する。Raspberry Pi OS 64bitではDockerのDebian向け案内を参照し、Ubuntuのリポジトリと混ぜない。
- 実際に適用するComposeファイル、override、project名、環境変数ファイルを揃えて`docker compose config --quiet`で検証する。展開済み設定全体の表示はsecretを漏らし得る。これは構成の検証であり、マウント元や権限の成功証明ではない。
- ホストの公開アドレスとポートを確認する。Tailscaleの導入やUFWの有効化だけでDockerの公開範囲を保証しない。外部からの到達確認は許可されたクライアントから行う。
- アプリの実行ユーザー、読取専用の参照元、書込み先を明示する。存在しないbind元の自動作成を避ける必要がある場合、long syntaxの`bind.create_host_path: false`を使う。既存の空ディレクトリや共有切断はこれだけでは検出できない。

## 適用・起動後

- 確認した設定と識別可能なイメージバージョン／digestを使う。更新時には以前の識別子と必要な設定を残す。GUIを使う場合も、Git等の正本との食い違いを解消してから適用する。
- `up -d`の終了と、コンテナのhealth、アプリのデータ契約を別々に確認する。healthcheckや待機オプションの対応は対象バージョンで確かめる。health失敗が自動でrollbackされるとは扱わない。
- 実行中コンテナのUID/GIDとマウントを確認し、その権限でテスト用の期待データと保存先を検証する。アプリが内部で権限を落とす場合、単なる`exec`の既定ユーザーでは実権限を再現できないため、アプリ経由の確認も使う。
- ログは対象サービス・時間・件数を絞り、返す前にsecretを除く。更新失敗時は旧イメージとのデータ互換性を確認してから戻す。`down -v`や`system prune`を復旧の既定にしない。
- 再起動試験は許可されたテスト環境で行い、ホスト起動時の共有接続とサービスの順序も確認する。

## 公式資料

- [Compose production](https://docs.docker.com/compose/how-tos/production/)
- [Compose services / volumes](https://docs.docker.com/reference/compose-file/services/#volumes)
- [Docker bind mounts](https://docs.docker.com/engine/storage/bind-mounts/)
- [Docker on Debian](https://docs.docker.com/engine/install/debian/)
- [Docker on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [Dockerの権限](https://docs.docker.com/engine/install/linux-postinstall/)
