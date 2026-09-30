# Codex Hooks初期設定ガイド

## 初期方針

Hooksが未設定でも異常ではない。home-bootstrapではグローバルhookを自動投入しない。まず次を読み取り専用でinventoryする。

- `~/.codex/hooks.json`
- `~/.codex/config.toml` 内のinline hooksと`notify`
- 対象repoの `.codex/hooks.json` / `.codex/config.toml`
- plugin由来のhook

既存定義は上書きしない。同じlayerでJSONとinline TOMLを混在させない。

## 推奨する導入順

1. **通知（任意）**: user-levelの`notify`を優先する。ローカル通知のみとし、外部Webhook、prompt本文、tool input、secretの送信は既定で無効にする。
2. **検証（repo単位・任意）**: fast focused checkがあるrepoだけを対象にする。`Stop`で失敗を通知または最大1回の継続要求に限定し、formatter、commit、pushは実行しない。
3. **最小ログ（高度・任意）**: `async: true`でイベント名、時刻、終了状態など最小metadataだけを保存する。prompt、transcript、command、path、secretは既定で収集しない。rotationと保存期間を定める。
4. **危険操作guard（高度・任意）**: synchronous `PreToolUse`のdeny-onlyとして設計する。`PermissionRequest`で自動allowしない。sandbox、approval、backup、branch protectionの代替にはしない。

`happy_ai_life` のCopilot用guardからは、stable IDで管理対象だけを更新すること、他entryの保持、dry-run、backup、policyとscriptの分離、短いtimeout、PowerShell/Bash parityを参考にする。ただしCopilotのevent名や入出力schemaはCodexへコピーしない。

## 適用契約

候補を設定するときは、次を満たす。

- command handlerだけを使用する。Windowsでは`commandWindows`も定義する。
- timeoutを明示し、重い処理をhookに載せない。
- hookの正確な定義と実行scriptをdiffで提示する。
- ユーザーが明示承認した項目だけをbackup付きで適用する。
- 適用後にCodexのSettings → Hooksまたは`/hooks`で定義を確認し、Trustが必要ならユーザーへ案内する。
- 新しいtaskでcanary testを行い、期待したevent、timeout、失敗時挙動を確認する。

Hooksは完全なsecurity enforcement boundaryではない。`PostToolUse`は既に起きた副作用を取り消せず、async hookはblock、approval、rewriteに使えない。

## Sources

- [OpenAI Docs: Hooks](https://developers.openai.com/codex/hooks)
- [OpenAI Docs: Configuration Reference](https://developers.openai.com/codex/config-reference)
- [agent-notify](https://github.com/paultendo/agent-notify)
- [Codex Command Guard](https://github.com/KStarob/codex-command-guard)
