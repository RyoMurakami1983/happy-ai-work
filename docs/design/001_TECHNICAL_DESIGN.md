# Technical Design 001: Constitution authority and evaluation governance

## Goal / Success Criteria / Out of Scope

### Goal

個人philosophyを全文複製せず、公式`happy-ai-work`が自律判断に使うversion付きConstitutionと、public利用先が自身のphilosophyを所有できる統治構造を作る。

### Success Criteria

- canonical Constitution、日常summary、判断プロファイル、同期record、用語、ADRの責務が分離される。
- 通常改善とConstitution amendment、評価A／B／C、過去recordと再評価を区別できる。
- GitHub profile READMEとupstream Constitutionのdriftを3日／7日／10日境界で検知できる。
- driftや非互換時もremediation pathを塞がない。
- skillが評価基準の事後緩和とupstream価値観のdownstream暗黙適用を防ぐ。

### Out of Scope

- GitHub profile READMEの変更
- 旧philosophy全文・個人経歴の複製
- private evalの実data保管機構
- Copilot固有agent、instructions、authoring構造
- filesystem編集を禁止するhard hook

## Current Structure

- `CONTEXT.md`はMission、product boundary、運用語彙を持つが、Constitution語彙と参照構造がなかった。
- `docs/ARCHITECTURE.md`はCodexのinstruction／skill配置を定義する。
- `skill-eval`はscenarioとcritical要件の事前固定を求めるが、Constitution version、過去record、緊急例外を扱わない。
- `improvement-loop`はskill変更時のbaseline固定を求めるが、通常改善とamendment、drift gateを扱わない。
- CIはrepo validator、unit test、Ruff、secret scanを実行する。

## Structure Decisions

1. Root `CONSTITUTION.md`を公式upstream Constitutionの正本にする。個人philosophyはGitHub profile READMEを参照し、全文を複製しない。
2. `docs/CONSTITUTION_SUMMARY.md`をAIの日常参照入口にする。正本と競合した場合は正本を優先する。
3. `docs/governance/UPSTREAM_DECISION_PROFILE.md`へinteraction topologyと文脈依存の重みを置く。原則本文へ数値を埋め込まない。
4. `docs/governance/constitution-sync.json`へprofile revision、Constitution version、照合日時、drift状態、resolutionを置く。
5. `scripts/validate_constitution.py`はlocal構造検証を常時行い、`--check-remote`時だけGitHub APIでprofile revisionを確認する。
6. `skill-eval`と`improvement-loop`だけを最小更新する。Constitution本文をskillへ複製せず、downstream resolutionと評価不変条件を各skillの責務内で参照する。
7. `evals/constitution/`をpublicなupstream evalの保存先とする。利用者private evalはrepo外または利用者管理の非公開領域に置く。

## Public Interfaces

### `CONSTITUTION.md`

- `Version`
- `Effective date`
- `Owner`
- 共通安全・評価整合性
- upstream原則
- amendment、drift、評価、downstreamの統治境界

### `constitution-sync.json`

```json
{
  "schema_version": 1,
  "constitution_version": "1.0.0",
  "constitution_sha256": "<sha256>",
  "personal_philosophy": {
    "url": "https://github.com/RyoMurakami1983/RyoMurakami1983/blob/main/README.md",
    "revision": "<commit-sha>",
    "committed_at": "<ISO-8601>"
  },
  "reconciled_at": "<ISO-8601>",
  "drift_started_at": null,
  "drift_source": null,
  "resolution": "reflected|not-applicable|pending",
  "reason": "<short rationale>"
}
```

### Validator CLI

```text
python scripts/validate_constitution.py [--check-remote]
```

- 0〜3日未満: success
- 3〜7日未満: warning、exit 0
- 7日以上: release／merge restriction、exit 1
- 10日以上: hard-stop diagnostic、exit 1
- remote取得不能: 判定不能Bとしてexit 1（`--check-remote`時のみ）

## State / Data Flow

1. profileまたはConstitutionに意味変更が入る。
2. profile revisionの不一致、または`resolution: pending`で表したConstitutionの未照合変更をdriftとする。pendingが`constitution`／`both`なら、直前に照合済みのhashを保持したまま現在fileとの差分を許容する。
3. profile側driftの開始時刻は最古の未照合commitの日時を使う。Constitution側は照合済みcommit SHA以後の最古commit日時とsync recordの開始日時の古い方を使い、後続変更や同一contentへのrevertで時計をresetしない。
4. Happyまたは所有者が差分を比較し、`reflected`または`not-applicable`と理由を記録する。
5. amendmentならvNext draft、旧基準との影響比較、所有者承認を経てversionを更新する。
6. 評価recordは使用versionを保持し、再評価は別recordとして追加する。

## Security Boundaries

- secret、顧客情報、非公開業務dataをConstitution、upstream eval、sync recordへ入れない。
- remote checkはpublic GitHub APIのprofile README commit情報だけを読む。
- downstream Constitutionはupstream固有価値を置換できるが、共通安全・評価整合性は緩和できない。
- 非互換時も同期、調査、修復、safe rollback、緊急安全対応を許可する。
- hookでConstitutionやvalidatorの編集を禁止しない。

## Compatibility / Migration

- `CONTEXT.md`の既存Missionと運用語彙は保持し、governance用語だけを追加する。
- pluginは新skillを追加せず、既存skillの責務内で参照を増やすためmanifest構造は変えない。
- plugin再installはsource validationと独立評価に不要。公開後は通常のplugin updateで配布する。
- downstreamにConstitutionがなければ、既存`AGENTS.md`／Mission／policyと共通安全境界だけを使う。

## Alternatives and Trade-offs

- GitHub profile READMEだけを唯一正本にする案は、Happy固有の実益変更とpublic downstreamを扱えないため却下。
- repoへ個人philosophy全文を置く案は、重複、個人情報、同期負担のため却下。
- filesystem mtime比較はclone／checkoutで不安定なため却下。
- fork利用者にupstream eval削除を求める案は、更新衝突と消し忘れを招くため却下。
- 強いhook lockはremediation主体まで排除するため却下。

## Risks / Unknowns

- GitHub API障害時はremote driftを判定できない。判定不能Bとして理由を明示し、local remediationを継続する。
- 数値profileは偽の精密さを招くため、anchor、具体例、理由を必須にする。
- 公開upstream evalが実装へ過適合しないよう、未見scenarioは実行前に固定し独立実行者へ渡す。

## ADRs

- `docs/adr/0001-constitution-authority-and-governance.md`

## Artifacts

- `docs/grill_results/001_CONSTITUTION_GRILL_WITH_DOCS_RESULT.md`
- `docs/design/001_TECHNICAL_DESIGN.md`
- `docs/adr/0001-constitution-authority-and-governance.md`
