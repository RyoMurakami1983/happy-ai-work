# Parallel Investigation

debugの並列調査は、再現条件を固定した後の証拠収集・仮説検証を速めるために使う。

## 起動条件

次をすべて満たす場合に使う。

- 症状を判定する共通のred/green commandがある。
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

repo lane、runtime lane、external evidence laneの最大3つから始める。repo / external laneには可能なら親が採取済みのartifactを渡す。外部laneは公式docs、upstream source、issue、release noteを優先し、一般的な類似談よりローカルの再現evidenceを優先する。

runtime laneがcommandを実行する場合は、独立worktree、temp、cache、port、DB等へ隔離する。隔離できない共有stress harnessは親agentだけが所有して直列実行し、workerはそのartifactを分析する。

## 統合

- 結論の多数決をしない。
- 矛盾する仮説を区別できる最小probeを1つ選ぶ。
- 全workerの候補を同じred/green commandで評価する。
- 原因が絞れたら並列調査を停止し、単一writerへ渡す。

## 拡張条件

最初の3レーンで収束せず、component、OS、version、service、log partition等の新しい独立軸が実在する場合だけ追加workerを起動する。固定数を埋めるために10体へ増やさない。

追加を止める条件:

- 最初の逸脱点が判明した
- 2種類以上の独立evidenceが同じ因果鎖を支持した
- 主要な対立仮説をprobeで否定した
- 新しいworkerが新しいevidenceを返さなくなった
- 修正候補を共通loopで検証できる

raceや性能の実験は、CPU、port、cache、DB等の競合が症状を変え得る。分析は並列化しても、benchmarkや共有環境の実験は隔離または直列化する。すべての実験にtimeoutとprocess-tree cleanupを付ける。
