# Technical Design 002: Codex-native evaluation assets

## Goal

`skill-eval`と`improvement-loop`で繰り返し使える公開case、versioned schema、append-only comparison record、policy validatorを最小構成で成立させる。旧PrivateEvalの制度上の責務を再分類し、Copilot固有の実行部品は移植しない。

## Legacy classification

| 分類 | 資産／責務 |
| --- | --- |
| Codex向けに再利用 | case設計、happy／near-miss／missing-context、schema、昇格判断、raw禁止、集計履歴、runner／grader／comparatorの役割分離 |
| 現行へ移植済み | baseline／current、typical／edge／negative／hold-out、独立実行、評価governance、A／B／C、Constitution evaluation record |
| 未移植で必要 | canonical public case、case／record schema、公開後非hold-out lifecycle、append-only record policy、禁止path／fieldのdeterministic validator |
| 移植対象外 | Copilot用固定agent群、benchmark sub-skill、viewer HTML、viewer生成、prompt corpus抽出、manual-run materializer、汎用集計runner |
| 現行境界と非互換 | 公開可能caseをprivate evalと呼ぶこと、public caseをsealed hold-outとして再利用すること、raw runをrepo内に永続化すること |

## Minimal structure

```text
evals/
├── schema/
│   ├── case.schema.json
│   └── record.schema.json
├── skill-eval/cases.v1.json
├── improvement-loop/cases.v1.json
└── records/<append-only-record>.json
```

`scripts/validate_evals.py`は標準libraryだけでcase／recordの必須field、version、公開hold-out禁止、参照、禁止path／field、明白なsecret patternを検証する。意味的品質とsanitizeの完全性はAI reviewと人の昇格判断が担う。

## Data flow

1. maintainerがcaseとrubricを実行前に固定する。
2. 条件ごとのgeneratorへpromptと許可contextだけを渡す。
3. responseはsession限定領域に置き、blind labelだけをgraderへ渡す。
4. graderが同一batchを採点し、別の独立reviewerが重要変更を評価する。
5. publicにはsanitize済み集計、必要最小の抜粋またはhashだけを新recordとして保存する。

## Version and change ownership

Constitution、判断プロファイル、評価constitution、case rubricは別versionとして参照する。caseやschemaの意味変更は新version、再評価は新recordとし、過去fileを結果に合わせて書き換えない。Constitution amendment、判断プロファイル変更、評価基準vNext、通常case保守はそれぞれのownerと承認境界へ戻す。

## Rejected scope

pilotに不要なUI、常設service、固定agent、model API wrapper、汎用benchmark frameworkは追加しない。これらがなければ再現不能だという証拠が得られた場合だけ別実験で検討する。

## Responsibility reset: decision evidence and response quality

### Goal / Success criteria / Out of scope

pilot 004〜006で、最終recordに必要な証拠を通常回答の定型文へ転写すると、局所的な欄埋めは改善する一方、mode誤選択、冗長化、別の要件脱落が生じた。以後は完全な文言一致を目的にせず、危険な意思決定を防ぎながら評価recordの追跡可能性と通常回答の自然さを両立する。

成功条件は、独立性の誤表示、過去recordの置換、汚染hold-outによる採用、public raw保存、A／B／C誤用がないこと、最終recordから判断根拠を追えること、通常回答へrecord内部の固定書式を強制しないことである。grader、runner、UI、外部service、全回答の完全一致scoreは対象外とする。

### Structure decisions

評価を二層へ分ける。

1. **Decision invariants**: 独立性、過去record保持、hold-out状態、public sanitize、A／B／C、採用可否など、誤ると評価整合性を壊す境界。違反または禁止行為が一件でもあればbehavior変更を採用しない。
2. **Response quality**: 代替案、説明順、通常要件、簡潔さ、全欄の明示など。coverageと残存riskとして比較し、単発の非安全 omissionだけで直ちに全体を棄却しない。

完全なdecision evidenceの所有者は`evals/records/`のsanitize済み最終recordとする。通常のユーザー向け回答は、その場の判断に必要なinvariantと次の行動を自然文で示す。固定6行templateをpublic interfaceにせず、同じ情報を回答とrecordへ二重管理しない。

### Public interfaces and data flow

最終recordでは、既存の構造fieldへ証拠を対応づける。

| 証拠 | record上の表現 |
| --- | --- |
| hold-out状態 | `conditions`または`gate_results` |
| 独立性と根拠 | `roles`とrole separationの判定 |
| 過去record保持 | `previous_record` |
| 新record | append-onlyな新filenameと`record_id` |
| public sanitize | `retention_decision` |
| A／B／Cと判定 | `mode`と`verdict` |

generatorの通常回答、blind graderの採点、独立evaluatorの判断を経て、公開側にはこの構造へ圧縮したrecordだけを保存する。schemaで表せるfieldを自由文templateへ重複させない。

### Evaluation gate

- Decision invariantと禁止事項は全反復でPASSを必須とする。
- final recordを作るscenarioでは判断証拠を構造的に欠落させない。
- Response qualityはbaseline非劣化、対象改善、保守コストをまとめて判断する。通常要件の単発 omissionは残存riskとして許容できる。
- 同じ失敗へ文言規則を足し続けず、2 iterationで収束しなければ責務または評価設計へ戻る。

### Security boundaries / Compatibility / Trade-offs

raw response、sealed prompt、private evalの公開禁止、独立性、append-onlyは緩和しない。変更するのは判定基準の粒度であり、Constitution原則ではない。criteria vNextとして新case versionと新recordへ適用する。初回commit前の試行pilotは正式履歴と混同せず、採用条件とbaseline instructionを自己完結した初回adoption manifest／recordへ統合する。追跡開始後のversioned case、schema、recordは上書きしない。

固定templateは採点しやすいが、回答を内部ledgerへ寄せて局所過適合を招くため却下する。全Critical完全一致は明快だが、安全性と同じ重みで説明上の単発 omissionを扱うため却下する。代わりにhard invariantの完全通過とqualityの比較判断を組み合わせる。

validatorはlocal dirty worktreeだけでなく、GitHub ActionsではPR baseまたはpush eventの`before` SHAからHEADまでのtracked diffを比較してappend-only違反を検出する。rename／delete／modifyに加えtype changeも拒否する。final record schemaはhold-out、role independence、prior record状態、artifact hash、sanitize retention、mode／verdictを構造fieldとして要求し、artifact pathの実体とSHA-256を照合する。path policyはhyphen区切りを含むsealed／holdout／raw markerを拒否する。baseline instruction variantは要約hashだけにせず、generatorへ渡した公開snapshotを採用manifestとともに保持する。
