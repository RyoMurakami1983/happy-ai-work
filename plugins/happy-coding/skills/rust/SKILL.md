---
name: rust
description: Rust／Cargoリポジトリのworkspace、toolchain、feature、format、Clippy、test契約を読み、所有権・エラー・unsafe境界を保って実装またはセットアップする。RustコードやCargo設定の変更で使う。
---

# Rust

既存edition、MSRV、workspace、feature、target、lint方針を先に確定し、一般的な最新設定で上書きしない。

## ワークフロー

1. `Cargo.toml`、`Cargo.lock`、workspace構成、`rust-toolchain*`、`.cargo/config.toml`、CIからbuild contractを読む。
2. library／binary、公開API、feature、target、MSRVへの影響を整理する。新規構築時は[project-setup.md](references/project-setup.md)を読む。
3. 所有権、error type、panic、unsafe、公開範囲を変更内容に合わせて確認する。詳細は[coding-practices.md](references/coding-practices.md)を読む。
4. focused testの後、repoの契約に従ってformat、check、Clippy、test、必要なtarget buildを実行する。
5. platform依存コード、FFI、async runtime、feature combinationは、実際に影響する組合せを明示して検証する。

repoへ永続的なRust規約を追加する依頼では、[AGENTS.fragment.md](assets/AGENTS.fragment.md)を対象repoに合わせて最寄りの`AGENTS.md`へ統合する。

## 境界

- Tauri固有のfrontend連携、capability、bundle、sidecarは`tauri`へ渡す。
- 不要なcloneを機械的に消すのではなく、所有権と可読性、実測コストで判断する。
- `unsafe`を必要悪として隠さず、安全性の前提と検証範囲を局所化する。
