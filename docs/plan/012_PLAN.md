# implement比較pilot — 実装計画

Artifacts: `docs/design/012_COMPARATIVE_PILOT.md`, `docs/design/012_DASHBOARD_DATA_CONTRACT.md`。
設計reviewの範囲別判定は `docs/reviews/012_TECHNICAL_DESIGN_REVIEW.md`。

## Slice 1: actor入力の再現可能な準備

- 振る舞い: 固定現行版と限定候補の各条件を、4群のpublic開発caseからfresh directoryに準備する
- 非対象: model実行・grading・隔離の実装・hold-out
- First test / RED: `python -m unittest discover -s tests -p test_comparison_bundle.py -v`。準備API未実装で失敗
- GREEN: 同command、fixture/task/skillだけをhash検証して出力
- Acceptance: 同commandでhash変化、path逸脱、上書き、4群、他条件/採点情報非包含を確認
- HITL: なし。OS隔離/実比較の判定にはこの成功を使わない

## Slice 2: 検証された台帳を表示する

- 振る舞い: local JSON importからcohort別の結果・欠測・根拠を表示
- 非対象: raw記録収集、機密採点、認証、勝手な定期更新
- First test / RED: dashboard validator未実装を確認
- GREEN / Acceptance: `python -m unittest discover -s tests -p test_evaluation_dashboard.py -v`
- Runtime: import成功/失敗保持/clear/filter/XSS/重複読込みの実ブラウザ確認
- HITL: 探索的確認。自動検証成功を利用者確認済みにしない

## Slice 3: 限定candidateと配布境界

- 振る舞い: implementの意味を保持して短い本文/条件付きreferenceへ配置
- 非対象: 現行plugin更新、全37技能再編、採用判断
- GREEN / Acceptance: `python -m unittest discover -s tests -p test_lean_implement_candidate.py -v`
- docsの配置確認でありREDが成立しない部分は構造検証と明記

## 終了gate

独立差分review、canonical quality、正確なheadのWindows/Ubuntu CI。
実行環境・model・登録方法・budget/費用の未確定は実比較のblockerとして残す。
実比較を開始せずにインフラの到達点を返せる。既存recordは変更しない。

## ローカル到達点

3 slicesの実装・focused検証・独立code/static reviewは完了。
実画面renderingは環境制約で未確認。実行者の隔離・model/予算・方法の登録も未確定。
公開承認前なのでpush/draft PR/両OS CIは未実施。この残件を隠すDONE renameは行わない。
