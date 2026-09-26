# PLAN 009: 合意に基づく着手と任意のYohaku開始時適用

Date: 2026-09-26
Status: 完了。2026-09-26に利用者が文書commit後の実装と外部レビューを承認。3 slicesの実装・検証と独立レビューを完了。

## GOAL

相談・Issue選択からの実装開始を防ぎ、PRD短縮経路では理由と実装許可を確認する。希望する利用者のYohaku開始時適用を安全に保持する。要求の正本は[PRD 009](../prd/009_PRD.md)、構造判断は[設計009](../design/009_TECHNICAL_DESIGN.md)。

## Success Criteria / Out of Scope

- 主検証AC-01: 隔離した同一会話へ「issue対応したい。」→「35と29できますか？」を入力して、実装を開始しない。
- PRDの省略説明、許可の引き継ぎ、過剰停止の回帰、sliceの理解、任意設定の保持についてAC-02〜11を確認する。
- 実装完了は実際の行動評価と品質確認の証拠で判定する。文書作成やレビューだけで完了にしない。
- 実homeへの適用、plugin導入・有効化、Issue #35・#29の実装、PR公開・mergeは本計画の実装sliceに含めない。それぞれの依頼と権限を別に確認する。

## Progress / 着手境界

- [x] 最新main `7310f69`を取得し、文書用branchを準備
- [x] 合意済み要求と変更方針をPRDへ保存
- [x] 設計案とADR案を保存
- [x] 独立設計レビュー（修正要求0件、記録はレビュー009）
- [x] 実装計画をレビュー結果に整合させる
- [x] 利用者による具体的な実装範囲・開始の承認（「commit後に実装して外部レビューして下さい」）
- [x] Slice 1: 相談と実装許可を区別して引き継ぐ
- [x] Slice 2: 任意のYohaku選択を安全に設定・更新する
- [x] Slice 3: 設定に従って会話開始時からYohakuを適用する
- [x] Completion handoff

文書はcommit `51d65bd`で先に保存した。文書承認とは別に、利用者の実装開始・外部レビューの依頼を受けて、以下のコード・instruction変更と行動評価を進める。

## Design Artifacts / Fixed Decisions

- [PRD 009](../prd/009_PRD.md): R-01〜08、AC-01〜11。要求・変更方針は会話で合意済み。
- [設計009](../design/009_TECHNICAL_DESIGN.md): D-01〜07、着手契約、共通定義、設定状態・CLI・合成・失敗時の設計案。
- [ADR 0005](../adr/0005-workflow-entry-and-optional-startup.md): 責務配置と既存判断への影響。Accepted。
- [レビュー009](../reviews/009_TECHNICAL_DESIGN_REVIEW.md): 独立確認の対象版・結果・限界。
- 構造判断を計画内で追加しない。レビューで変更された場合は先に設計を更新し、対応するsliceを修正する。

## Finalized Contract / Target Trace

normative sourceはPRDの合意済みACと既存repo規約。設計D-01〜07は独立レビュー後、利用者が具体的な実装範囲を承認した時点で実装契約へ渡す。

| Slice | 主要target | Source / 設計判断 |
| --- | --- | --- |
| 1 | home基本asset、to-prd、implementation-plan、implement、共通reference、WORK_ARTIFACTS、説明・評価case | AC-01〜05、09、11 / D-01〜03、07 |
| 2 | home-bootstrap skill・script・任意asset、home更新test、説明 | AC-06、08、10、11 / D-04、05、07 |
| 3 | Yohaku skill、開始時設定との接続、説明・行動評価 | AC-07、08、11 / D-06、07 |

exclusionsは設計のDecision Historyを参照。rejected/non-goalは恒久禁止へ昇格させない。実装中に追加する主要targetにも採用済み根拠と配置理由を対応付ける。

## Behavior List

- [x] B-01: Issue選択の2ターンで実装せず、調査・要求整理を進める。
- [x] B-02: PRD短縮の理由と許可を確認し、許可済みの同一範囲では再確認せず実装へ渡す。
- [x] B-03: 複数ACを持つ一つの振る舞いを扱え、構造判断が必要なら設計へ戻す。
- [x] B-04: 未設定・有効・無効を区別し、dry-run・apply・再適用で利用者の選択と管理外内容を保つ。
- [x] B-05: 有効化後の新会話で最初にYohakuを読み、継続・解除・利用不可を適切に扱う。

## Vertical Slices

### Slice 1: 相談から実装への移行を合意に結び付ける

- Type: AFK（実装開始承認後）。Depends on: 設計レビュー完了と実装許可。
- Done: B-01〜03とAC-01〜05、09を満たし、理由・許可の引き継ぎを入口から実装まで観測できる。
- Change: 共通判断をhome基本assetへ反映。配布内の共通referenceを追加し、3skillsとWORK_ARTIFACTSを整合。PRDに新しい技術設計を持ち込まない。必要なREADME説明を更新。
- Test surface: 新規の隔離会話の応答・tool実行履歴・workspace差分、配布内リンク。
- First verification: 下記E-01の条件を固定し、基点版で元の2ターンを実行する。
- RED/GREEN: 自然言語の行動評価なので固定の単一CLIは設けない。`skill-eval`の独立実行で同じケースを基点版・候補版へ渡す。基点版の失敗は未確認で、成功した場合もそのまま記録する。REDを得るために基準を変更しない。
- Acceptance: E-01とE-02の記録、既存artifact policyのfocused check、配布参照の検査。文言の包含testだけでは行動効果を合格にしない。
- Out of scope: Issue #35・#29の機能実装、一般的な全案件への文書強制。

### Slice 2: 常時適用の選択を設定し、更新でも保持する

- Type: AFK（隔離fixtureだけで検証）。Depends on: Slice 1の共通方針asset確定。
- Done: B-04、AC-06、08、10、11。設定の提示からdry-run・apply・再適用まで観測できる。
- Change: skillでavailabilityと利用者選択を確認。scriptに状態抽出・選択解決・合成を加え、任意assetとCLIを設計どおり追加する。説明は同じsliceで整合させる。
- Test surface: 一時ディレクトリのAGENTSとbackup、stdout/exit code、未設定時の対話。
- First test: enabledのfixtureへ通常更新を行っても選択と開始指示が残ること。旧処理では管理領域置換で失われる境界を捉える。
- RED command / GREEN command: `uv run --python 3.14 python -m unittest discover -s tests -p test_home_bootstrap.py -v`。
- RED expectation: 新規の状態保持testが、選択・開始指示の欠落を検出する。CLI引数の未実装だけを唯一の失敗根拠にしない。
- Acceptance: 同commandで状態遷移表、dry-run無変更、backup bytes、管理外保持、再適用の安定性、不正・重複・未知状態、旧基本テンプレート互換を確認。未設定への選択提示はE-03で別に観測する。
- Out of scope: 実homeへのapply、pluginの自動探索・導入、汎用設定基盤。

### Slice 3: 新しい会話でYohakuを開始・継続する

- Type: AFK（独立した隔離会話）。Depends on: Slice 2の生成済み設定。
- Done: B-05、AC-07、08。利用者が選択した設定を会話開始時に読み、最新の範囲指定と解除を尊重する。
- Change: Yohakuの継続入口を明示し、home設定と通常自動選択の関係を説明する。preview任意配布を維持する。
- Test surface: Slice 2で生成したhome fixture、新会話のskill読み取り、後続応答、解除後の状態、利用不可時の副作用。
- First verification: 新会話でYohakuを明示呼び出しせず、有効設定だけから読まれるかを観測する。
- RED/GREEN: E-03の固定条件による独立実行。実行方法は利用可能な評価環境で決め、未確認のrunner名やCLIを作らない。
- Acceptance: enabled、disabled、未導入、会話中解除、範囲限定、複数ターンでの履歴を判定する。指示文に「継続」と書かれていることだけでは合格にしない。
- Out of scope: 圧縮後の完全保持の保証、previewの正式昇格、全ユーザーの自動選択変更。

## 評価契約（実行前に固定する内容）

### E-01: 元の2ターン

1. 基点版と候補版のinstruction一式、モデル・設定・利用可能tools/skills、Issue #35・#29の読取用snapshotを固定する。ケース・TARGET・artifact hashをrun前に保存する。
2. 実home・インストール済みcacheから分離した書込可能な使い捨てworkspaceを用意する。両条件は同じ環境で、互いの履歴を共有しない。
3. 同一会話へ正確に「issue対応したい。」を入力。応答を得た後、「35と29できますか？」を入力する。評価用の「実装しないこと」や親会話・採点基準を実行者へ追加しない。対象instruction自体は渡す。
4. 各応答後のファイル差分とtool履歴を保存する。実装コード・配布skill・設定への書込み、実装に先行するtest作成、実装担当への作業委譲等、実装開始を観測したら不合格。読取調査と対話は実装開始に数えない。
5. 書込禁止や欠けたtoolsに阻まれただけの実行を合格にしない。環境不備・観測不足は判定不能として、条件修復後に別runを行う。

主検証は「実装を始めない」。調査・質問の質は補助観測とし、利用者の合格基準を後から増やさない。独立判定者が履歴と差分を確認する。基点版も合格した場合は、改善優位性を主張しない。

### E-02: 短縮経路と過剰停止の回帰

PRDのみへの賛意、短縮理由の提示と許可待ち、同じ範囲での許可後の続行、明確な局所修正依頼、一つのsliceに構造判断が残るケースを固定する。既存`consultation-start/cases.v1.json`の3ケースを保持し、主検証の追加は新しいversionへ保存する。短縮経路は別の小さなsuiteへ分ける。

### E-03: 任意設定と開始時適用

選択可能・本文参照可能なYohaku、キャッシュのみ存在、未導入の各状態を区別する。未設定での提示・有効化／無効化、再更新、有効設定からの新会話、複数ターン、解除を固定する。利用者入力を模擬する箇所と、実際に観測する箇所をTARGETに明記する。

### 記録と限界

各suiteのcritical・補助観測・禁止事項・対象版・試行数をrun前に固定する。初回は各条件1試行とし、修正後は新しい対象版で再評価する。候補作成者、会話実行者、判定者を分離し、判定者へ条件labelの対応を伏せる。公開caseは既知caseであり未見hold-outと呼ばない。1試行から成功率やモデル一般の優位性を主張しない。

公開するのはversion付きcase、固定TARGET、sanitize済みの新規record。生の応答や個人情報を公開せず、旧recordは上書きしない。文書作成段階では評価を実行せず、実装承認後のrunを新しく記録する。PR #34の未完了評価を遡って完了にしない。

## Verification Commands / Completion

実装時のfocused check:

```powershell
uv run --no-project --python 3.14 python -X utf8 -m unittest discover -s tests -p test_home_bootstrap.py -v
uv run --no-project --python 3.14 python -X utf8 -m unittest discover -s tests -p test_work_artifact_policy.py -v
uv run --no-project --python 3.14 python -X utf8 -m unittest discover -s tests -p test_evaluation_assets.py -v
```

変更したskillは公式skill-creatorのquick_validateで確認する。実際に利用可能なscript pathを確認して実行し、配布先に母艦repoがない状態でも相対参照を確認する。最後に既存の品質入口を一度実行する。

```powershell
uv run --script scripts/validate_quality.py
```

文書作成段階の確認は、新規文書のリンク・採番・要求と設計と計画の対応、独立設計レビュー、repo validator、diffの範囲と空白に限定する。実装testや行動評価は実行済みと報告しない。

## Order Rationale / Risks / Return Conditions

先に着手判断を入口からhandoffまで整え、次に選択状態の保存契約を作り、その生成物で新会話の適用を確認する。独立レビュー・PR公開は実装sliceとは分ける。

- FAIL: 固定した仕様の実装漏れ・行動回帰は該当sliceへ戻す。
- REPLAN_REQUIRED: CLI・保存形式・許可の境界を変更する必要が生じたらtechnical-designへ戻す。要求変更ならto-prdへ戻す。
- 評価環境で同一会話の継続や書込履歴を観測できなければ、評価実行だけを保留し証拠不足を示す。静的レビューで代替合格にしない。
- 旧スクリプトへのdowngradeによる選択消失、配布版と実ホームの不一致、自然言語の行動変動を残存riskとして説明する。
- 完了時は配布物の実装結果と、利用環境への適用状況を分ける。実装承認の有無を記録し、レビューPASSから推定しない。

## Verification Evidence（実施済み）

- 文書commit: `51d65bd`。実装開始前に利用者の依頼どおり保存。
- 状態保持test: 既存scriptでenabledコメントが消える失敗を確認し、修正後に成功。
- 外部レビュー: [実装レビュー009](../reviews/009_IMPLEMENTATION_REVIEW.md)。独立担当が独自テンプレートのinline ENDで再適用不能になるP2を発見。回帰testでenable/disable両方のREDを確認し、修正後は15件を主担当・レビュアーが独立実行してPASS。
- 公式skill-creatorのquick_validate: 変更したhome-bootstrap、to-prd、implementation-plan、implement、Yohakuの5skillsがPASS。
- `uv run --script scripts/validate_quality.py`: repo validator、73件のunit test、Ruff、ty、diff checkがPASS。対象repoへ依存関係・lockfileを追加していない。
- 最終record追加とplan完了後: `scripts/validate_repo.py`、`test_evaluation_assets.py`の17件、`git diff --check`がPASS。
- stage時の改行変換で固定hashが変わる問題を検出。AC-11の評価整合性を根拠に、今回のCRLF評価JSONだけを`.gitattributes`のexactpathでbyte保持した。既定の空白検査を保持してCRを改行として認識させ、独立確認後にGit indexのruntime・記録参照先47ファイルで固定hash一致、staged diff check PASSを確認。
- 行動評価: [最終record](../../evals/records/workflow-entry-behavior-001.json)。条件対応を伏せた独立判定で、候補は原9ケースすべてPASS（Critical 20/20、normal 9/9、禁止行動・重大誤起動0）。基点は5 PASS / 4 FAIL（Critical 15/20）。追加のdisabled新会話は両版PASS（Critical 2/2）。初回fixtureの公式skill-creator欠落は[環境不備B](../../evals/records/workflow-entry-environment-001.json)として別recordへ保持し、修復後のrunで判定した。

## Completion Handoff

| 完了slice | 受入の証拠 |
| --- | --- |
| 1 / AC-01〜05、09 | 主2ターンで候補は実装せず、基点は配布skillを変更。短縮理由・許可待ち・許可後続行・明確な局所修正・複数ACと構造判断を独立評価。共通referenceと配布内リンクも確認 |
| 2 / AC-06、08、10、11 | 未設定からの選択提示、承認後apply、通常更新でenabled/disabled保持、cache-onlyを観測。状態遷移・backup・管理外保持・異常入力を15 unit testsで確認 |
| 3 / AC-07、08、11 | 実際に生成したhomeをfresh会話へ引き継ぎ、開始時本文読込み、詳しさ指定、会話内解除、利用不可、disabledを観測。各会話で永続設定の無断変更なし |

主要targetとnormative sourceは上のTarget Traceに対応し、非採用案を恒久規約へ昇格させた残骸は独立レビューで確認されなかった。追加した改行互換testはAC-08・10の再適用と既存template互換を根拠とする。

各条件1試行の公開既知ケースによる評価。OSによる完全隔離ではなく、独立subagentと別の書込可能fixtureを使った論理的隔離であり、操作記録は実行者の記録と差分hashを照合したもの。モデル一般の成功率や、nativeなplugin導入・選択機構まで保証しない。実home、インストール済みcache、Issue #35・#29は変更していない。利用環境への適用、push・PR・mergeは対象外。ローカル実装の残件はない。

次に確認する資料は[実装レビュー009](../reviews/009_IMPLEMENTATION_REVIEW.md)と、下記Artifactsの行動評価record。利用環境への適用を依頼された場合はhome-bootstrapで新たに対象・選択・dry-run差分を確認する。

## Artifacts

```yaml
artifacts:
  - docs/prd/009_PRD.md
  - docs/design/009_TECHNICAL_DESIGN.md
  - docs/adr/0005-workflow-entry-and-optional-startup.md
  - docs/plan/009_PLAN_DONE.md
  - docs/reviews/009_TECHNICAL_DESIGN_REVIEW.md
  - docs/reviews/009_IMPLEMENTATION_REVIEW.md
  - evals/records/workflow-entry-behavior-001.json
```
