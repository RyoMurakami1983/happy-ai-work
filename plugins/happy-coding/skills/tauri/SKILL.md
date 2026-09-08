---
name: tauri
description: Tauriデスクトップアプリのfrontend／Rust境界、capability、Windows toolchain、bundle、sidecarを実装・診断・配布検証する。Tauri導入、Windows build、外部binary、installer、packaged-only failureで使う。
---

# Tauri

frontend、Rust command、capability、external binary、bundleを別契約として扱い、dev起動成功を配布成功とみなさない。

## ワークフロー

1. Tauri major、frontend package manager、Rust toolchain、target、`tauri.conf.*`、capabilities、bundle targetを確認する。
2. 初回導入やWindows toolchain問題では[windows-setup.md](references/windows-setup.md)を読む。
3. Windowsの日常開発、生成済みEXEの直接確認、または再ビルド時のアクセス拒否を扱う場合は[windows-development-loop.md](references/windows-development-loop.md)を読む。
4. frontendからRust command／pluginへ渡す入力、権限、error、serialization境界を固定する。
5. sidecarまたはinstallerを扱う場合は[sidecars-and-distribution.md](references/sidecars-and-distribution.md)を読み、raw実行、packaged smoke、bundle、clean環境を段階化する。
6. dev、frontend build、Rust build、packaged applicationを分けて検証し、どの段階まで成功したか報告する。

## 境界

- TypeScriptだけの変更は`typescript`、一般Rust変更は`rust`を使う。
- capabilityを広げて症状を消さず、必要なcommand／sidecarだけを許可する。
- proxy、CA、revocation回避は環境固有の例外とし、repositoryへ秘密値や個人pathを固定しない。
- MSI／installer生成成功だけでinstall後動作を保証しない。
