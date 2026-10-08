# Work Artifacts

`interview-with-docs`、`to-prd`、`domain-modeling`、`technical-design`、`implementation-plan`、`implement`の間で渡す成果物の既定構造です。

## Canonical doc structure

```text
docs/
  grill_results/
    001_GRILL_WITH_DOCS_RESULT.md
  prd/
    001_PRD.md
  domain/
    001_DOMAIN_MODEL.md
  design/
    001_TECHNICAL_DESIGN.md
  plan/
    001_PLAN.md
  adr/
    0001-short-slug.md
```

## Numbering rules

- `grill_results` / `prd` / `domain` / `design` / `plan` は同じ案件番号 `NNN` を共有する
- ADR は `docs/adr/0001-short-slug.md` の独立連番を使う

## 保存ポリシー（saved-by-default）

成果物は保存を既定とし、handoff の `artifacts` には実在する確定pathを列挙します。

- repoに `CONTEXT.md` がなければ作成し、あれば案件で確定した用語・境界を反映する
- `to-prd` は `docs/prd/NNN_PRD.md` を保存する
- `domain-modeling` のモデル化は既存のドメイン文書、なければ `docs/domain/NNN_DOMAIN_MODEL.md` へ保存する。用語整理だけなら用語集の更新で終え、モデル文書は作らない
- `technical-design` はMarkdownのみなら `docs/design/NNN_TECHNICAL_DESIGN.md`、新規のHTML併用案件なら `docs/design/NNN_design/NNN_TECHNICAL_DESIGN.md` を正本として保存する。形式は同skillの出力契約に従う
- `implementation-plan` は `docs/plan/NNN_PLAN.md` を保存する
- `interview-with-docs` は、結果を後続PRDへ根拠・未決事項・重要判断として引き継ぐ場合を除き、`docs/grill_results/NNN_GRILL_WITH_DOCS_RESULT.md` を保存する

### 図入りHTMLを併用する場合

設計の構成・処理順・状態や、複数sliceの依存・開始条件を人が判断するときは、Markdown正本への入口としてオフラインHTMLを追加できる。小変更へ図やHTMLを要求しない。利用者の形式指定と既存repo規約を優先する。

- 新規の設計資料は `docs/design/NNN_design/` に正本、`NNN_DESIGN.html`、表示用入力、必要な図と確認記録をまとめられる
- 計画の正本は `docs/plan/NNN_PLAN.md` を保ち、`NNN_presentation.json` と `NNN_plan/NNN_PLAN.html` 等を追加する
- 既存資料を自動移動しない。handoffは既定pathを推測せず、正本と派生資料の実在pathを渡す
- HTMLは要約・図・詳細の表示であり、独立した規範入力や実装開始の許可にはしない。正本更新・PLAN_DONEへの改名後は表示用入力とリンクも揃え、再生成する

形式ごとの保存・同期は[設計HTML](../../technical-design/references/html-design.md)と[計画HTML](html-plan.md)を参照する。

### conversation-only exceptions

`artifacts: conversation-only` は、利用者が明示的に文書不要と指定した場合、または変更が明らかに小さく低riskな small one-slice で、後続handoffや判断記録が不要な場合だけ選べます。handoffには `exception reason:` と具体的な理由を必ず記載します。

multi-repo、複数slice、public contractの変更、long-lived structure、compatibility、migration / operationsへの影響がある案件では例外を選べません。

small one-sliceや工程省略を判断するときは[垂直スライスと短縮条件](vertical-slice.md)を参照します。単一sliceでも設計・計画が必要な場合があります。保存を省略できることと実装開始の許可は別に確認します。

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
