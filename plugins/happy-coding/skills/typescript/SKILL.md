---
name: typescript
description: TypeScript／TSXリポジトリのpackage manager、tsconfig、module方式、lint、test、build契約を読み、型安全と実行時境界を保って実装またはセットアップする。Node.jsやfrontendのTypeScript変更で使う。
---

# TypeScript

lockfileとpackage scriptsを実行契約として扱い、npm、pnpm、Yarn、Bunや特定test runnerを既存repoへ無断で持ち込まない。

## ワークフロー

1. lockfile、`package.json`の`packageManager`／scripts、`tsconfig*.json`、module type、lint／format／test／build設定を確認する。
2. 既存repoでは宣言済みpackage managerとscriptを使う。新規構築を依頼された場合だけ[project-setup.md](references/project-setup.md)を読む。
3. `strict`設定、公開型、外部入力のruntime validation、ESM／CJS境界を確認する。詳細は[coding-practices.md](references/coding-practices.md)を読む。
4. focused test、type check、lint、buildをrepoの依存順序で実行する。fresh install確認ではlockfile固定のcommandを使う。
5. browser、Node.js、edge runtimeなど実行環境の差を明示し、片方だけで使えるAPIを共有層へ漏らさない。

repoへ永続的なTypeScript規約を追加する依頼では、[AGENTS.fragment.md](assets/AGENTS.fragment.md)を対象repoに合わせて最寄りの`AGENTS.md`へ統合する。

## 境界

- Tauri固有のRust連携、capability、bundle、sidecarは`tauri`へ渡す。
- `any`禁止を目的化せず、型不明の境界では`unknown`から検証して絞り込む。
- lint／format設定の全面刷新を、機能変更へ混ぜない。
