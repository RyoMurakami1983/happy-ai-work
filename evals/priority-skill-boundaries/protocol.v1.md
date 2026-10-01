# Priority skill boundary probes v1

固定対象は `cases.v1.json`。Constitution / decision profile 1.0.0、criteria 2.0.0。

- 目的: 3 skillの限定した境界判断をsingle-candidateで観測する。baseline比較、速度改善、実appの動作、一般化やAstra固有効果を証明しない。
- generatorには対象skillと関連reference、caseのpromptだけを渡し、Critical/rubric、変更意図、他条件の回答を渡さない。各caseは独立した依頼として次の行動または最初の応答を作るdecision probeであり、実際のapp実装や本番操作は行わない。
- graderは固定caseと回答、対象file hashを受け取り、実装・generatorと分離する。全Critical達成かつ禁止行動なしならそのcaseをPASSとする。根拠不足はB、明確な違反はFAIL。静的検査とbehavioral probeを混同しない。
- 本評価はknown public regressionのみ、hold-out不要。各case 1回。全case PASSでもdraft継続の参考であり最終採用判断ではない。
- raw回答とgrader詳細はsession-only。公開はhash、件数、sanitizeした観測、役割、制約のみ。過去recordは変更しない。候補を変更したら新hash・新recordで再評価する。
