---
name: skill-eval
description: 既存skillや再利用promptの振る舞いを実務に即した通常課題・難問で評価し、素のモデルや旧版に対する追加価値、失敗、誤起動・未起動、回帰を証拠として残す。公開前・大幅変更後の検証や、満点続きで差が見えない比較の見直しに使う。skillの作成は扱わない。
---

# Skill evaluation

skillの文章を好みで採点せず、期待する起動、期待しない起動、成果物の要件を固定して挙動を比較する。新規作成・通常の更新は公式`skill-creator`へ任せる。

評価基準のversion、Constitutionとの関係、過去結果の再評価、緊急例外、採用可否、独立再評価を扱う場合は[評価governance](references/evaluation-governance.md)を先に読む。

再利用するcaseの設計、公開昇格、廃止、比較履歴を扱う場合は[公開評価資産](references/evaluation-assets.md)を読む。公開caseをprivate evalまたは未見hold-outと呼ばない。

## ワークフロー

1. 評価する問いを一つに絞る。trigger精度、workflow遵守、成果物品質、旧版との差、曖昧さを混ぜない。
2. まず2〜5件のtypical scenario、実務上の境界・例外・曖昧さを含む難問、should-not-triggerを用意する。比較や難度の予備調整では[prompt-evaluation.md](references/prompt-evaluation.md)の測定設計を先に読み、調整用と未使用の本評価を分ける。低得点や都合のよい差を目標にしない。
3. scenarioごとにcritical要件、通常要件、禁止事項、観測方法と、比較条件・反復数・終了条件を実行前に固定する。
4. 条件ごとに白紙の別task／独立実行者を使い、scenario、必要なartifactとその条件のskillだけを渡す。生成役へrubric・他条件の出力を渡さず、採点役へ条件名を伏せる。実際の入力・環境・skill適用状況を記録する。独立実行が利用できなければ不足を明示し、静的reviewをbehavioral評価と呼ばない。
5. 要件達成、誤起動／未起動、裁量補完、余分な手順、失敗理由を記録する。全skill共通のコミュニケーション品質は[prompt-evaluation.md](references/prompt-evaluation.md)を読み、発言・通知時点と短い判定根拠を残す。未観測を成功へ補完しない。
6. 素のモデルや旧版との比較では同じscenario・環境・判定基準を使い、一度に一つの変更テーマだけ評価する。通常課題と難問の結果を分け、満点続きなら識別力を点検する。差が観測されないだけで同等性を主張しない。
7. 修正が必要なら公式`skill-creator`へ戻す。既知caseで回帰を確認し、未使用caseで追加価値を検証する。調整後の評価は新runとして残す。

評価資産をrepoへ残す場合はraw runではなく、version付きcaseとsanitize済みappend-only recordだけを昇格する。機械判定できるschema、path、field、secret patternはvalidatorへ任せる。

複数iteration、hold-out、過適合確認が必要な重要skillでは[prompt-evaluation.md](references/prompt-evaluation.md)を読む。

## 停止条件

- critical要件が満たされ、should-not-triggerで誤起動しない。
- 新しい重大な曖昧さが連続した再評価で出ない。
- 改善幅が小さくなり、追加複雑性が利益を上回らない。
- 評価コストがskillの重要度に見合わない場合は、残存riskを記録して止める。
