---
name: repo-onboarding
description: 未知のリポジトリを変更せずに調査し、目的、構造、技術、build／test契約、重要境界、未確認事項の最初の地図を作る。新しいrepoへ入るときや実装前のorientationで使う。bootstrap変更は扱わない。
---

# Repository onboarding

read-onlyで、README・manifest・lockfile・CI・有効なCodex project instruction・近接docsを根拠に最初の地図を作る。

1. repo root・git状態・README・docs入口を確認する。各directoryのinstruction chainは`AGENTS.override.md`→`AGENTS.md`→`project_doc_fallback_filenames`の設定済みfallbackの順で解決する。
2. solution／workspace／manifest／lockfile／CIから主要言語・runtime・dependencyとbuild／test／lintの正本を特定する。
   - 上流から取り込んだrepoは、初回push・CI有効化・上流同期で変更をpushする前に、送信先の公開範囲、CIの起動条件・対象OS・重いjobの所要時間／費用、公開・配布処理、権限・secretの参照を読み取りで確認する。利用目的に合わせ「毎回／対象変更時／配布前／不要」に分け、残すべきsecurity検証・必須チェック（上流へ提出する場合はその要件も）と費用の根拠・不明点を示す。調査中はCIを起動・変更しない。
3. 主要directory・entrypoint・public interface・data store・external integrationを浅くたどり、一つの代表経路を入口から出力まで追って責務境界を確かめる。
4. commandには根拠を添え、推測しない。実行が必要でも安全なread-onlyのversion／help／test discoveryから始める。

出力は目的、技術・環境、directory・entrypoint、代表flow・責務境界、根拠付きbuild／test／lint、重要制約・risk、未確認と次に読む場所。

親／home指示があっても、repo内にrepo管理の有効な`AGENTS.override.md`・`AGENTS.md`・設定済みfallbackがなければ、その事実とrepo固有のbuild／test・重大review制約を永続化する必要性を出力する。導入価値があり`workspace-bootstrap`が使えればhandoff候補にし、使えなければ必要性と専用機能の利用不可を伝える。どちらでもonboarding中は作成しない。

`AGENTS.md`・CI・hook等の追加依頼は`workspace-bootstrap`へ分け、onboardingの名目で設定を書き換えない。
