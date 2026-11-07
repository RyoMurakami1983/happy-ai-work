# Plan 019: 短歌と俳句の参照組込み

## 契約
2026-11-07の所有者承認に基づき、[設計](../design/019_TANKA_SKILL_INTEGRATION.md)と[Issue #73](https://github.com/RyoMurakami1983/happy-ai-work/issues/73)の範囲を実装する。

- 3スキルから共通スキル名を参照し、本文を複製・変更しない。
- 設計概要と詳細を同じ正本に置き、重要riskと未決事項を入口にも残す。
- AC・許可・検証・既存の保存契約を維持する。
- ハーネスと実例評価は後続。draft PRで停止し、マージしない。

## 手順と検証
1. Issueの重複確認・作成、3スキルと設計資料のテンプレート／参照を更新。
2. focused repo validator、参照先と元本文の照合、独立差分レビュー。
3. `uv run --script scripts/validate_quality.py`、plugin version検査、remote Constitution検査、draft PRのCIを確認。

文書・manifestのみの変更でREDを装わない。品質検証と差分照合を用い、行動改善は未評価として残す。戻し先は今回の差分のrevert。

## 結果
- 3スキル・設計テンプレート・HTML指針の変更、Issue #73を作成。
- focused validator、3スキルのquick_validate、独立差分レビューは成功。
- remote Constitution検査は既存の7日超driftを検出。draft PRに留め、同期の確認前にはrelease／mergeしない。
- 品質検証の最終結果とPR CIはPRに記録する。読解・実装能力、実plugin読込、実例評価は未測定。
