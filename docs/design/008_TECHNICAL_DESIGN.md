# Technical Design 008: 相談から成果物変更へ移る判断

## Goal / Normative Inputs

Issue [#33](https://github.com/RyoMurakami1983/happy-ai-work/issues/33) と [PRD 008](../prd/008_PRD.md) のAC-01〜06を実現する。既存のhome／repo／skillの責務を維持し、相談中の誤着手と明確な変更依頼への過剰停止をともに減らす。

## Current Structure and Observed Gap

- `home-bootstrap/assets/AGENTS.md` はホームへ配布する6項目の共通方針で、現時点の個人ホーム管理領域と一致する。目的把握は書かれているが、会話の段階と変更への着手判断は明記されていない。
- repoルートの `AGENTS.md` はこのrepoの配布・品質・統治境界を所有する。恒久規約の採用根拠は規定するが、着手判断は所有しない。
- `workspace-bootstrap/assets/AGENTS.md` は新しいrepo固有指示の土台である。共通方針のコピー先ではない。
- `implement/SKILL.md` は実装契約を受けた後の工程を所有する。skillが必要情報を確認できても、会話上の変更依頼の有無は別に判定する必要がある。

## Structure Decisions

1. 共通方針の最初の項目へ、依頼の段階を会話から判断する条件を融合する。相談・分析・比較では調査と回答を進め、候補案や賛意だけを変更依頼とみなさない。変更が任されたら範囲内で修正・検証を完了する。項目数は6を維持する。
2. 対象を「成果物の変更」とし、コードに限らず文書・設定にも適用する。明示された成果物作成や修正依頼は進められるよう、相談という単語だけで一律停止しない。
3. repoルート・workspaceテンプレート・`implement` skillに同じ規則を複製しない。各々の固有責務を保つ。
4. 配布テンプレートの編集と個人ホームへの反映は別の操作とする。後者は既存の`home-bootstrap`手順と利用者の明示判断に従う。

## Change Scenarios / Expected Locality

| 変化 | 変更する場所 | 影響を閉じる理由 |
| --- | --- | --- |
| 共通の着手判断を調整する | `home-bootstrap/assets/AGENTS.md` の第一項目 | 全repoに共通する判断の正本だから |
| 特定repoの変更対象・検証を調整する | そのrepoの `AGENTS.md` | 他repoへ波及させないため |
| 実装中のslice手順を調整する | `implement` skill | 着手判断と実装手順を分けるため |

## Interface / Flow

`home-bootstrap` の既存CLIが配布テンプレートを読み、dry-runで差分を表示する。承認された個人適用時だけ管理対象マーカー内を更新し、既存ファイルのbackupを作る。CLIのinterfaceや保存形式は変更しない。

会話では、依頼とこれまでの合意から現在の仕事を判断し、読取調査・回答または依頼された成果物変更へ進む。曖昧さが結果を大きく変える場合だけ質問する。単語の有無や固定の承認フローを判定器にしない。

## Compatibility / Boundaries

- 既存の目的・完了条件把握、必要な質問、安全、検証を残す。
- `README.md` と既存設計の「6項目」に整合させる。
- 個人ホームはrepo外であり、配布テンプレートの変更だけで更新済みとは扱わない。
- Issue #17のfinalization gateは採用内容を恒久成果物へ昇格する後段として保持する。

## Alternatives / Trade-offs

- repoごとに同文を置く案は、共通判断を分散させ、更新時の不一致を生むため採用しない。
- 全変更前に確認する案は、明確な修正依頼まで停止させるため採用しない。
- `implement` skillだけで制御する案は、skillを使わずに直接修正する場面へ届かないため採用しない。

これらの非採用案は判断履歴であり、別途採用されない限り恒久的な禁止規約ではない。

## Verification / Risks

- 既存のhome-bootstrap testとrepo validatorで、テンプレートの配布、管理領域の保持、文書・リンクを確認する。
- 複数ターンの相談、賛意後の比較、明確な修正依頼のscenarioで、誤着手と過剰停止を評価する。独立実行できない場合は静的reviewをbehavioral評価と呼ばない。
- 一項目への融合で長文化する危険がある。意図を保ちながら短くし、skillの詳細workflowを追加しない。

## Finalized Contract / Handoff

Normative source: PRD 008のAC-01〜06、repo `AGENTS.md` の恒久規約の根拠条件、`home-bootstrap/SKILL.md` の個人適用条件。

| 主要target | Source | 配置理由 |
| --- | --- | --- |
| `plugins/happy-core/skills/home-bootstrap/assets/AGENTS.md` | AC-01〜05 | 議論を知らない利用者の全repoで着手判断を再現するため |
| `docs/plan/008_PLAN.md` | AC-01〜06 | 今回の実行順と個人適用境界を追跡するため |
| `evals/consultation-start/cases.v1.json` | AC-01〜03 | 誤着手と過剰停止を同じ観測基準で評価するため |

Exclusions: repoへの共通文言複製（rejected）、全変更前の確認（rejected）、Issue #17の再実装（non-goal）。個人ホームへの適用は2026-09-25に利用者が明示承認し、dry-runとbackupを経て実施した。更新後の探索的な隔離試行は参考観測であり、正式な行動評価と採用判定は未実施。

```yaml
artifacts:
  - docs/prd/008_PRD.md
  - docs/design/008_TECHNICAL_DESIGN.md
  - evals/consultation-start/cases.v1.json
```
