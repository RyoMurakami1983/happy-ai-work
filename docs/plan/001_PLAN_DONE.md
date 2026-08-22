# PLAN 001

## GOAL

公式`happy-ai-work`のConstitution正本、同期・改訂・評価統治、public downstream境界を文書・validator・skill behaviorとして実装し、固定済み未見scenarioで独立評価する。

## Success Criteria

- 正本、summary、判断プロファイル、同期record、ADR、用語が責務分離される。
- drift 3日／7日／10日とremediation exceptionが機械検証できる。
- `skill-eval`と`improvement-loop`が評価改ざんと無断amendmentを防ぐ。
- 固定済み5 scenarioのCritical要件を独立評価で全通過する。
- 全品質commandとCIが成功する。

## Out of Scope

- GitHub profile READMEとhome設定の変更
- private eval実dataの収集・公開
- 新しい公開skill、固定agent、hard hookの追加

## Progress

- [x] Bootstrap / 前提確認
- [x] Slice 1: Constitution参照構造を読むだけで判断できる
- [x] Slice 2: driftとschema違反をvalidatorで検知できる
- [x] Slice 3: skillがamendmentと評価recordを正しく扱う
- [x] Slice 4: 固定scenarioを独立評価する
- [x] Completion handoff

## Design Artifacts / Fixed Decisions

- `CONSTITUTION.md`が公式upstream正本、GitHub profile READMEが個人philosophy。
- `docs/CONSTITUTION_SUMMARY.md`、`docs/governance/UPSTREAM_DECISION_PROFILE.md`、`docs/governance/constitution-sync.json`へ適用層を分離する。
- 共通安全境界はdownstreamで緩和不可。upstream固有価値はdownstreamへ暗黙適用しない。
- hookで修復経路を塞がず、CIとagent判断で公式mergeを制御する。
- 評価scenarioは`evals/constitution/001_SCENARIOS.md`で実装前固定済み。

## Behavior List

- [x] AIが正本とsummaryから通常改善／amendment／停止を区別できる。
- [x] profile revisionまたはConstitution versionの未照合をdriftとして検知する。
- [x] 3日警告、7日merge制限、10日hard stopを判定する。
- [x] sync／remediationをhard stopの例外として説明する。
- [x] 評価A／B／Cと過去record非改ざんをskillが適用する。
- [x] downstream Constitution不在時にupstream固有価値を暗黙適用しない。
- [x] secret、個人経歴、private evalをpublic成果物へ混入させない。

## Vertical Slices

### Slice 1: Constitution参照構造を読むだけで判断できる

- Type: AFK
- Depends on: なし
- Done: 正本、summary、profile、sync record、README／AGENTS／ARCHITECTURE導線、用語が整合する。
- Test surface: `tests/test_constitution_contract.py`の文書contract
- First test: 正本とsummaryがversion、所有者、改訂、downstream、A／B／C、drift境界を公開すること。
- RED command: `python -m unittest tests.test_constitution_contract -v`
- RED expectation: 正本・summary・governance artifactが未作成のため失敗する。
- GREEN command: `python -m unittest tests.test_constitution_contract -v`
- Acceptance command: `python scripts/validate_repo.py`
- Out of scope: remote GitHub API取得、skill behavior評価。

### Slice 2: driftとschema違反をvalidatorで検知できる

- Type: AFK
- Depends on: Slice 1
- Done: local schema検証とremote revision比較、3／7／10日判定をunit test可能なpure functionとして実装する。
- Test surface: `scripts/validate_constitution.py` CLIと`tests/test_constitution_validator.py`
- First test: drift age 3、7、10日の境界値とremote取得不能B。
- RED command: `python -m unittest tests.test_constitution_validator -v`
- RED expectation: validator moduleが未作成のため失敗する。
- GREEN command: `python -m unittest tests.test_constitution_validator -v`
- Acceptance command: `python scripts/validate_constitution.py`
- Out of scope: remote stateを変更する処理、hard hook。

### Slice 3: skillがamendmentと評価recordを正しく扱う

- Type: AFK
- Depends on: Slice 1
- Done: `skill-eval`と`improvement-loop`がConstitution resolution、基準version固定、A／B／C、過去record、drift gateを責務内で扱う。
- Test surface: skill validator、repo contract test
- First test: skillが事後緩和禁止、vNext、record非改ざん、通常改善との区別を含むこと。
- RED command: `python -m unittest tests.test_constitution_contract -v`
- RED expectation: 現行skillにgovernance contractがないため失敗する。
- GREEN command: `python -m unittest tests.test_constitution_contract -v`
- Acceptance command: 公式`quick_validate.py`を変更した各skillへ実行する。
- Out of scope: 新skill作成、plugin manifest変更、plugin再install。

### Slice 4: 固定scenarioを独立評価する

- Type: AFK
- Depends on: Slice 1, Slice 3
- Done: 独立subagentがrubricを見ずに5 scenarioへ回答し、parent判定でCritical全通過・禁止0件となる。
- Test surface: `evals/constitution/001_SCENARIOS.md`と保存した結果record
- First test: scenario 1〜4を独立実行し、収束後にhold-out scenario 5を実行する。
- RED command: 静的commandなし。独立subagent初回responseをbaselineとする。
- RED expectation: Critical未達があれば同じscenarioを維持して最大2回修正する。
- GREEN command: 独立subagent再実行とparent rubric判定。
- Acceptance command: Critical全通過、禁止0、should-not-amend誤起動0を結果recordで確認する。
- Out of scope: rubric変更、private eval data、外部write。

## Order Rationale

- 読める正本をtracer bulletにし、そのcontractからvalidatorとskill behaviorを派生させる。
- deterministic testを独立AI評価より先にgreenにし、behavior評価を機械検証の代替にしない。
- hold-outは修正に使わず、収束時だけ実行する。

## Risks / Unknowns

- GitHub API障害時はremote checkが判定不能Bになる。
- profile revisionは実装時の最新commitを固定する必要がある。
- skill変更が重要behavior変更に該当するため独立評価を省略できない。

## Artifacts

```yaml
artifacts:
  - docs/grill_results/001_CONSTITUTION_GRILL_WITH_DOCS_RESULT.md
  - docs/design/001_TECHNICAL_DESIGN.md
  - docs/plan/001_PLAN_DONE.md
  - docs/adr/0001-constitution-authority-and-governance.md
  - evals/constitution/001_SCENARIOS.md
```

## Return Conditions

- FAIL: 同じsliceでimplementationまたはtestを修正する。
- REPLAN_REQUIRED: 責務境界変更はtechnical-design、価値判断不足はinterview-with-docsへ戻す。
