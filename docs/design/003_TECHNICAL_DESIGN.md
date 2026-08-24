# Technical Design 003: Instruction finalization gate

## Goal / Success Criteria / Out of Scope

Issue #17の採用案以外の議論が、AGENTS.md、SKILL.md、references、README、実装、testへ恒久契約として混入する問題を、工程ごとに責務の異なる多層防御で防ぐ。

成功条件:

- `AC17-DECISION-SEPARATION`: 採用済みcontract、decision history、Non-goals／Unknownsを分離できる。
- `AC17-NORMATIVE-HANDOFF`: 後続工程がfinalized contractの規範部分だけを実装根拠として扱う。
- `AC17-TRACEABILITY`: 恒久成果物の主要な追加をAcceptance Criteria、採用decision、既存の恒久repo規約、外部contract、安全invariantへ追跡できる。
- `AC17-DURABLE-PLACEMENT`: AGENTS.md、SKILL.md、reference、README、実装、testへ一時事情や非採用案の制約を持ち込まない。
- `AC17-HISTORY-BOUNDARY`: decision historyをdesign／ADRに隔離し、実行規約と区別する。
- `AC17-BIDIRECTIONAL-REVIEW`: 実装diffとDeepReviewが、誤混入と必要制約の欠落を対称に検出する。
- `AC17-WRAPPER-SCENARIO`: wrapper案からrepo-local案へ決定を変えるscenarioでlocator等の混入を検出する。
- `AC17-OVER-MINIMIZATION`: 採用案にも必要なconstraintの過剰削除を検出する。
- `AC17-BASELINE-CURRENT`: 同じscenarioと基準でbaseline／currentを比較し、sanitize済みrecordを残す。
- `AC17-LIGHTWEIGHT-NEAR-MISS`: 単純な局所変更へ重いfinalization artifactを強制しない。

対象外:

- 会話やIssueから非採用案を削除すること。
- 禁止語の文字列testだけで意味的混入を判定すること。
- 全skill、README、workspace template、言語別referenceへ規則を複製すること。
- ADRから価値のある判断理由を削除すること。

## Current Structure

- `technical-design`は採用案、却下案、理由、riskと実装handoffを所有するが、規範入力とdecision historyの分離contractがない。
- `implementation-plan`はAcceptance Criteriaをbehaviorへ対応付けるが、恒久成果物へのsource traceを要求しない。
- `implement`は契約を必要十分に圧縮し、不要抽象化をslice gateで見るが、非採用案の意味的残骸を明示的には確認しない。
- `deep-review`はdiffと要件を独立確認するが、instruction finalization固有の出口観点がない。
- `skill-eval`と`evals/`にはbaseline/current、public case、sanitize済みappend-only recordの既存基盤がある。

## Structure Decisions

1. `technical-design`をDecision Resolution Gateの主所有者とする。複数案を実質的に比較した場合、決定が途中で変わった場合、または恒久instruction／testへ案固有の制約が入り得る場合だけ、条件付きreferenceを読む。
2. finalized contractは`normative`、`exclusions`、`unknowns`、`target_traceability`を持つ。規範sourceはAcceptance Criteria、採用decision、既存の恒久repo規約、採用案から独立して必要な外部／安全invariantに限る。
3. 非採用案は必要な場合だけdesign／ADRへdecision historyとして残し、implementation handoffへ詳細を再展開しない。Non-goalは今回のscope外であり、別途採用されない限り恒久禁止ではない。
4. `implementation-plan`はfinalized contractのconsumerとして、各sliceと主要な恒久targetをnormative sourceへ対応付ける。根拠不明なら`technical-design`へ戻す。
5. `implement`はfinalization contractがあるsliceに限ってactual diffを確認する。除外案由来の文言だけでなく、責務、抽象化、validation branch、test seamも残骸として扱う。必要な採用constraintの欠落も同じgateで確認する。
6. `deep-review`は決定を作り直さず、diffからsourceへ遡れない恒久規範、除外案由来の残骸、採用constraint欠落を独立して指摘する。
7. static validatorはschema、link、path等の決定論的契約だけを扱い、意味的混入はbehavioral evalで判定する。
8. root `AGENTS.md`には、このupstream repo自身で恒久実行規約を編集するときの短い不変条件だけを置く。詳細workflowは複製しない。

## Public Interfaces

technical-design handoffの条件付きblock:

```yaml
finalized_contract:
  normative:
    - AC-1
    - DEC-REPO-LOCAL
    - POLICY-HOME-SAFETY
  exclusions:
    - id: ALT-WRAPPER
      status: rejected
    - id: NG-HOME-BOOTSTRAP
      status: non-goal
  unknowns: []
  target_traceability:
    plugins/example/SKILL.md:
      sources:
        - AC-1
        - DEC-REPO-LOCAL
      placement_reason: 議論を知らない実行者も採用済みworkflowを再現するため
  exclusion_policy:
    rejected: 別途negative requirementとして採用されない限り恒久禁止ではない
    non-goal: 今回のscope外であり恒久禁止ではない
```

小さく明白な単一変更、比較案がない変更、恒久instructionを変更しない変更では、このblockを強制しない。

## Implementation Handoff

```yaml
finalized_contract:
  normative:
    - AC17-DECISION-SEPARATION
    - AC17-NORMATIVE-HANDOFF
    - AC17-TRACEABILITY
    - AC17-DURABLE-PLACEMENT
    - AC17-HISTORY-BOUNDARY
    - AC17-BIDIRECTIONAL-REVIEW
    - AC17-WRAPPER-SCENARIO
    - AC17-OVER-MINIMIZATION
    - AC17-BASELINE-CURRENT
    - AC17-LIGHTWEIGHT-NEAR-MISS
    - DEC-FINALIZATION-GATE-OWNERSHIP
    - POLICY-INSTRUCTION-PROMOTION
    - SAFETY-EVALUATION-INTEGRITY
  exclusions:
    - id: ALT-EARLY-DISCARD
      status: rejected
    - id: ALT-DEEP-REVIEW-ONLY
      status: rejected
    - id: ALT-DUPLICATE-FULL-RULE
      status: rejected
    - id: NG-STRING-TEST-ONLY
      status: non-goal
  unknowns: []
  target_traceability:
    AGENTS.md:
      sources:
        - POLICY-INSTRUCTION-PROMOTION
        - AC17-TRACEABILITY
        - AC17-DURABLE-PLACEMENT
      placement_reason: 議論を知らないcontributorも恒久instructionの昇格条件を守るため
    CONTEXT.md:
      sources:
        - AC17-DECISION-SEPARATION
        - AC17-NORMATIVE-HANDOFF
      placement_reason: 議論を知らない読者も製品用語と工程境界を共有するため
    plugins/happy-coding/skills/technical-design/SKILL.md:
      sources:
        - DEC-FINALIZATION-GATE-OWNERSHIP
        - AC17-DECISION-SEPARATION
        - AC17-NORMATIVE-HANDOFF
      placement_reason: 議論を知らない設計者もfinalization gateを起動して規範handoffを作るため
    plugins/happy-coding/skills/technical-design/references/finalization-contract.md:
      sources:
        - AC17-TRACEABILITY
        - AC17-DURABLE-PLACEMENT
        - AC17-HISTORY-BOUNDARY
        - AC17-OVER-MINIMIZATION
      placement_reason: finalization対象の設計者だけが詳細な分類・昇格・handoff規則を読むため
    plugins/happy-coding/skills/implementation-plan/SKILL.md:
      sources:
        - AC17-NORMATIVE-HANDOFF
        - AC17-TRACEABILITY
      placement_reason: 議論を知らないplannerも規範sourceだけをsliceへ渡し根拠不明時に戻すため
    plugins/happy-coding/skills/implementation-plan/assets/NNN_PLAN_TEMPLATE.md:
      sources:
        - AC17-TRACEABILITY
        - AC17-LIGHTWEIGHT-NEAR-MISS
      placement_reason: finalization対象planだけが主要target traceを同じ形式で保存するため
    plugins/happy-coding/skills/implement/SKILL.md:
      sources:
        - AC17-NORMATIVE-HANDOFF
        - AC17-BIDIRECTIONAL-REVIEW
      placement_reason: 議論を知らない実装者もsliceごとに規範sourceとactual diffを照合するため
    plugins/happy-coding/skills/implement/references/eval-checklist.md:
      sources:
        - AC17-DURABLE-PLACEMENT
        - AC17-OVER-MINIMIZATION
      placement_reason: finalization対象sliceだけが意味的残骸と過剰削除を対称に検査するため
    plugins/happy-coding/skills/deep-review/SKILL.md:
      sources:
        - AC17-BIDIRECTIONAL-REVIEW
      placement_reason: 議論を知らないreviewerも対象diffで独立backstopを起動するため
    plugins/happy-coding/skills/deep-review/references/preflight.md:
      sources:
        - AC17-DURABLE-PLACEMENT
        - AC17-HISTORY-BOUNDARY
        - AC17-OVER-MINIMIZATION
      placement_reason: finalization対象reviewだけが混入・欠落・history境界を詳細確認するため
    evals/instruction-finalization/cases.v1.json:
      sources:
        - AC17-WRAPPER-SCENARIO
        - AC17-OVER-MINIMIZATION
        - AC17-LIGHTWEIGHT-NEAR-MISS
      placement_reason: 改善前後を同じ公開scenarioと基準で再評価するため
    evals/records/instruction-finalization-adoption-004.json:
      sources:
        - AC17-BASELINE-CURRENT
        - SAFETY-EVALUATION-INTEGRITY
      placement_reason: raw transcriptを残さず最終採否の再現可能な要約をappend-onlyで保存するため
  exclusion_policy:
    rejected: 別途negative requirementとして採用されない限り恒久禁止ではない
    non-goal: 今回のscope外であり恒久禁止ではない
```

`DEC-FINALIZATION-GATE-OWNERSHIP`は`docs/adr/0003-finalization-gate-ownership.md`、`POLICY-INSTRUCTION-PROMOTION`はroot `AGENTS.md`、`SAFETY-EVALUATION-INTEGRITY`は`CONSTITUTION.md`と`docs/EVALUATION_ASSETS.md`へ接地する。exclusionの詳細はこのdesignのAlternatives and Trade-offsおよびADR参照に留め、planへ再展開しない。

## State / Data Flow

```text
discussion / candidates
  -> technical-design: accepted / rejected / deferredを確定
  -> finalized contract: accepted sourcesだけを規範化
  -> implementation-plan: source -> slice / durable target
  -> implement: actual diff finalization gate
  -> deep-review: independent semantic backstop
  -> skill-eval: baseline / current adoption evidence
```

## Security Boundaries

- 検討中に見つかった安全constraintは、非採用案で初出したことだけを理由に削除しない。採用案にも独立して必要なら既存policy／外部invariantへ再根拠付けする。
- full discussion transcriptを実装者やreviewerの規範入力にしない。
- public evalへraw response、transcript、sealed hold-outを保存しない。

## Compatibility / Migration

- finalized contractは条件付き追加であり、既存の小規模変更やconversation-only例外を壊さない。
- 既存artifactに遡ってID付与しない。今回以降の対象workflowだけへ適用する。
- plugin間依存は増やさず、`happy-coding`内の既存skill境界を利用する。

## Alternatives and Trade-offs

- 入口で議論を即時削除する案は、必要constraintと判断理由を早計に失うため却下。
- DeepReviewだけに所有させる案は、不要責務やtestが固定された後の修復コストが高いため却下。
- 全skillへ同じ長文を複製する案は、instruction noiseと更新driftを増やすため却下。
- 行単位の完全traceabilityは保守負担が大きいため採用せず、sliceと主要artifact単位の短いsource traceを採用する。

## Risks / Unknowns

- agentがsource IDの形式を過剰に儀式化するriskはshould-not-trigger caseで評価する。
- 文字列を消すだけで意味的なwrapper責務を残すriskはhappy-pathで評価する。
- 短さを最適化して必要な安全constraintを落とすriskはedge caseで評価する。

## ADRs

- `docs/adr/0003-finalization-gate-ownership.md`

## Artifacts

```yaml
artifacts:
  - docs/design/003_TECHNICAL_DESIGN.md
  - docs/adr/0003-finalization-gate-ownership.md
```
