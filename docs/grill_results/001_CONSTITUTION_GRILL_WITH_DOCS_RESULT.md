# Constitution 再確立 grill result

Tracking: GitHub Issue #12

## 目的

個人のphilosophy、HappyのConstitution、repo固有のMission、運用policy、評価constitutionを分離し、所有者が常時同席しなくても通常改善とConstitution改訂を区別できる統治境界を確立する。

## 確認済み資料

- 現行 `CONTEXT.md`、`README.md`、`docs/ARCHITECTURE.md`、関連skill
- 旧 `happy_ai_life/docs/PHILOSOPHY.md`
- 旧 `happy_ai_life/docs/PHILOSOPHY_SUMMARY.md`
- 旧 `happy_ai_life/CONTEXT.md`
- 旧 `happy_ai_life/docs/adr/instruction-hierarchy-and-authoritative-source.md`
- GitHub profile `RyoMurakami1983/RyoMurakami1983` の現行README

## 重要な判断軸

- 独立性と評価結果の改ざん耐性
- 人の曖昧さを許容できる継続可能な同期
- 個人情報と重複の最小化
- 後から根拠と基準versionを再現できること

## 決定ログ

### 2026-08-22: 正本を単一文書へ固定しない

**利用者の回答**：個人philosophyとHappy側の文書はどちらも変化し得る。基本的なVision／Missionは変わりにくいが、実益のためHappy側だけを先に直す場合もある。片側の更新を忘れる人の曖昧さを仕組みで補い、更新時刻が3日以上ずれた場合は警告する運用が望ましい。

**現時点の解釈**：個人philosophyとHappy Constitutionは、同一内容のmirrorではなく責務の異なるliving documentsとする。一方を常に他方へ自動上書きするのではなく、意味のある変更が片側だけにある状態をdriftとして検知し、人へ同期判断を促す。

**未確認事項**：3日判定の起点、同期判断の所有者、意図的な片側変更を許容する記録方法、衝突時の優先順位。

### 2026-08-22: driftは段階的に制限し、10日以上で停止する

**利用者の回答**：3日を超えた更新差は警告とし、10日以上ずれた場合は停止する。それまでにも段階的に実行できないことを増やしたい。

**現時点の解釈**：通常作業を直ちに全面停止するのではなく、drift ageに応じてgovernance上の変更権限を縮小する。少なくとも10日目には未解決driftを放置したまま進めないhard stopを設ける。

**未確認事項**：各段階で禁止する操作、hard stopの対象範囲、安全修正などの例外、drift解消を承認する所有者。

### 2026-08-22: 安全対応はhard stopより優先する

**利用者の回答**：段階制限案を採用し、安全を最優先とする。

**合意した段階**：0〜3日未満は通常運用。3〜7日未満は警告し、driftを拡大するphilosophy／Constitution／評価基準の採用を禁止する。7〜10日未満はbehavior変更を伴うskill・pluginのrelease／mergeも禁止する。10日以上はread-only調査、同期作業、緊急安全対応以外を停止する。

**例外境界**：10日以降も、secret漏洩や破壊被害の封じ込めなど、遅延が被害を増やす安全対応は許可する。通常の機能修正、利便性向上、評価緩和を緊急安全対応へ分類してはならない。

**未確認事項**：driftの機械的な測定方法、drift解消を承認する所有者、原則衝突時の扱い。

### 2026-08-22: 同期判断の所有者は具体例で再確認する

Happyが単独で「個人philosophyへの反映不要」と判断できる範囲を質問したが、抽象的で理解しにくいとの回答を得た。運用手順の追加と価値観の変更を対比する具体例へ分解して再確認する。

### 2026-08-22: 価値観変更は利用者の明示判断を必須とする

**利用者の回答**：観測項目の追加のような価値観を変えない運用改善はHappyが判断してよい。価値観を変更するときは村上さんへ確認する。

**決定**：Happyは現行Constitutionの範囲内で通常の運用改善と「個人philosophyへの反映不要」の同期判断を行える。原則の追加・削除・優先順位変更はConstitution amendmentであり、所有者の明示判断なしに採用できない。

### 2026-08-22: amendmentはdraftと承認を分離する

**利用者の回答**：価値観変更は、Happyがdraftを書き、利用者と壁打ちして固め、承認後に修正を有効化する。

**決定**：変更要求だけでは現行Constitutionを置き換えない。旧基準との影響比較を持つvNext draftを作り、対話で確定し、所有者の明示承認後に新versionとして有効化する。承認までは現行versionを適用する。

### 2026-08-22: 過去の評価結果は基準versionとともに保存する

**利用者の回答**：当時の判断を尊重しつつ、再評価結果も継続性として評価する。履歴やログから観点・視点の変更が見えることは有益である。

**決定**：評価基準を正当に改訂しても、旧versionで得た結果を上書きしない。旧結果と新versionでの再評価を別recordとして保存し、基準と結果の変化を追跡可能にする。

### 2026-08-22: 不明を認め、緊急判断を隠さない

**利用者の回答**：曖昧な基準をその場の感覚で決めると、判断能力低下、見落とし、失敗を招くため、余裕があれば判定不能として証拠付きで閉じ、後日明確な別評価を行う。納期などで緊急に判断する現実は否定しないが、緊急判断だったことを判別可能にする。分類は複雑化を避け、最大3軸とする。

**現時点の解釈**：通常判定、判定不能、緊急例外の3 modeに限定する。緊急例外は通常のPASSに偽装せず、後日の再評価対象として残す。

**未確認事項**：3 modeの名称と、緊急例外に最低限必要な記録項目。

### 2026-08-22: 評価modeを3つに限定する

**決定**：評価modeはA「通常評価」、B「判定不能」、C「緊急例外」とする。Aだけが通常のPASS／FAILを返す。Bは証拠付きで停止して後日vNextで再評価する。Cは暫定判断であり、通常PASSへ偽装せず、理由と再評価期限を残す。

### 2026-08-22: 緊急例外の選択権限を理由で分ける

**決定**：secret漏洩や破壊被害など、安全被害を止めるための緊急例外CはHappyが自律的に選べる。納期や利便性を理由にCを選ぶ場合は、リポジトリ所有者の明示承認を必須とする。

### 2026-08-22: 公開利用者へ個人philosophyを強制しない

**利用者の問題提起**：`happy-ai-work` とHappyはpublicであり、clone／fork／plugin利用者が村上さん個人のphilosophyに固定されるのは不適切である。利用先のphilosophyに従える境界が必要である。

**確認済み意図**：今回のupstream repoについては村上さんがConstitution amendmentと納期理由の緊急例外を明示承認する。

**未確認事項**：public distributionで不変にする安全・評価整合性と、downstream所有者が置換できる価値観の境界。Constitution探索時の優先順位。

### 2026-08-22: Constitutionを3層に分ける

**決定**：publicなHappyは、(1) 利用者が緩和できない安全・評価整合性、(2) 村上さんのphilosophyを公式`happy-ai-work`の判断へ翻訳したupstream Constitution、(3) clone／fork／plugin利用先の所有者が自分のphilosophyと優先順位を定義するdownstream Constitution、の3層を区別する。downstreamはupstreamの価値観を置換できるが、安全・評価整合性は維持する。

### 2026-08-22: downstream Constitutionがない場合の既定動作

**決定**：Happyはupstream固有の価値観を利用先へ暗黙適用しない。利用先repoの既存`AGENTS.md`、Mission、policyを尊重し、共通の安全・評価整合性だけを適用する。価値判断が必要で既存方針から決められない場合に、利用先所有者へConstitution作成または個別判断を求める。

### 2026-08-22: 非互換時も修復経路を塞がない

**利用者の回答**：安全・評価整合性を弱めるdownstream指示にはHappyが従わない境界を認める。一方、強いhook guardでAIからの修正まで不可能になり、手動修正が必要になった過去の負担を避けたい。

**現時点の解釈**：「停止」は違反する通常作業や採用を進めないことであり、repo全体の編集不能化ではない。同期、原因調査、設定修正、safe rollbackなどのremediation pathは常に残す。修復主体まで排除する不可逆なhook lockは採用しない。

### 2026-08-22: 公式mergeを止めてもremediationは止めない

**決定**：ローカルではHappyが違反作業を拒否し、validatorが理由と修復手順を示す。公式repoのCIは非互換なConstitutionや禁止中のrelease／mergeをFAILにできる。Constitutionや設定の修復を妨げるhard lockはhookへ置かず、同期、調査、修復、safe rollback、緊急安全対応を常に許可する。

### 2026-08-22: 原則衝突を文化と差別化の学習資産にする

**利用者の問題提起**：原則衝突は単に停止する場面ではなく、双方の価値の相対的な重みを確認し、評価軸を育てる機会である。たとえば最小差分を1、将来再利用性を10としたとき、現在の文脈が3か6かを明示する。人→人、人→AI、AI→AIのどこを開発主軸にするかという比較軸は、将来の文化、競争力、差別化になる。

**批判的検討**：方向性は有益だが、単一の1〜10値は偽の精密さと結果に合わせた操作を招く。対象利用者、interaction topology、lifecycle、可逆性などの文脈と、尺度のanchor、具体例、決定理由を一緒に固定する必要がある。また旧repoの`privateEval`は評価scenario資産を指していたため、価値の重み付けに同じ語を再利用すると責務が混線する。

**提案**：Constitutionの原則を変更せず、特定文脈での相対的な重みと根拠をversion付きで表す`decision profile`を導入する。評価scenarioはprofileを事前固定して検証し、判断後に都合よく重みを変えない。

### 2026-08-22: private evalの一般的な意味を優先する

**利用者の補足**：旧repoの`privateEval`定義は十分理解せず、Satya Nadella氏の発信を起点に採用していた。Nadella氏の意味と先ほどの価値相対性が異なるなら、一般的なprivate evalを正とし、価値相対性には別名を一緒に考えたい。

**一次資料による確認**：Microsoft Build 2026の公式transcriptでは、private evalsは各組織の目的に対して継続改善するhill-climbing machineの一部であり、outcomes、RLEs、traces、enterprise knowledgeとともに組織が所有・管理する差別化IPと説明されている。

**整理**：private evalは、組織固有の「何が良いか」をscenario、rubric、期待結果、実測履歴として評価可能にした資産である。価値観の相対的な重み付けはprivate evalの設計入力になり得るが、それ自体をprivate evalとは呼ばない。旧repoの「secretを含まない公開評価ケース層」という定義は、public repoに置ける共有資産の境界としては有用だが、private eval一般の定義としては狭く、名称と責務の再設計が必要である。

**名称候補**：`decision profile`（判断プロファイル）、`trade-off profile`（トレードオフプロファイル）、`value-weight profile`（価値重みプロファイル）。

### 2026-08-22: 判断プロファイルをcanonical termにする

**決定**：原則間の文脈依存の重み、尺度、anchor、具体例、理由を表す正式語を`判断プロファイル`とする。二項対立を人が認知しやすい補助名として、初出時に`判断プロファイル（トレードオフプロファイル）`と表記する。`private eval`は組織固有の評価資産を指す語として分離する。

### 2026-08-22: publicな実評価と利用者private evalを分離する

**利用者の回答**：一般利用者のprivate evalは利用者管理の非公開領域に置く。一方、村上さん自身の実際の評価は、使いやすさを損なわないならpublic repoへ置いてよい。fork利用者が村上さん固有部分を削除・置換する案も検討したい。

**批判的検討**：公開した評価資産は、組織固有の「何が良いか」を測る実評価ではあっても、秘密性の意味ではprivateではない。fork後の削除・置換を必須にすると、個人情報の消し忘れ、upstream更新との衝突、upstream価値観の暗黙適用が起こりやすい。

**提案**：村上さんが公開を承認した実評価は、公式repoだけを検証する`upstream eval`としてplugin配布境界の外に置く。downstreamはそれを削除せず既定で非適用にし、利用者管理のprivate evalを別の場所から追加する。secret、顧客情報、非公開業務dataは公開承認の対象にせず、公開前に除外する。

### 2026-08-22: upstream evalを公開実評価の名称にする

**決定**：村上さんが公開を承認した公式repo用の実評価を`upstream eval`と呼ぶ。plugin配布先では既定非適用とし、利用者の`private eval`を削除・置換ではなく追加できる構造にする。全利用者へ適用する共通安全evalは個人philosophyを含めず、別責務とする。

### 2026-08-22: 最初の判断プロファイルのinteraction topology

**決定**：公式`happy-ai-work`の現在の主軸を人→AI、拡張軸をAI→AI、監査・復旧軸を人→人とする。人が目的・価値判断・承認を所有し、Happyが実行する。AI間の委譲・独立評価・自律改善を拡張しつつ、人だけでも履歴を読み、判断し、修復できる状態を維持する。

### 2026-08-22: upstreamの中心原則5群は現在も有効

**決定**：余白と継続可能性、基礎の正確さと再現可能な型、形式知化と成長の連鎖、原理原則・計測・ニュートラルな判断、安全・評価の誠実性と外科的対応、の5群は現在も有効である。

**利用者の懸念**：原則を受け取ったAIが判断に悩むなら、多少の変更を許容したい。原則が人→AI用かを明確にしたい。

**現時点の解釈**：価値そのものはinteraction topologyに依存させず、AIが適用しやすいsummary、優先規則、例、判断プロファイルを別に持つ。AIの失敗だけを理由に価値を緩めず、意味を変えない明確化と価値変更を区別する。

### 2026-08-22: 原則と適用層を分離する

**決定**：Constitution本文は人・AI共通の短い原則とする。日常summaryはAI向けの優先規則と停止条件、判断プロファイルはinteraction topologyごとの重みと具体例、private／upstream evalは実際の判断能力の検証を担う。AIの迷いはまずsummary、例、profileを改善し、原則の意味を変える場合だけvNext amendmentとする。

### 2026-08-22: 絶対的な優先関係だけを固定する

**決定**：安全・評価の誠実性・人間の所有権・修復可能性は他の利益と交換しない。基礎の正確さは速さや適用範囲の拡大より先に担保する。それ以外の原則衝突は事前固定した判断プロファイルで比較し、profileでも決まらなければ推測せず所有者へ確認する。

### 2026-08-22: driftはGit履歴と同期recordで測る

**決定**：cloneやcheckoutで変化するfilesystem mtimeは使用しない。個人philosophyはGitHub profile READMEのcommit SHAとcommit日時、upstream Constitutionはversionとcommit日時、同期状態は最後に比較した組み合わせ、drift開始日、反映／反映不要の判断で記録する。CIはprofileの最新commitを確認し、未確認の意味変更を検知する。

## Interview handoff

### 対象の目的

所有者が常時同席しなくても、通常改善、価値観変更、不正な評価緩和、正当なvNext改訂を区別でき、publicな利用先では利用者自身のphilosophyを尊重できる統治構造を作る。

### 重要な判断軸

- 安全・評価整合性・人間の所有権・修復可能性
- 基礎の正確さと再現可能性
- 余白、継続可能性、学習可能性
- public upstreamとdownstreamの所有権分離
- 判断軸と評価結果のversion付き履歴

### 役割と責任

- 村上さん：公式upstreamの価値観変更、納期理由の緊急例外、vNext採用を明示承認する。
- Happy：現行Constitution内の通常改善、意味を変えない明確化、安全被害の緊急対応を自律実行する。
- downstream所有者：利用先のphilosophyとConstitutionを所有する。
- 独立評価者：事前固定したscenarioと基準でbehaviorを評価し、過去recordを改ざんしない。

### 例外・異常系

- 3日以上のdriftは警告、7日以上はbehavior変更のrelease／mergeを制限、10日以上はremediationと緊急安全対応以外を停止する。
- 判定基準が曖昧ならB「判定不能」。納期で暫定判断するC「緊急例外」は所有者承認が必要。安全被害の封じ込めではHappyがCを選べる。
- downstreamが共通安全境界を緩和した場合は非互換として通常作業を停止するが、修復経路は塞がない。

### 成功条件と失敗条件

- 成功：各判断が該当するConstitution、判断プロファイル、評価基準versionに結び付き、過去と現在を比較できる。public利用先にupstream固有価値を強制しない。
- 失敗：実装結果に合わせた評価緩和、過去結果の上書き、価値観変更の無断採用、drift放置、修復不能なhard lock、個人情報やprivate evalの不用意な公開。

### 未確定事項

実装を左右する価値判断は解消済み。ファイル名、schema、validator実装などは、合意済み境界を変えない範囲で既存repoの型に合わせて決める。

## 調査時点の分類

### 移植済み

- repo固有のMission、product boundary、運用語彙
- source of truthを先に読むこと、小さい変更、機械検証、独立評価の一部
- 動的subagentによる独立レビュー、固定agentを増やさない境界

### 未移植

- 個人philosophyとHappy Constitutionの参照関係
- Constitutionの所有者、承認境界、versioning
- 評価基準を失敗後に緩和しない統治境界
- philosophy／Constitution間のdrift検知と同期判断

### 移植対象外

- 個人経歴と原体験のrepo内全文複製
- Copilot固有instructions階層、固定agent、`copilot-authoring`
- 旧repoの個別技術規約をConstitution本文へ混在させる構造

## 未確定トピック

1. drift検知と同期判断の契約
2. Constitution改訂の所有者・例外・禁止境界
3. 原則衝突時の停止・照会規則
4. versionと過去評価結果の結び付け
