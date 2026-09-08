# Balanced Coupling

結合の 3 次元（統合強度・距離・変動性）で、multi-repo や境界設計のリスクを確認します。
これは標準ルートでは重い場合にだけ使う optional route です。

## こんなときに使う

- 複数 repo が関係するとき
- shared library / SDK / generated client を提供または消費するとき
- frontend / backend / worker / mobile など所有境界が分かれるとき
- service split や context 分割を判断したいとき
- 共有 model や shared database が増えているとき
- 変更時に複数チーム・複数 deploy を同期する必要があるとき

単一repoの通常機能追加なら、通常の`technical-design`手順に戻ります。

## ワークフロー: Balanced Couplingをtechnical designへ反映する

### ステップ 1 — context と ownership を整理する

表にします。

| Context / Repo | Owner | Responsibility | Provides | Requires | Deploy / Release |
|---|---|---|---|---|---|

ここでの目的は、誰が何を所有し、どの contract を提供/要求するかを明確にすることです。

### ステップ 2 — サブドメインと変動性を見る

必要な範囲でだけ分類します。

- **Core**: 競争優位や主要価値に直結し、変わりやすい
- **Supporting**: 必要だが差別化ではなく、変化は中程度
- **Generic**: 既製品や標準機能で足りることが多い

分類は設計の補助です。全機能を DDD 表に落とすことが目的ではありません。

### ステップ 3 — 統合を 3 次元で評価する

主要な統合だけ評価します。

- **統合強度**: Contract < Model < Functional < Intrusive
- **距離**: 同一 module < 同一 repo < 別 repo < 別 team / 別 deploy
- **変動性**: 低 / 中 / 高

```markdown
| Integration | Strength | Distance | Volatility | Risk | Adjustment |
|---|---|---|---|---|---|
```

目安:

- 高強度 + 高距離 + 高変動性: contract を薄くする、所有境界を寄せる、同期変更を減らす
- 低強度 + 低距離: 分けすぎの可能性を見る
- Generic で高強度統合: provider lock-in と置換コストを見る

### ステップ 4 — technical designへ落とす

通常のtechnical designに、multi-repoのcontract情報を追加します。

追加するもの:

- repo ごとの provide / require
- 依存順序
- contract artifact path
- checksum や version が必要な artifact
- 統合 test / contract test の確認 command
- `artifacts:` フィールド（通常は保存したdesign artifact path。例外時だけ理由付きの`artifacts: conversation-only`）

`docs/design/NNN_TECHNICAL_DESIGN.md` へ保存します。multi-repoではconversation-onlyを選べません。
複数repoの実装順、vertical slices、HITL / AFKは`implementation-plan`へ渡します。
ユーザーが設計書の保存を明示した場合は、repo内artifactを保存してhandoffに列挙します。

## 注意点

- Balanced Coupling を毎回使わない。
- 3 次元評価を機械判定にしない。設計判断の会話を短くするための lens として使う。
- モジュールテスト仕様や実装順をここで詳細化しない。
- contract が不明なら、推測で実装順序を決めず `interview-with-docs` に戻す。
