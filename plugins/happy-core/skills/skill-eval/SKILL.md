---
name: skill-eval
description: 既存skillや再利用promptの実際の振る舞いをrealistic scenarioで評価し、baseline／current比較、誤起動・未起動、曖昧さ、回帰を証拠として残す。skillの作成ではなく、公開前や大幅変更後のbehavioral evaluationで使う。
---

# Skill evaluation

skillの文章を好みで採点せず、期待する起動、期待しない起動、成果物の要件を固定して挙動を比較する。新規作成・通常の更新は公式`skill-creator`へ任せる。

## ワークフロー

1. 評価する問いを一つに絞る。trigger精度、workflow遵守、成果物品質、旧版との差、曖昧さを混ぜない。
2. typical scenario、edge case、should-not-triggerを含む2〜5件のpromptを用意する。
3. scenarioごとにcritical要件、通常要件、禁止事項、観測方法を実行前に固定する。
4. 可能なら白紙の別task／独立実行者へ、対象skill、scenario、必要最小限のartifactだけを渡す。利用できなければ独立性不足を明示し、静的reviewをbehavioral評価と呼ばない。
5. 要件達成、誤起動／未起動、裁量補完、余分な手順、失敗理由を記録する。
6. 旧版と比較する場合は同じscenarioと判定基準を使い、一度に一つの変更テーマだけ評価する。
7. 修正が必要なら公式`skill-creator`へ戻し、同じscenarioを再実行する。

複数iteration、hold-out、過適合確認が必要な重要skillでは[prompt-evaluation.md](references/prompt-evaluation.md)を読む。

## 停止条件

- critical要件が満たされ、should-not-triggerで誤起動しない。
- 新しい重大な曖昧さが連続した再評価で出ない。
- 改善幅が小さくなり、追加複雑性が利益を上回らない。
- 評価コストがskillの重要度に見合わない場合は、残存riskを記録して止める。
