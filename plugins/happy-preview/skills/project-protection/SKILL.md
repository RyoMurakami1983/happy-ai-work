---
name: project-protection
description: ローカルの新規フォルダ、既存repo、clone、worktreeの事故防止設定を診断し、承認した差分だけ導入する試用スキル。mainへの直接commit・pushと秘密混入の予防、GitHub作成前の開発開始、保護状態の確認に使う。
---

# Project Protection

ローカルフォルダから始める開発を維持する。GitHub repoを先に作らせない。
実利用未検証のプレビューとして扱い、[判断基準](references/protection.md)を読む。

1. 対象root、AGENTS.md、branch、変更状態、既存hook・設定を読み取る。
2. `python3 scripts/project_protection.py plan <root>` で検出と差分計画を出す。
   Git未作成の既存フォルダでは `--init` を加える。フォルダ自体は事前に作る。
3. 対象、追加内容、local hooksPath設定、初期branch main、必要ツールを示す。
   既存承認があればその範囲で進め、実利用先への適用が未承認なら承認を得る。
4. 同じ引数に `--apply <plan_hash>` を付けた `bootstrap` で適用する。
   変更された計画、既存hook、global/worktree設定、管理外変更は上書きせず停止する。
5. `doctor <root>` で再診断する。設定合格と実行検証、remote保護を別々に報告する。
   doctorは設定を書き換えず、scanやnetwork操作を実行しない。

新しいcloneやworktreeごとにplanから始める。追跡ファイルだけではGit設定は伝わらない。
`assets/` を資産の正本とし、GitHubテンプレートは将来これを使う別入口とする。
今回はテンプレートrepoを変更しない。

技術別CIを一律導入しない。TypeScriptは既存の
[設定基準](../../../happy-coding/skills/typescript/references/project-setup.md)、
Rustは既存の[検査候補](../../../happy-coding/skills/rust/references/project-setup.md)を再利用する。
Python等は対象repoの検査入口を読む。既存CIを優先し、このbootstrapでは言語CIを生成しない。

Windowsの配布・利用者実機検証は後続。Python 3、Git、Gitleaks 8.24以降を前提とする。
WindowsではGit for WindowsのshとPATH上のpythonを使い、POSIX環境ではshとpython3を使う。
ツールを勝手にグローバル導入しない。依存なしのPython標準ライブラリを使い、環境への変更を小さくする。
