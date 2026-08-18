---
name: debug-and-fix
description: 特定の不具合、回帰、flaky failure、性能劣化について、症状を検出できる再現loopを作り、根本原因を証拠で絞り、最小修正と回帰確認まで完了する。原因説明だけでなく、直してgreenにする依頼で使う。
---

# Debug and Fix

コードを眺めて推測する前に、ユーザーの症状そのものをred/greenで判定できるfeedback loopを作る。修正依頼として起動したら、根本原因、最小修正、元症状と回帰範囲の再検証まで閉じる。

## 完了契約

開始時に次を短く固定する。

- 観測された症状と期待する挙動
- 環境、入力、version、発生頻度
- 成功条件
- 修正が依頼範囲に含まれること
- 既知の正常状態または比較対象
- flaky / hang / performanceでは試行回数または時間budgetと、修正前後を比較する判定基準

診断だけを依頼された場合は修正しない。このskillは「直して」「解決して」「改善して」または同等の修正依頼に使う。GitHub Actionsだけの失敗は、利用可能なら `ci-debug` を先に使う。

## 1. Red-capable loopを作る

次を満たす1つのcommandを作り、実際にredを確認する。

- 実際の症状を検出し、別の近接エラーを誤認しない
- 修正後に同じ条件でgreenを判定できる
- 可能な限り高速で決定的
- agentが無人で反復実行できる
- 各試行にwall-clock timeoutがあり、hang時も必ず終了する
- timeout時はkill前にstack、dump、trace等の必要最小限の診断artifactを採取し、子process treeまで回収する
- pass、通常failure、timeout / hangを別の結果として記録する

優先順の例:

1. 既存または追加したfailing test
2. HTTP / CLI / fixture / snapshotの再現command
3. headless browserやtrace replay
4. 最小harness、property / fuzz loop、bisection、旧版とのdifferential run

flaky bugでは単発成功をgreenとしない。seed、time、filesystem、networkを固定するか、同じ刺激の反復・stress・隔離した並列実行で再現率を測る。baselineとしてattempt数、failure / hang数、timeout、seed、elapsedを記録し、修正前後を同じ試行数または同じ時間budgetで比較する。性能問題ではlogを増やす前にbenchmark / profiler / query planのbaselineを取る。

budget内でredを作れない場合は「直った」と判定しない。原因を推測して進まず、試した内容を示し、次のinstrumentation、再現環境、redact済みartifact、または必要な権限を求める。

## 2. 再現を最小化する

loopを反復し、入力、設定、呼び出し元、data、stepを1つずつ減らす。flaky症状では各削減候補を同じsampling ruleで比較し、1回のgreenだけで要素を除外しない。残った各要素を外すとgreenになるところまで縮める。最小再現は後の回帰test候補にする。

## 3. 必要な場合だけ独立調査を並列化する

boundedなred-capable loopが存在し、未知の独立軸が2つ以上ある場合だけ[parallel-investigation.md](references/parallel-investigation.md)を読む。既定は最大3レーンにする。loopができた時点で、親agentの最小化とread-onlyなrepo / artifact / external調査は並行してよい。

- repo / ownership: 実行経路、責務境界、最近の変更、正常系との差分
- reproduction / runtime: 最初に期待からずれる境界、環境差、log / trace
- external evidence: 公式docs、upstream issue、changelog、version固有の既知regression

明確なcompiler error、単一test failure、所有箇所が既知の局所bugは単独で続ける。調査agentへsourceやworking treeを変更させず、親agentが共通stress harnessを所有して証拠を統合する。runtime実験が必要なら独立worktree、temp、cache、portへ隔離するか、親agentが直列実行する。

## 4. 仮説を順位付けして反証する

証拠に支えられる範囲で最大3〜5個の相互に区別できる仮説を作り、各仮説に「原因なら、どのprobeで何が起きるか」を付ける。個数を満たすために推測を水増ししない。単一変数のprobeで上位から検証し、否定した仮説も短く残す。

instrumentationは境界を区別する最小量にする。temporary logには一意のtagを付け、完了時に検索して除去する。多数決ではなく、対立仮説を区別するevidenceで決める。

## 5. Regression testと最小修正

実際のbug patternを通る正しいtest seamがあれば、修正前に最小再現をfailing regression testへ変える。flaky stress reproducerは、決定的なseamへ落とせた場合だけ通常suiteへ入れる。決定的にできないharnessは診断用または隔離suiteへ置き、default CIへ混ぜない。浅すぎるseamしかなく偽の安心になる場合は無理にtestを書かず、そのarchitecture gapを記録する。

根本原因に直接効く最小修正を単一writerが行う。複数仮説の修正、無関係なrefactor、silent fallbackを混ぜない。

## 6. 元症状でgreenを確認する

完了前に次を確認する。

- regression testまたは代替verificationが通る
- 最小化前の元scenarioでも症状が再現しない
- 影響範囲のfocused gateが通る
- flaky / performanceではbaselineと同じ試行数または時間budgetで改善を確認した
- temporary log、harness、debug artifactを除去または明示的な場所へ隔離した

修正でgreenにならなければ、更新されたevidenceを使って仮説工程へ戻る。調査報告だけで完了扱いにしない。

## Handoff

- 症状と期待値
- red/green commandと結果
- 最小再現
- 調べた仮説と否定根拠
- 根本原因
- 修正
- regression / original scenario / focused gateの結果
- 残存riskと再発時の最初のcommand

## 安全上の注意

- secret、個人data、認証headerをlogやartifactへ残さない。
- 本番へのinstrumentation、外部変更、data mutationは権限を確認する。
- log追加でtimingやraceが変わる可能性を考慮する。
- high-riskな修正は必要に応じて `deep-review` へ渡す。
