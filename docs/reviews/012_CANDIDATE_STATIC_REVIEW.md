# 012 — implement候補の静的契約保持レビュー

日付: 2026-10-03。baseline: `ab32391c9612ad7983a4805040a6331ad5f576db`。
対象: `evals/openai-first-implement/candidate/implement/`。
Reviewer: `candidate-reviewer-01`（候補作成担当とは別のread-only reviewer）。

## 範囲と結論

**静的契約保持: PASS。実行helper構成の補足確認: PASS。**

既存instructions、Constitution、`docs/design/012_COMPARATIVE_PILOT.md`、固定baseline、候補本文と参照先を比較した。共有filesystem上の静的レビューであり、blindな行動比較、モデルの実行結果、採点の妥当性、実利用効果、採用可否は検証していない。reviewerはprivate評価内容を読まず、比較trialを実行せず、候補を編集していない。

## Review v1 — 意味と参照の保持

重大な契約欠落は見つからなかった。確認先は以下。

| 契約 | 候補での確認先 |
| --- | --- |
| 安全、実装開始の明示許可、同じ範囲・工程省略の許可、設計への賛意を実装許可にしない | `SKILL.md:14–20` |
| 対象sliceに必要なbootstrapのみ、検証通知と承認の再確認を区別 | `SKILL.md:26–31`、`references/verification-communication.md:3–9` |
| plan境界、順次slice、RED→最小GREEN→REFACTOR、public interface、system boundaryのみのmock、docs/config-onlyの正直な代替検証 | `SKILL.md:35–45,49–59` |
| artifactの実在、conversation-only制限、finalized_contractのsource追跡、exclusion残骸確認、未決・変更decisionのreplan | `references/task-contract.md:7–28` |
| 独立評価へのcontract・差分・証拠、評価者は修正しない、評価中の並列実装禁止、単一writerの修正 | `SKILL.md:55` |
| 実runtime観測、HITL milestone、acceptance依存HITLの保留、到達状態の区別 | `SKILL.md:57,65`、`references/interactive-gates.md:7–34` |
| 完了証拠、source対応、残件、plan rename、blockerのない工程間は継続 | `SKILL.md:59,63–67` |

long-lived structureとcompatibilityの省略制限は、baselineが参照していたWork Artifactsの既存制約を保持するもの。戻り先skillが未導入の場合は判断を創作せず、不足と再開条件をhandoffする。

初回は13個の保持resourceのbyte一致、20個のlocal Markdown linkの解決、plan templateとcheckpointの包含を確認した。ただし、**この初回PASSは未参照の実行helperを含むtool inventoryの同一性を確認していなかった**。

## Review v2 — 実行helper構成の補正

親担当の確認で、baselineの`orchestrator/__init__.py`と`orchestrator/fleet_orchestrator.py`の欠落が判明した。本文・referenceだけを変え、tool surfaceを同一にする比較に対しては交絡となるため、初回の依存解決PASSを完全な構成保持と解釈しない。

両fileをbaselineからbyte同一で復元し、provenanceに追加した。reviewerが復元fileとprovenanceを再確認し、**この補正に限定してPASS**とした。baselineと候補は同じ4つのPython helper/package pathを持つ。

`tests/test_lean_implement_candidate.py`の`test_executable_surface_is_unchanged_from_baseline`はPython fileのpath集合と各fileのbyte一致を確認する。実装担当は復元前のFAILを確認し、復元後に12件のfocused testsがPASSした。reviewerはtestの内容を検査したが、実行結果の再実行はしていない。

helper削除によるpackage縮小をlean効果として数えない。本文の長さが変わったこと自体も、行動・品質・人の負担の改善証拠にしない。PyYAMLは既存checkpointの外部依存のままであり、可搬packageはhermetic runtimeを意味しない。

## 最終対象hash（SHA-256）

以下は`evals/openai-first-implement/candidate/`からの相対path。

| 対象 | SHA-256 |
| --- | --- |
| `implement/SKILL.md` | `ec61c34e7c41852697865781dc3eab8bc05ef8d5f9b3729bfd19666e438bf3d7` |
| `implement/references/task-contract.md` | `32383b31a5927b139cf031bb86d6a22c7b75c595677a8229f90b332ef13b10c7` |
| `implement/references/interactive-gates.md` | `7bcfc272feca8d6d13c0af4a74b540eac4e6014ef9234397e5d16d1590444c44` |
| `implement/orchestrator/__init__.py` | `10926f0f43062e9afca70d1e1091378ca28bf4f7fcf1c1a8100f1b6fbbd86b56` |
| `implement/orchestrator/fleet_orchestrator.py` | `aaa11e14ba498315e5605f936953a5a225ffa1faf14da2b300bcebca42dc29c9` |
| `provenance.json` | `5055e543faab2d263897a2e494a24f5e45ce4208ce693bcf4b6e3fc0a1b7915e` |

保持resourceは最終版で15個。本文・条件付き新規referenceは3個。配布pluginとversionは変更していない。

## 実装担当の決定的検証と残るgate

- `python -m unittest discover -s tests -p test_lean_implement_candidate.py -v`: 12 PASS（Python 3.12.14でのfocused検証）
- 公式skill-creatorの`quick_validate.py`: PASS
- repo validator、canonical Python 3.14 quality、全体の差分review、両OS CIは親担当の最終検証へ接続する
- 実行model・予算・権限・事前登録・アクセス分離・独立採点の実比較gateは未充足のまま。この文書はそれらを解除しない

固定したactual comparisonと実利用確認が済むまで、候補は未採用であり、現行配布物を維持する。
