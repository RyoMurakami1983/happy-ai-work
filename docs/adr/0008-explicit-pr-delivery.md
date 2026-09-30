# 明示マージ依頼から安全な整理までをskillで閉じる

Status: Accepted for implementation（2026-09-30、利用者が公式資料に基づく方式選択と実装・検証・draft PRを依頼。今回の新PRのマージは未承認）

## 決定と根拠

[公式Git設定](https://learn.chatgpt.com/docs/developer-settings#git)のpromptはcommit messageとPR description生成用と説明され、明示マージ依頼からlocal/remote branch・worktree整理までのworkflow指定と同等とは確認できない。[公式skill資料](https://learn.chatgpt.com/docs/build-skills)はdescriptionによる自然文の暗黙選択とinstructions-firstを説明する。したがって設定・Hookを変更せず、単一目的の`pr-delivery`を追加する。自動選択は期待できるが100%の保証にはしない。

実在する`deep-review`は差分評価、`ci-debug`はCI失敗の切り分け、home-bootstrapのGitガイドはPR準備完了までを扱い、merge/cleanupの完了責務を持たない。既存skillを汎用routerへ拡張せず、明示依頼によるPRの完了だけを独立目的にする。

利用者の「マージして」は当該PRのbase同期と安全に証明できた対象の整理までを通常の終了条件とする。これは作業手順の定義であり、tool/platformの権限、別PRの承認、未保存変更の削除許可へ読み替えない。取得済みの同じ範囲の許可は再質問せず、対象不明や新しい権限・安全判断だけを保留する。限定指示があれば優先する。

repo固有merge方式、正確な最新head/checks、MERGED状態とbase履歴、安全なbase同期、削除対象の限定、未保存/未push/未統合/別worktree利用の保護を完了契約とする。安全を証明できない対象や通常削除が拒否されたbranchは理由付きで残す。force/resetや認証・課金・security設定の変更はしない。

remote削除は確認後の別pushを守るため、確認済みSHAを条件とするforce系option不要の比較条件付きAPIに限定する。その保証がない実環境ではremote branchを保持して理由を報告する。合成APIの成功を実GitHub toolの対応保証へ読み替えない。

## 配布と確認範囲

[ADR 0004](0004-preview-plugin-distribution.md)に従い`happy-preview`で任意試用する。通常/対象外/保護caseを隔離されたlocal bare remoteと合成PRで検証し、実PR・既存branchを試験目的でmerge/deleteしない。自動発火の完全性、実GitHubでのeffect、squash/rebaseを含む全repo運用は未測定として残す。実利用確認後の通常配布採用は別判断とする。
