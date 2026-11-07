# 設計レビューの通常配布と未使用skillの撤回

判断日: 2026-11-03。公開前の変更案。所有者は設計レビューの昇格準備とゲーム制作2skillの削除を指示した。公開・マージは別途確認する。

## ADR 0004とportfolio条件への対応

- 独立目的・trigger: 実装前の技術設計を合意した目的・要件・契約から検証する。設計を作るtechnical-design、実装差分を検査するdeep-reviewとは入力と判断対象が異なる。
- 独自判断・risk: 根拠不足と設計上の破綻を区別し、判定、受容条件、修正の戻り先、対象版と再確認範囲を残す。referencesへの統合だけでは独立レビューの依頼先が不明になる。
- 起動・非起動: [試用前評価](../../evals/records/technical-design-review-preview-001.json)と[説明改善評価](../../evals/records/technical-design-review-explanations-002.json)で公開の模擬依頼と近接依頼の振り分けを確認した。自動発見精度や未知案件への一般化を測った試験ではない。
- 実利用: [比較pilotの設計レビュー012](../reviews/012_TECHNICAL_DESIGN_REVIEW.md)には具体的指摘と修正後確認がある。加えて所有者側の限定監査から、別の実案件でhappy-preview 0.4.1の読込先を明記した複数版レビューに具体的指摘と修正後確認があるとの報告を受けた。私的原資料・全読込tool出力はこの環境で再検証していない。別案件の記録も報告されたが版日時が未固定のため、版を結び付けた根拠には数えない。
- 上記の異なる実作業での観測、独立目的、既存の模擬検証を合わせ、通常配布へ移す変更案とする。件数だけ、模擬評価だけで採用する判断ではない。

## 版差分と限界

レビュー012に固定されたSKILL.mdのSHA-256は`3818ff4bbf898b142c7b7ce2e62157e0f95571ee7763cfe3b224404ec4755e2f`。最新main（`4855d7e`）の本文は`25292019d954abfb2ebf6df1ce8bea8955ea61b47e4bbc98c436138ce38cfd20`。差分は次工程のimplementation-planをimplementの計画段階へ変更した一箇所であり、レビュー基準・手順は変わらない。referenceのhashは両版とも`33367c107b7e0a6e8ce35a3a8f5825519b4a64a277fcbc32f22da1967fb43b01`。

本変更はディレクトリ移動とpreview・実利用検証中の表示除去のみで、レビュー手順とreferenceを維持する。実利用の全件の使用版、現行版の因果効果、一般的な優位性、自動起動精度、利用者理解の定量改善を証明しない。過剰な分割要求、条件付き判定の受容記録、説明の理解度は今後も観察する。既存の評価結果・hash・snapshotは当時の記録として変更しない。

## 配布と移行

technical-design-reviewはコピーせずhappy-previewからhappy-codingへ移動する。happy-codingは0.7.0、happy-previewは0.5.0へ更新する。marketplaceのplugin登録と任意導入policyは維持する。導入済み利用者はhappy-codingを導入・更新し、旧previewのnamespaceを使う明示呼出しを変更する。

未使用のvideo-game-designとunity-beginner-developmentは所有者の依頼で配布ディレクトリと現行の紹介・既定promptを削除する。無効性を実証したという判断ではない。過去の設計・ADR・評価記録は消さず、必要ならGit履歴から復元できる。他のpreview skillの本文は変更しない。

既存インストールが自動的に消えるとは仮定しない。happy-previewも更新し、残った旧skill登録を確認して無効化・削除する。他のpreview skillを利用する場合はplugin全体を無効化しない。
