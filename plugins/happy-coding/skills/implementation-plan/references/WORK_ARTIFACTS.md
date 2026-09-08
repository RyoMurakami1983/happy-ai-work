# Work Artifacts

`interview-with-docs`、`to-prd`、`technical-design`、`implementation-plan`、`implement`の間で渡す成果物の既定構造です。

## Canonical doc structure

```text
docs/
  grill_results/
    001_GRILL_WITH_DOCS_RESULT.md
  prd/
    001_PRD.md
  design/
    001_TECHNICAL_DESIGN.md
  plan/
    001_PLAN.md
  adr/
    0001-short-slug.md
```

## Numbering rules

- `grill_results` / `prd` / `design` / `plan` は同じ案件番号 `NNN` を共有する
- ADR は `docs/adr/0001-short-slug.md` の独立連番を使う

## 保存ポリシー（saved-by-default）

成果物は保存を既定とし、handoff の `artifacts` には実在する確定pathを列挙します。

- repoに `CONTEXT.md` がなければ作成し、あれば案件で確定した用語・境界を反映する
- `to-prd` は `docs/prd/NNN_PRD.md` を保存する
- `technical-design` は `docs/design/NNN_TECHNICAL_DESIGN.md` を保存する
- `implementation-plan` は `docs/plan/NNN_PLAN.md` を保存する
- `interview-with-docs` は、結果を後続PRDへ根拠・未決事項・重要判断として引き継ぐ場合を除き、`docs/grill_results/NNN_GRILL_WITH_DOCS_RESULT.md` を保存する

### conversation-only exceptions

`artifacts: conversation-only` は、利用者が明示的に文書不要と指定した場合、または変更が明らかに小さく低riskな small one-slice で、後続handoffや判断記録が不要な場合だけ選べます。handoffには `exception reason:` と具体的な理由を必ず記載します。

multi-repo、複数slice、public contractの変更、long-lived structure、compatibility、migration / operationsへの影響がある案件では例外を選べません。

## Write timing

- `CONTEXT.md` は開始時に存在を確認し、用語解決ごとに inline 更新する
- grill結果を後続PRDへ引き継がない場合は grill 完了時に保存する
- PRD / design / plan は各skillの完了時にcanonical pathへ保存する
- `implement` の completion handoff まで終わったら、必要に応じて `docs/plan/NNN_PLAN_DONE.md` へリネームする

## Boundary with `implement`

`docs/plan/NNN_PLAN.md` は人間向けの進捗計画です。
`implement` は各 slice の直前に slice contract を再固定し、TDD loop と slice gate を実行します。
handoff には必ず `artifacts:` フィールドを含めます。通常は `artifacts:` の下に保存したpathを列挙します。例外時だけ `artifacts: conversation-only` と `exception reason:` を併記します。`implement` は bootstrap でpathの存在と例外条件を確認します。

multirepository fleet の contract verification が読む repo root の `plan.md` YAML front-matter とは別物として扱います。

## PLAN template

PLANの正本テンプレートは`../assets/NNN_PLAN_TEMPLATE.md`に置きます。
PLAN は進捗を追う補助であり、重い工程表ではありません。

含めるもの:

- `GOAL`
- `Success Criteria`
- `Out of Scope`
- `Design Artifacts`と実装で守る既決の構造判断
- `Behavior List`
- `Vertical Slices`
- 各 slice の `HITL / AFK`
- 各 slice の `First test`
- 各 slice の `Test surface`
- `RED command`
- `RED expectation`
- `GREEN command`
- `Acceptance command`
- `Return Conditions`

含めないもの:

- 毎回の MVP 技術選定
- 詳細すぎるモジュールテスト仕様
- 実装後の PR / review / furikaeri 手順
- phase ごとの自動停止指示
