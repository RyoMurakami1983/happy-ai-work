# Technical Design 009: 着手判断・短縮経路・任意の開始時設定

Date: 2026-09-26
Revision: 1
Status: 採用。独立レビュー後、2026-09-26に利用者が文書commit後の実装を承認。レビュー対象版はcommit `51d65bd`と[レビュー009](../reviews/009_TECHNICAL_DESIGN_REVIEW.md)に保存。

## Goal / Normative Inputs

[PRD 009](../prd/009_PRD.md) R-01〜08 / AC-01〜11を実現する。要求と変更方針は合意済みで、本書は構造と公開操作を具体化する設計案。repoのAGENTS.md、既存home-bootstrapの適用条件、ADR [0003](../adr/0003-finalization-gate-ownership.md)・[0004](../adr/0004-preview-plugin-distribution.md)を既存境界とする。

文書作成・レビュー後、配布物の実装と評価実行が承認された。実ホーム適用とIssue #35・#29の実装は対象外。構造契約はレビュー版から変更せず、実装の検証結果は計画と評価記録へ残す。

## Current Structure / 観測事実

基点はmain `7310f69d904df0a0e4d52f161a2f55587e73a92c`（PR #34 merge）。

- homeテンプレートは会話段階と変更依頼を区別するが、Issue選択と着手許可の区別は具体化していない。
- `to-prd/SKILL.md`は「単一の明確な変更ならimplementへ直接渡してよい」。`implement`の入力確認には明示的な着手許可の確認項目がない。
- `implementation-plan`と`implement`には「1ユーザー行動または1受け入れ条件」というsliceの説明がある。
- `home_bootstrap.py`の`merge(existing, managed)`は管理領域全体をテンプレートへ置換する。任意設定の抽出・保持はない。
- Yohakuは明示呼び出し時の会話内継続を持つ。開始時の常時適用を保存する機能はない。
- 個人ホームとインストール済みテンプレートの差は調査時点の観測。旧版の利用が前回誤着手の唯一の原因とは推定しない。

## Structure Decisions / Target Trace

| ID / 予定target | 責務・判断 | 根拠 | この配置が必要な理由 |
| --- | --- | --- | --- |
| D-01: home-bootstrap/assets/AGENTS.md | 共通の相談・対象選択・実装許可の区別を短く示す | R-01、03、07 | skill未起動時にも入口で判断するため |
| D-02: to-prd/SKILL.md、implement/SKILL.md | PRD側で短縮理由と許可を引き継ぎ、実装側で会話上の許可と範囲を確認する | R-02、03 | 準備が整ったことと着手許可を各工程の境界で区別するため |
| D-03: implementation-plan/references/vertical-slice.md（新規予定） | 垂直スライスと短縮条件の正本。to-prd、implementation-plan、implement、WORK_ARTIFACTS.mdから判定時に参照する | R-04、07 | 必要な場面で同じ定義を使い、配布先でも参照を完結するため |
| D-04: home-bootstrap/SKILL.md | 利用可能性の確認、利用者への選択提示、適用承認を担当 | R-05、08 | 会話とskill一覧を参照できる担当に置くため |
| D-05: home-bootstrap/scripts/home_bootstrap.py、assets/yohaku-startup.md（新規予定） | 選択状態を抽出・保持し、基本テンプレートと任意文言を合成する | R-06、08 | 更新で選択が消えず、同じ入力から同じ差分を得るため |
| D-06: yohaku/SKILL.md | 利用者が承認した開始時設定も会話内継続の入口と明示する | R-06 | 通常の自動選択と利用者による常時適用を混同しないため |
| D-07: README、tests、evals | 導入説明、更新の保存契約、行動観測を担当 | R-01〜08 | 静的な正しさと実際の行動を別々に確認するため |

targetのskill名は`plugins/happy-core/skills/`、`plugins/happy-coding/skills/`、`plugins/happy-preview/skills/`にある既存配置に対応する。新しい共通referenceは同じhappy-coding plugin内の相対リンクで参照し、配布先へ母艦repoのdocsやhome CONTEXTを要求しない。

## 着手と短縮経路の契約

### 共通方針の文言案

> 依頼の段階を会話から把握する。相談、実現可能性の確認、Issueの選択だけでは実装を始めず、必要な調査と要求整理を進める。提案への賛意やPRDの承認を、実装開始の承認とみなさない。実装範囲について明示的な依頼・承認がある場合は、その範囲で進める。

相談という単語だけで停止する規則にしない。明示された文書作成や局所修正はその範囲で進められる。実装と無関係な一般質問へ開発工程を課さない。

### PRD短縮の成立条件

一つのまとまった振る舞いまたは明確な局所修正で、要求・受入条件・既存構造に沿う方法・検証方法が明確であること。新しい構造判断や順序調整が残る場合は該当工程へ戻る。複数repo、公開契約、長期的な構造、互換性、移行・運用への影響は、既存WORK_ARTIFACTSの省略制約とも照合する。一つのsliceという事実だけでは省略できない。

短縮経路では、対象範囲、省略する設計書・計画書と設計レビューの要否、具体的な理由、その内容での実装可否を利用者へ示す。例:

> 今回はボタンの文言だけを変更し、処理や権限は変えません。単一の明確な変更のため、PRDのみで設計書と計画書は不要です。既存の表示文言だけなので設計レビューも省略できます。このPRDの内容で、そのまま実装してよいですか？

明確に依頼済みの局所修正をわざわざPRD経由へ戻さない。短縮内容を後から新たに決めた場合は、その内容への許可を確認する。同じ対象・範囲・省略内容への許可を既に得ていれば再質問しない。

### Handoff

工程を渡す際に次を短く残す。専用の永続許可DBは作らない。

- 対象と実装範囲。
- 省略工程と理由（該当時）。
- 許可の状態、根拠となる利用者発言、許可された範囲。
- 未確定事項と戻り先。

`implement`は記録中の「approved」という自己申告だけに依存せず、利用可能な会話の合意と最新の制約を照合する。根拠不足・範囲変更・後からの停止指示があれば、影響部分を開始せず確認へ戻す。Issue本文やPRDの存在を許可の代替にしない。計画省略経路にも同じ許可確認を引き継ぐ。

## 垂直スライスの定義案

> 利用者または外部の呼び出し元から観測できる、一つのまとまった振る舞いを、必要な層にまたがって実現・検証する変更単位。一つのsliceに正常系・境界条件・失敗時など複数の受け入れ条件を含めてよい。

ファイル数・層数・AC数で単一かを判定しない。例えば設定の保存と不正値の拒否は同じ振る舞いに属し得る。一つの決済操作でも新しい認可・外部連携判断があれば設計が必要。文言・文書修正へ不要なUI・DB変更を加えず、特定のvertical slice architectureを要求しない。PRDは要求単位を確認し、技術的なslice分割を新しく設計しない。

## Yohaku: State / Public Interface / Data Flow

### 利用可能性と選択

home-bootstrapの実行者が、現在選択可能なskill一覧と本文の参照成功で判定する。スクリプトによるキャッシュ走査やplugin自動導入は行わない。未設定かつ利用可能なら常時適用の意味を示して希望を尋ねる。保存済みの有効・無効は通常更新で再質問しない。利用者が変更を希望すれば改めて差分へ反映する。

「この会話で解除」は会話内の適用終了であり、保存済みの常時適用設定を自動変更しない。今後も無効にしたいという依頼は、home-bootstrapで無効化差分を確認する。

### 保存形式（設計案）

既存のstart/end管理領域内に、最大1個の状態コメントを置く。新たな管理領域やhome CONTEXTは作らない。

```html
<!-- happy-ai-work:yohaku=enabled -->
```

- コメントなし: 未設定。旧版の管理領域もこの状態。
- `enabled`: 利用者が常時適用を選択済み。開始時の指示を合成する。
- `disabled`: 利用者が常時適用しないことを選択済み。開始時の指示を合成しない。

状態コメントは更新処理のためのmetadataであり、別の管理領域の開始・終了マーカーではない。管理外にある同様の文字列は保存し、設定値として読まない。未設定を無断でdisabledと記録しない。

CLI案: 既存の`--dry-run`、`--apply`、`--target`、`--template`を維持し、`--yohaku preserve|enable|disable`を追加。省略時は`preserve`。

| 既存状態 | preserve | enable | disable |
| --- | --- | --- | --- |
| 未設定 | 未設定 | enabled | disabled |
| enabled | enabled | enabled | disabled |
| disabled | disabled | enabled | disabled |

`enable/disable`を指定する前の利用者選択と適用承認はskillの責務。CLI自体が会話上の承認を検証できるとは扱わない。

### 合成と適用

`assets/AGENTS.md`を基本方針の正本、追加予定の`assets/yohaku-startup.md`を有効時文言の正本とする。既存管理領域から状態を抽出→CLIの選択を解決→基本方針・状態コメント・有効時文言を単一管理領域に合成→既存merge境界で差分生成→dry-runまたは承認済みapply、の順とする。

`--template`も基本テンプレートの差し替えとして維持する。入力テンプレートに任意状態コメントが埋め込まれている場合は、二重設定を避けるため書き込み前にエラーとする。通常の旧テンプレートは利用できる。管理領域内の既存内容は従来どおり配布物で更新するため、独自追記はskill側の差分確認で競合を解決する。

有効時の文言案:

> 新しい会話の開始時に、利用可能なYohakuスキルを読み、その会話中の説明と成果物へ適用する。利用者による適用範囲の指定・解除を優先する。利用できない場合は共通方針で続ける。

Yohaku本体には、承認済みの開始時設定も明示利用と同じ会話内継続として扱う旨を加える。通常の自動選択の範囲を全利用者について変更しない。新会話ごとに保存済み設定から適用し、文脈圧縮は既存の引き継ぎ規約で扱う。毎回答の再読・告知を要求しない。

### 失敗時と信頼境界

- 重複・未知値・不正な状態コメント、既存start/endの不整合は書き込み前にエラーとし、ファイルとbackupを変更しない。既存の設定を推測して修復しない。
- Yohaku利用不可はスクリプト失敗にしない。保存済み選択を保持し、会話は共通方針で継続する。
- dry-runはファイル・backupを作成しない。applyは既存のbackupと管理外保持契約に従う。OSの書込失敗までtransactionalに回復する新機構は本設計の対象外。失敗時は未完了と報告し、実ファイルとbackupを照合する。
- 実home、インストール済みcache、repo配布物は別の書込境界。今回の文書作成と将来のrepo実装は、実homeの更新を許可しない。

## Compatibility / Migration / Change Scenarios

| 変化 | 変更箇所・局所性 | 互換性と確認 |
| --- | --- | --- |
| 短縮条件を調整 | 共通referenceとhandoffを使う3skills | 同一plugin内で参照。ホームの常時用語集を増やさない |
| home基本方針を更新 | 基本asset | preserveでYohaku選択が残ることを確認 |
| Yohaku文言を改善 | 任意assetとYohaku本体 | 状態IDは文言と独立。選択を読み違えない |
| previewが未導入・一時無効 | availability確認と開始時の条件分岐 | core単独で利用でき、設定は消さない |
| 旧版へ戻す | backupによる復元、利用版の確認 | 旧スクリプトは任意設定を保持しない。旧版適用前に差分を確認し、設定保持を保証しない |

repo配布物の完成、pluginの更新、実homeへの適用、次の会話での読込確認を別の状態として説明する。今回の評価は候補版を明示的に与える隔離評価であり、インストール済み環境の更新成功までは証明しない。

## Alternatives / Decision History

- rejected: 全初回依頼を必ず停止する方式。明確な局所修正への過剰停止を招く。
- rejected: implementだけで着手を止める方式。skill未起動の場面へ届かない。
- rejected: 全詳細をhomeへ記載する方式。無関係な会話の常時負担を増やす。
- non-goal: home CONTEXTの新設、汎用設定基盤、Yohakuの通常pluginへの移動。
- superseded: 設計005の「開始指示をAGENTSへ追加しない」は利用者のopt-inに限り更新。設計008の「implementへ同文を複製しない」は維持し、別責務として許可の受け取り確認を追加する。

rejected/non-goalは本案件の判断履歴であり、別途negative requirementとして採用されない限り恒久禁止ではない。採用範囲は[ADR案0005](../adr/0005-workflow-entry-and-optional-startup.md)へ記録する。

## Review Readiness / Handoff

- Review required: yes。利用者が設計レビューを含む計画を承認し、工程間の許可と永続設定の互換性に影響するため。
- 対象版: 本書Revision 1。レビュー時にPRD・本書・ADRのSHA-256を固定する。
- 確認点: 過剰停止、短縮経路の抜け道、definitionの責務、設定保持・異常時・旧版互換、previewへの必須依存がないこと。
- 設計を止める要求Unknowns: なし。技術案は独立レビューで確認済み。実装承認はPRD S-05に記録。行動評価は後続記録で確認する。
- Finalized contract: PRDの合意済み要件・ACと既存repo規約を規範入力とする。D-01〜07は本設計の提案で、レビューと利用者の実装開始判断後に実装契約として渡す。非採用案の詳細は本書に留める。
- 次担当: implementation-planへ構造判断・上表のtarget trace・許可状態を渡す。独立レビューの対象版と限界はレビュー009に記録する。

```yaml
artifacts:
  - docs/prd/009_PRD.md
  - docs/design/009_TECHNICAL_DESIGN.md
  - docs/adr/0005-workflow-entry-and-optional-startup.md
```
