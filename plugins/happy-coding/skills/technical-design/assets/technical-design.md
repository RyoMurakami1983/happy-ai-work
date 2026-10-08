# Technical Design NNN: 案件名

設計版・合意状態・形式を選んだ理由を記載する。これは記入用テンプレートであり、空欄を未知の事実で埋めない。短い変更は見出しを統合・省略する。

## Goal / Success Criteria / Out of Scope
目的、観測可能な成功条件、対象外。

## Normative Inputs
合意済み要求・AC・制約・既存規約のpath、節、版。提案と推定を分ける。

## Purpose / Requirement Trace
要求 → モデルの責任（必要時） → module/interface → 検証境界。

## Current Structure and Observed Harms
既存コードの具体的な入口・処理と証拠。新規の場合は調査済み参照と未確認範囲。

## Change Scenarios / Expected Locality
根拠のある変更理由と変更する箇所。材料がない場合はその旨を記載。

## Structure Decisions
責務、所有、依存方向、採否と理由。図の問い・解説とこの節を対応させる。

## Public Interfaces
公開操作の入力と結果、エラー、観測できる境界。

## Domain Invariants / Interface Contracts
事前条件、成功時の事後条件、失敗時の状態・副作用と保証する責任。

## State / Data Flow
状態と遷移条件、I/Oの順序、部分失敗。図だけで保証を追加しない。

## Security Boundaries
外部入力、認証、秘密情報、file/networkの境界。

## Compatibility / Migration
既存参照、移行、rollbackが必要な範囲。

## Alternatives and Trade-offs
比較した案・理由・既知risk。恒久判断のADRへの参照。

## Risks / Unknowns
未確認事項、影響する要件/設計、blockingか、戻り先と担当。

## ADRs
実在する判断記録のpath。

## Review Readiness / Handoff
対象版、レビュー要否と理由、確認してほしい点、実装承認との区別。

## Artifacts
正本、HTML、図、編集元、検証結果と関連する実在path。
