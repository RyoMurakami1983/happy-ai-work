# Parallel Investigation

debugの並列調査は、再現条件の発見または固定後の仮説検証を速めるために使う。

## 起動条件

次をすべて満たす場合に使う。

- 共通の症状、既知の事実、調査budgetを共有できる。red/green commandが未確立なら、再現条件の発見を目的とするread-only調査に限定する。
- 所有境界、runtime、外部version等、独立した未知が2つ以上ある。
- 各レーンへ重複しない問いと停止条件を渡せる。

## Worker contract

各workerはsourceと共有working treeを変更せず、次の形式を返す。

```text
confirmed facts and evidence:
root-cause candidates:
next falsifiable probe:
rejected hypotheses:
confidence:
possible fix and risk:
```

repo lane、runtime lane、external evidence laneから必要なレーンだけ選ぶ。repo / external laneには可能なら親が採取済みのartifactを渡す。外部laneは公式docs、upstream source、issue、release noteを優先し、一般的な類似談よりローカルの再現evidenceを優先する。

runtime laneがcommandを実行する場合は、独立worktree、temp、cache、port、DB等へ隔離する。隔離できない共有stress harnessは親agentだけが所有して直列実行し、workerはそのartifactを分析する。

## 統合

- 結論の多数決をしない。
- 矛盾する仮説を区別できる最小probeを1つ選ぶ。
- loop未確立なら候補から次の再現probeを選ぶ。確立後は全workerの候補を同じred/green commandで評価し、read-only調査結果だけで修正済みとしない。
- 原因が絞れたら並列調査を停止し、単一writerへ渡す。

## 拡張条件

現在のレーンで収束せず、component、OS、version、service、log partition等の新しい独立軸が実在する場合だけ追加workerを起動する。固定数を埋めるために10体へ増やさない。

追加を止める条件:

- 最初の逸脱点が判明した
- 2種類以上の独立evidenceが同じ因果鎖を支持した
- 主要な対立仮説をprobeで否定した
- 新しいworkerが新しいevidenceを返さなくなった
- 修正候補を共通loopで検証できる

raceや性能の実験は、CPU、port、cache、DB等の競合が症状を変え得る。分析は並列化しても、benchmarkや共有環境の実験は隔離または直列化する。すべての実験にtimeoutとprocess-tree cleanupを付ける。
