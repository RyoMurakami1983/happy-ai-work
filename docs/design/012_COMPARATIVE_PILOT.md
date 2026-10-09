# 012 — implement比較pilot 詳細設計

設計版: 0.1 / 2026-10-03。根拠: 承認済み基本設計0.2・評価方法v0.1。
現行基準: ab32391c9612ad7983a4805040a6331ad5f576db。
着手範囲: 比較準備、限定候補、データ検証・閲覧、tests、draft PR。merge・配布・有料実行は含まない。

## 結論と境界

最初はimplementのみ。現行配布pluginを変更せず、評価領域にlean候補を保存する。
必要な安全・承認・TDD・停止・HITLの意味を保ち、条件付き詳細のみreferenceへ移す。
本差分は通常改善でありConstitutionの優先関係を変更しない。候補の優位・採用は未判定。
全37技能の再編、認証、常設runner、model API、hold-outの作成/公開は対象外。

## 構成と受入

1. `evals/openai-first-implement/`に現行snapshot、候補、publicな開発caseとfixtureを固定する。
   小修正・docs-only・UI・未承認依頼の4群、正常・境界・失敗/不足の各3ケースを準備する。
   caseの目的は実際の作業であり「最初の返事」だけを評価しない。成果物diff、tool実行と結果、
   test、runtime、承認境界、質問・停止の時点を外部observerが保存する。
2. 準備scriptはcaseごとのfixtureと一条件のskillだけをfresh directoryへ出力する。
   入力はallowlistで固定し、採点基準・重み・他条件・会話履歴をbundleへ入れない。
   出力manifestはhash、source revision、case/conditionを持つ。既存先へ上書きしない。
   これは入力の最小化でありOS/tool/contextの隔離を提供しない。実行commandは実装しない。
3. `docs/evaluation-dashboard.html`は検証済みのsanitize済みJSONをlocal importする。
   スキーマ、出典、方法/model/cohort、実測/診断/架空の表示を分離する。詳細は
   `012_DASHBOARD_DATA_CONTRACT.md`。失敗/未完了/判定不能/未実行を全割当の分母に残す。
4. canonical quality入口へ既存unittest経由で追加。現在pluginを変えないのでreleaseは発生しない。

## 実行前gate（未充足なら実比較を開始しない）

- 同一正式model variant/取得可能なsnapshot、effort、harness、tools、permissions、fixture hash、
  context予算、token/time/cost上限をA/Bで固定。取得できないmodel名をGPT-6と断定しない。
- 72 runs（4×3×3×2）は基本設計の提案規模。実行規模/上限/費用を承認してから始める。
  小規模診断への変更もその範囲を記録し、72 runsを完了したことにしない。
- 新規contextで実行。実行者のfilesystem mount、検索、connector、network、ログ、親contextを検査し、
  private採点資産へのreadが実際に拒否されることを外部observerが記録する。
  `fork_turns:none`、役名変更、読まない指示、単なる別directoryは隔離の証明にならない。
  この環境のnative subagentsはshared filesystemを持つためblind trialとして使わない。
- 改善者はpublic開発caseのみ。最終hold-outは独立評価者の非公開領域。private artifactをrepoに置かない。
  blind graderには条件ラベルを伏せる。traceにskill参照pathが露出する場合は対応をprivate保持して匿名化し、
  意味を失うredactionならblind不可と記録する。推測可能性を独立性の完全保証へ読み替えない。
- 判定担当は独立agent/人とし、作成担当自身の採点を採用根拠にしない。

## 方法の事前登録

品質、安全、権限、重大ACを先に判定。hard failが1件あれば採用停止。判定不能はB、緊急例外はC。
Sは適格caseにのみQ/(1+λB)。Q、全gate、B、内訳、合格完了率を別に表示する。
λ=0.1、β=3は提案であり確定しない。以下をbaseline出力を見る前に独立校正し、所有者と確定する。

- Qの尺度、各AC anchor、合格threshold、正規化/上限
- bの単位、読む負担/判断項目/回答/手戻りのanchorと重複event統合方法
- 各caseでの最初に合理的に知り得た時点と、その判断に依存する作業eventの単位/正規化
- 回避可能eventはb(1+βd²)、必要質問の回避可能な先送りはbβd²のみ。
  新事実で初めて必要になった質問・適切な停止は0。実時間/返信待ち/無関係の作業をdにしない。
- 人の負担が推定か実測か、評者、判定根拠、曖昧時のBへの移行。

方法のdraftは採点値を生成しない。重みはprivate事前登録に保持し、hashと承認状態だけを公開できる。
登録後の変更は新method/run ID。過去recordを書き換えない。

## 仮説と反証

仮説: 本文を短くして条件付き参照へ移すと、必要な判断を保ちつつ不要読込み/確認負担が減る。
反対仮説: 重要条件の見落とし・参照往復が増え、品質や人の負担が悪化する。
同一model/context/fixtureの比較がなければinstructionの因果効果とは呼ばない。
同一case反復は独立task数ではない。小規模結果は診断であり一般優位・統計的有意を主張しない。
公開開発caseはhold-outでなく、当該caseへの適合は一般化の証拠にならない。
品質/承認の新規失敗が出た候補は採用せず、別候補・別runへ戻す。

## 検証順と終了条件

- 独立詳細設計review → TDDで準備/取込みの正常・不正・境界を検証 → 独立差分review。
- snapshot/candidateのlink可搬性、禁止ファイル非包含、hash整合、上書き拒否をfocused test。
- JSON欠測/重複/nonfinite/異cohort/矛盾gate、import失敗時保存、XSS、空状態を検証。
- `uv run --script scripts/validate_quality.py`、両OS CIをdraft PRの正確なheadで確認する。
- runtime/費用/事前登録が未確定ならインフラの到達点とblocked項目を返す。実測を捏造しない。
- 実比較合格後も最低2件の異なる実作業が未観測なら効果未確認。
  約5件で方法を再検討する案は件数稼ぎや新規仕事の生成を意味しない。

## 保管と復元

既存eval schema/records/historyは変更しない。新public caseもappend-only対象。
raw evidenceとprivate判定はrepo外。dashboard importはブラウザmemory内のみ、送信/永続化しない。
このPRの撤回は候補を採用しないこと。既存配布物のrollbackは不要。
