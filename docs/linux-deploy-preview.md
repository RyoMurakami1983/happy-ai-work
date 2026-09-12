# linux-deployの初版設計と検証範囲

Date: 2026-09-11 (Asia/Tokyo, UTC+09:00)
Status: Preview / 実デプロイでの効果は未検証
Source: [Issue #23](https://github.com/RyoMurakami1983/happy-ai-work/issues/23)

## 採用した目的

利用者が指定した「環境・パスを実測して適用する」「正しいデータを正しい権限で扱えるか確認する」「失敗時に原因・残存状態・再実行方法を残す」をprimary purposeとする。

[linux-deploy](../plugins/happy-preview/skills/linux-deploy/SKILL.md)は方式を強制せず、初期の具体的な経路としてComposeを参照文書で扱う。既存systemd／shellも尊重する。共有のパス・権限・FSROOTの判断は条件付きreferenceに分離した。OS導入手順をコピーした汎用インストーラーや、新しいデプロイエンジンは作らない。対象アプリの契約に応じたチェックを作成・実行するためのskillである。

通常配布に必要な実利用の証拠はまだないため、ADR 0004に従いhappy-previewに置く。Issueの実環境Acceptance Criteriaを、このskillファイルの作成だけで完了扱いにしない。

## 初版の確認

公式skill-creatorに基づき、実装履歴を渡さない独立subagentへスキルと次の架空依頼を渡した。実機操作・変更は許可せず、提示事実から次の判断と報告を作る模擬試験とした。

| 模擬依頼 | 観測された応答 |
| --- | --- |
| UbuntuでCompose更新後health 200。共有のつもりのパスは存在するがfindmntは祖先のext4を返し、既知ファイルが見えない。「完了でよいか」 | 完了とせず、共有接続を断定せずに期待する共有と照合。Dockerホスト側のパスと実UID/GIDでの確認へ進んだ |
| Piのsystemd用install.shがSSH切断。新バイナリ配置済み、移行の終了記録なし、FSROOTは/team。「同じsudoを再実行して」 | 移行状態・残存プロセス・再実行性を先に確認。同時／二重移行を避け、FSROOT単独で異常判定しなかった |

これは2ケースの模擬応答の確認であり、実デプロイ成功、スキルなしとの優劣、手戻り削減を証明しない。通常選択での発火・非発火も未評価。

形式確認は公式quick_validateとrepo標準validate_qualityを使用する。参照文書中のパス確認コマンドについては読取実行での確認を行ったが、共有マウントや権限拒否の実証とは区別する。実環境の接続先・生ログはこの公開用文書に含めない。

## 次の試用で確認すること

- Raspberry Pi OS arm64とUbuntu Server 26.04で、テストアプリの初回導入・同一設定の再実行を実施する。
- 限定した環境で共有未接続・権限不足・更新途中の失敗を試す。原因、残存状態、再実行条件が分かり、既存データが守られるかを確認する。
- テスト用バックアップを別の保存先へ復元し、アプリ権限で利用できるか確認する。
- 試行前に同じ観察条件を置き、確認漏れ、利用者の修正再実行回数、不要な質問・承認待ちを記録する。比較を行う場合はスキルなしの結果も別記録に残す。

効果が出なければ、アプリ専用の手順へ戻すことやスキルの縮小も選ぶ。全ディストリビューション対応やGUI必須化で範囲を広げない。

## 2026-09-12: 実行依頼前の確認を補強

根拠は[Issue #23の追加フィードバック](https://github.com/RyoMurakami1983/happy-ai-work/issues/23#issuecomment-5629147337)。初版の安全な停止・再実行に加え、利用者へ適用を頼む前に環境と手順を照合し、判定条件自体を検証する。エージェントが確認できる不備を利用者のsudo実行で発見する往復を減らすことを狙う。

既存の権限境界は維持する。利用者固有の操作が必要な場合は未確認事項をまとめ、必要条件が未確認なら確認だけを依頼する。再実行前には原因・修正・検証結果・残存状態を対応づける。新しいインストーラー方式や一律の承認待ちは追加しない。

今回の確認条件は、環境と手順の不一致を適用前に扱うこと、正常例を誤拒否する判定を点検すること、未知の前提を残した適用依頼を避けること、既存の実行許可を重ねて要求しないこと。形式検証と差分の確認は実施結果を別記し、実機での手戻り削減の証明とは扱わない。

形式検証: 公式quick_validate成功、標準validate_quality成功（58 unit tests、repo/eval validator、Ruff、ty、git diff check）。独立behavioral評価は今回未実施。

利用者指定のPiを読取確認した結果、Raspberry Pi 5、Raspberry Pi OS由来のDebian 13（trixie）、aarch64であることを確認した。Docker未導入、sudoは対話認証が必要だった。公式配布元へのHTTPS疎通は成功した。Compose試験は前提不足で未実施であり、失敗注入や再実行の検証成功とは扱わない。

Issue全体の残件はDocker導入後のPiでの隔離試験と、別途Ubuntu Server 26.04での実環境試験。ホスト準備ではDocker公式APT source・署名鍵の追加、Docker Engine／CLI・containerd・Buildx／Compose pluginの導入とdaemon起動が必要になる。既存設定の存在時は上書きせず停止する導入案を準備した。ユーザーのdocker group追加は含めない。この変更のみではIssueを完了としない。

## 2026-09-12: PiでのCompose実機試験

上記の前提確認後、利用者がDocker導入を承認し、手元でsudo実行して導入成功を報告した。その後、SSH経由の`sudo -n docker`でDocker Engine 29.8.0／Compose 5.5.1の稼働を確認し、以下の隔離試験を実施した。Dockerなしとの比較実験やskillの独立behavioral評価ではない。

再現用: [compose-smoke.sh](../tests/manual/linux-deploy/compose-smoke.sh)。通常ユーザーで`bash tests/manual/linux-deploy/compose-smoke.sh`を実行する。Docker／Composeと非対話の`sudo docker`実行権限が前提。スクリプトは一意な`/tmp`配下、Compose project、ローカルイメージタグを作り、外部公開ポートなし・コンテナネットワークなしでBusyBoxの小さなHTTPアプリを実行する。利用者データや既存サービスは対象にしない。

実行前にスクリプト内のassertionを固定し、対象Piで`bash -n`を通してから1回実行、終了値0を確認した。

| 試験 | 観測結果 |
| --- | --- |
| 初回配置・同一設定で再実行 | healthy。再実行前後でcontainer IDと設定ハッシュが一致 |
| アプリ権限のデータ契約 | 非rootで既知ファイルを読み、専用保存先へ書込み・再読。兄弟フォルダへの既知パスは見えず、読取専用への書込みは終了値1で拒否 |
| ローカルbind元の欠落 | 起動が終了値1で失敗。存在しないディレクトリの自動作成なし。テスト元を戻して再実行するとhealthy |
| 参照元の権限不足 | テストファイルの読取が終了値1で拒否。権限を戻すと読取成功 |
| 更新途中の失敗と復旧 | 壊れたv2イメージへ再作成後、アプリは終了値42で停止、Composeは終了値1。段階・理由・終了値をログで確認。v1イメージに戻してhealthy、保存データのハッシュ不変 |
| 別保存先への復元 | テスト用tarを別フォルダへ復元。内容一致とアプリUID/GIDによる読取を確認。元の保存データは不変 |
| 後片付け | この試験のコンテナとv1／v2タグを削除、同projectの残存コンテナなし。テストデータ・ログ・バックアップ、BusyBoxベースイメージとbuild cacheは残す |

ベースイメージは`busybox:1.37`をpull後、`busybox@sha256:9db7b59979c38555a39def84a31fb98b5296952f9e3afd4f6f11f05b07adfab0`へ固定して2種類のテストイメージをbuildした。スクリプト自身のSHA256は`ec01a414bfc73a84269dc17c3cecbfa4a431cb918c60f9c42d44960a55af5891`。

途中で予期しない失敗が起きた場合、スクリプトは段階・終了値・作業先を表示して停止し、診断用に状態を残す。表示された作業先の`results.log`と`compose.yaml`、project名を使って`docker compose ps -a`／`logs`を確認し、原因と残存状態を確認してから当該projectだけを片付ける。このスクリプトを再実行すると新規の試験領域を作るため、前回の残存物を自動で修復するものではない。

観測した制約: kernel／cgroupによるメモリ上限非対応の警告が出て、設定した64 MiB上限は無視された。今回のデータ／復旧試験の合格条件に資源上限の有効性は含めておらず、メモリ隔離成功とは報告しない。Compose参照文書へ、設定無視の警告と実効性を確認する手順を追加した。ホストのboot設定は変更していない。

残件: SMB／NFS共有未接続（mount先だけ残る状態を含む）、共有の再接続・起動順、Ubuntu Server 26.04、実アプリの更新・データ移行、実利用での手戻り削減。今回のbind元欠落試験は共有切断の代用にしない。Issue #23は継続扱いとする。

## 2026-09-12: メモリ上限警告の原因調査

読取調査で直接原因を特定した。稼働カーネルの設定は`CONFIG_MEMCG=y`だが、実際の起動引数に`cgroup_disable=memory`があり、有効化指定はなかった。起動ログの`Disabling memory control group subsystem`、cgroup v2のルート`cgroup.controllers`に`memory`がないこと、Dockerの`MemoryLimit=false`／`SwapLimit=false`が一致する。cgroup自体はマウントされており、機能の組込み不足ではなく起動時の無効化である。

導入済みカーネルのPi 5用DTBを`fdtget`で読み取ると、`/chosen/bootargs`に同じ無効化指定がある。稼働中Device Treeでも確認した。[Raspberry Pi公式ソース](https://github.com/raspberrypi/linux/blob/rpi-6.18.y/arch/arm64/boot/dts/broadcom/bcm2712-rpi.dtsi)の既定値とも一致する。端末固有の設定ミスやDockerのインストール失敗とは断定しない。

再利用する知見は、設定の受理・ホスト機能・実効値を区別すること。cgroup v2は`/proc/cgroups`だけで判定せず、`cgroup.controllers`と対象コンテナのcgroupを確認する。根拠は[Linux cgroup v2文書](https://docs.kernel.org/admin-guide/cgroup-v2.html)と[Dockerの資源制限文書](https://docs.docker.com/engine/containers/resource_constraints/)。`memory.max`は非root cgroupのファイルなので、ルートでの欠落自体を故障の証拠にしない。

調査のみを実施し、起動設定・DTBの変更や再起動はしていない。修復完了には、実際に読み込まれる起動設定の確認、有効化後のcontroller／Docker対応確認、対象コンテナの上限値と必要な限定試験が残る。生の起動引数や機器識別子は保存しない。
