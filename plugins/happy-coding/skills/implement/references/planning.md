# 実装内の計画

複数sliceの実依存、外部開始条件、HITL、公開契約、移行・運用、または再開可能な記録が必要なときに読む。新しいarchitectureは決めず、採用済み契約を実行可能な順序にする。

## 計画に残すもの

- 目的・AC・対象外と、実装許可の範囲・根拠となる利用者発言。計画のみの依頼なら「今回の依頼は計画のみ」と記録し、過去の実装許可があれば履歴として区別する
- ACから観測可能なbehavior、各sliceのDone、public test surface、first test、REDの期待失敗、GREEN / acceptance commandへの対応
- `finalized_contract`がある場合はnormative source → slice / 主要な恒久targetへのtrace。exclusionsは識別子と参照だけを保持し、非採用案の責務を作り直さない
- schema、consumer/provider、外部成果物などの実依存。必要な開始条件、成立の証拠、未成立時に影響するslice
- 検証の目的・規模、合成/実環境、所要時間の見込みと根拠（不明なら不明）、timeout/試行budget。[検証通知](verification-communication.md)へ渡し、予定commandと実行結果を区別する
- 実装中の変更理由と次の再開点。詳細な作業日記や全testの先書きにはしない

[PLAN template](../assets/NNN_PLAN_TEMPLATE.md)を必要な節だけ使う。slice数・HITL数は固定しない。初回はtracer bulletで縦断し、以後は価値とriskを早く観測できる順を選ぶ。確定していないsliceの並列実装はしない。

## HITLと外部前提

HITLは人の主観、実端末、外部appの確認がacceptanceに必要な境界だけに置く。reviewable milestone、launch、代表操作、期待結果、feedbackや承認による再開条件を残す。自動runtime evidenceで足りるsliceをUIという理由だけで止めない。

外部artifactが未着でも、依存しない許可済みsliceは進められる。外部データを捏造してgateを通さず、artifactの版・hash・互換性など契約で定めた証拠が揃うまで影響sliceは待つ。複数repoの既存`plan.md` YAMLと`checkpoints/contract_verify.py`の形式を変更せず使い、人間向け`docs/plan/NNN_PLAN.md`と混同しない。

## 移行・運用と回復

migration / operationsは計画不能の理由ではなく、明示的な保存計画が必要な条件である。影響するデータ・利用者・互換性、段階的切替、失敗検知、backup / rollbackまたはroll-forwardの根拠、回復確認commandを残す。データ削除・本番実行・権限拡張の許可を実装許可から推定しない。回復方法や公開契約の判断が未決なら設計へ戻すが、安全な調査・合成検証まで一律停止しない。

## 計画を変えるとき

順序・分割・統合の調整でAC、公開契約、採用済み構造、許可範囲、実依存、HITLと回復条件が保たれるなら、理由と検証への影響を記録して実装を続ける。取得済みの同じ実装許可を聞き直さない。既存のPASS evidenceは過去の対象版に紐づけたまま残し、変更で影響を受けるtestは再実行する。

契約自体の変更、normative source不明、未決の構造判断、追加権限は`REPLAN_REQUIRED`。影響する範囲を止め、要求・設計・許可のそれぞれの所有者へ具体的な問題と選択肢を返す。単なるtest失敗は`FAIL`として同じ実装を直す。

## 保存・表示・完了

[成果物規約](WORK_ARTIFACTS.md)に従う。短い計画でも後から判断が必要なら保存し、依存や人の確認を図で読む価値がある場合だけ[HTML](html-plan.md)を併用する。形式を実装の許可にしない。

旧implementation-planの`docs/plan/NNN_PLAN.md`、template由来の節、`artifacts`、HITL、finalized contractはそのまま受け取れる。機械的な再作成・番号変更は不要。参照するpathが欠けていれば所在・版を調べ、確認できない契約を埋めない。すべての対象sliceがPASSして初めてPLAN_DONEへ改名する。未完了分は明示的な次のplan/handoffへ切り出し、元の全体が完了したとは報告しない。HTML併用時は正本の変更と改名に合わせ入力・リンクを再生成する。
