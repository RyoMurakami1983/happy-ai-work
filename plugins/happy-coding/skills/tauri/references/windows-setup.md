# Windows setup

既存repoのTauri versionと公式prerequisiteを正本にし、次の依存鎖を個別に確認する。

1. frontend runtimeとpackage manager
2. Rust toolchainとtarget
3. MSVC C++ build tools／Windows SDK
4. WebView runtime
5. Tauri CLI
6. bundleに必要なinstaller tool

`link.exe`、Rust target、frontend出力先、`frontendDist`、`devUrl`、`beforeBuildCommand`を分けて診断する。PATH更新を伴う導入では、新しいshellまたは同一processで反映を確認する。

企業networkではgit、Cargo、Node、installer downloadが同じproxy／CA設定を自動共有するとは限らない。組織の正本からbuild processへ必要最小限を渡し、TLS検証無効化を恒久設定にしない。
