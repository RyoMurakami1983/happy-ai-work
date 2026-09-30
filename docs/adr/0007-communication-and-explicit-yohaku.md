# コミュニケーション評価とYohakuの明示利用

Status: Accepted for implementation（2026-09-30、所有者が1→2→3の実装・検証とdraft PRを承認。mergeは保留）

Refs #45 / #44。新しい共通評価軸・改善優先度は[基準移行判断](../../plugins/happy-core/skills/skill-eval/references/evaluation-criteria-v2.md)に記録する。Constitution 1.0.0の原則と順位を変更しない。

ADR 0005の決定4（home-bootstrapによるYohakuの開始時生成・選択保持）を置き換える。生成・保持経路とCLIオプションを除去し、旧管理領域は通常更新で基本方針へ移行する。管理外の個人設定は保持し、実homeは明示承認範囲の差分とbackup付きで更新する。旧scriptへのdowngradeでは復活する可能性があるため、更新に使うscriptとdiffを確認する。過去の設計・評価は保存し、当時の結論を現在へ読み替えない。

Yohaku本体は明示利用・比較用に残す。この除去はYohakuの無効性の結論ではない。全スキルへの本文複製はせず、implement/debug-and-fixから長時間検証の通知と終了報告を共通referenceへ接続し、dotnetとimplementation-planの受渡しも整える。

利益は、評価軸と代表スキルの責務を直接検証でき、homeの開始時読込へ依存しないこと。不利益は既存利用者の自動適用が更新で消えることと、旧版へ戻すと再生成し得ること。配布物・インストール更新・実home・新しい会話の観測は別々に報告する。

## PR #46の所有者feedbackを反映

2026-09-30、所有者は[PRコメント](https://github.com/RyoMurakami1983/happy-ai-work/pull/46#issuecomment-5916874103)で、READMEとhome-bootstrapには現在の結果だけを残し、Yohakuへの言及・移行説明を削除するよう依頼した。READMEの紹介・利用説明・移行段落とhome-bootstrapの説明を削除し、scriptの旧状態専用guardも取り除く。管理マーカー検証、既定テンプレートへの更新、管理外保護、dry-run、backupは維持する。ユーザーが明示指定するcustom templateは通常の管理マーカー検証で扱う。

判断履歴はこのADRと既存の凍結評価証拠に保持し、現在の利用手順へ再展開しない。Yohaku本体の削除は今回の依頼に含まれず、明示利用・比較用のskillとして残す。既定更新で旧開始時設定が復活しない回帰testも保持する。
