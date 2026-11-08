# HOMEの権限エラー導線

Date: 2026-11-08 (UTC)
Status: Issue #75 の実装案。Workでの自動読込は未確認。

## 判断概要

[Issue #75](https://github.com/RyoMurakami1983/happy-ai-work/issues/75)に基づき、権限エラー時は原因を深掘りする前に現在の会話・実行先・失敗操作・権限を確認する。配布元の`home-bootstrap/assets/AGENTS.md`に短い導線を追加し、インストール成功と会話への読込成功を区別する。実行モードの切替は拒否の迂回手段にしない。

## 採用する条件

- 会話の実行モード（Work／Codex等）、実行先、失敗操作・対象、権限・承認状態を簡潔に示す。根拠がない項目は「未確認」とする。
- アプリ名や画面の切替から、元の会話のモード・権限・エラー原因を推測しない。OS権限、sandbox、承認待ち、拒否を分ける。
- Workの実行制限とCodexでの正規の方法が確認できた場合だけ、Codexの新規チャットへ必要な作業情報を引き継ぐ手順を案内する。追加承認は保持する。
- HOME方針の配布先、管理外設定の保持、backup、再適用の冪等性を維持する。実homeの変更や既存会話への反映は、このrepo変更だけでは行われない。

既存の安全・人間の所有権・修復可能性を維持する運用改善とし、Constitutionの意味や優先順位は変更しない。

## 読込の確認範囲

2026-11-08に開いた[公式AGENTS.md資料](https://learn.chatgpt.com/docs/agent-configuration/agents-md)は、Codexが`CODEX_HOME`（未設定なら`~/.codex`）のglobal指示を発見し、空でない`AGENTS.override.md`を`AGENTS.md`より優先することを説明している。[Personalize ChatGPT](https://learn.chatgpt.com/docs/personalize)もglobal `AGENTS.md`についてはCodexを明記している。

これらはWorkで同じファイルが自動読込される証拠ではない。今回のクラウド実行環境には対象のHOMEファイルがなく、利用者のWork会話での自動読込を示す実測は得られていない。「Workでは読まれない」とも断定しない。ファイルの存在、手動read、bootstrapの成功、Codexでの読込確認をWorkでの自動読込確認へ置き換えない。

実利用で確認するときは、対象会話のモード・実行先・実効`CODEX_HOME`とoverrideを特定し、別会話や明示readの内容と混同せず、起動時に有効だった指示の根拠を確認する。確認に新たな設定変更やチャット作成が必要なら、その範囲の承認を得る。証拠が得られなければ未確認のまま報告する。

## 検証

- 自動testは一時`CODEX_HOME`へのdry-run／apply、配布templateとの一致、overrideの非変更を確認する。既存testで管理外のbyte保持、backup、冪等性を確認する。
- 会話のモードが不明な権限エラー、確認済みWork制限、明示拒否、overrideがある導入済みHOMEの4ケースで指示の判断をレビューする。
- repo品質入口とplugin version gateを実行する。静的検証や模擬応答は、Work実環境の読込や障害解消を証明しない。

happy-coreを0.5.2へ更新する。保護hookの修正、利用者PCへの適用、mergeはこの変更の対象外。
