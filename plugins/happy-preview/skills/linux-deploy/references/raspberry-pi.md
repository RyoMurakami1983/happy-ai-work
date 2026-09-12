# Raspberry Piへの配置で補う確認

Linux共通の配置・データ検証・復旧手順を前提とする。機種名だけでOS、CPUのユーザーランド、利用可能なカーネル機能を決めない。

## 環境を識別する

- `/proc/device-tree/model`、`/etc/os-release`、`uname -m`、`dpkg --print-architecture`等を対象ホストで照合する。Pi OS由来かは、必要なら`/etc/rpi-issue`も確認する。
- Raspberry Pi OS 64bitへDockerを入れる場合は[DockerのDebian向け案内](https://docs.docker.com/engine/install/debian/)を確認する。Pi上のUbuntuには[Ubuntu向け案内](https://docs.docker.com/engine/install/ubuntu/)を使う。機種が同じでもリポジトリやイメージplatformを流用しない。

## メモリ上限を使う場合

Composeに上限を書いても、ホストが対応していなければ警告付きで無視される場合がある。上限を必須条件にするなら、配置前に対応状況を確認する。

```bash
sudo docker info --format 'MemoryLimit={{.MemoryLimit}} CgroupVersion={{.CgroupVersion}}'
cat /sys/fs/cgroup/cgroup.controllers
tr ' ' '\n' < /proc/cmdline | grep '^cgroup'
grep -E '^(CONFIG_CGROUPS|CONFIG_MEMCG)=' "/boot/config-$(uname -r)"
```

- cgroup v2ではルートの`cgroup.controllers`に`memory`があるか確認する。`/proc/cgroups`だけでv2の可否を判定しない。機能が見えることと、Dockerまでの階層で使えることも区別する。
- `CONFIG_MEMCG=y`は組込み済みの証拠であり、起動後の有効性を証明しない。configの保存場所はOS依存で、ファイルが見つからないことを非対応と扱わない。
- 有効化後はDockerの認識に加え、テストコンテナのcgroupの`memory.max`を確認する。64 MiBなら67108864 bytes。ルートcgroupに`memory.max`がないこと自体は異常ではない。値の確認と上限動作の試験は分ける。

### Pi 5で観測した例

2026-09-12、Pi OS由来のDebian 13／カーネル`6.18.39+rpt-rpi-2712`で、Device Treeの`cgroup_disable=memory`が起動引数へ入り、メモリ制御が無効だった。`CONFIG_MEMCG=y`、無効化を示す起動ログ、`memory` controller不在、Dockerの`MemoryLimit=false`が一致した。[公式Device Treeソース](https://github.com/raspberrypi/linux/blob/rpi-6.18.y/arch/arm64/boot/dts/broadcom/bcm2712-rpi.dtsi)にも同じ既定値がある。

これはPi 5全機種・全OSの保証ではない。無効化引数が設定ファイルに見つからなくても、実際の`/proc/cmdline`とDevice Treeを確認する。生の起動引数全体には機器識別情報が含まれ得るため、公開記録は関連項目だけにする。

## 起動設定を変更する場合

実際に読み込まれるboot領域、設定ファイル、includeを確認してから変更案を作る。`/boot/cmdline.txt`が移動先を示す案内だけのこともある。推測した場所への新規ファイル作成やDTBの直接編集を既定の修復策にしない。

変更前にバックアップ、停止影響、復旧経路を具体化する。配置の依頼だけを再起動の許可とは扱わない。再起動後は起動引数・controller・Dockerの認識・テストコンテナの実効値を照合する。原因の特定を修復完了と報告しない。

## 根拠

- [Dockerの資源制限](https://docs.docker.com/engine/containers/resource_constraints/)
- [Linux cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)
- [Raspberry Piカーネルの起動引数処理](https://github.com/raspberrypi/linux/blob/rpi-6.18.y/kernel/cgroup/cgroup.c)
