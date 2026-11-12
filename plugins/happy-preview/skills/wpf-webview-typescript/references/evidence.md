# 設計の根拠

調査日: 2026-11-09。採用前に対象SDKと現行仕様を確認する。

## 公式仕様

- [WebView2 security](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/security): 受信元・入力検証、公開能力の限定、JSONでの送信を境界設計の基礎にした。
- [Threading model](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/threading-model): UI STA、callback内のreentrancy回避、deferralの扱いを寿命設計へ反映した。
- [Local content](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/working-with-local-content): virtual host mappingを静的UIの配信候補にした。HTTPサーバーを禁止する規則ではない。

## 公開repoの変更から得た判断

スターは注目度であり、設計の正しさではない。以下は差分読解による知見であり、各repoの実行検証ではない。

- [nomis51/webview2-desktop: TS bindings](https://github.com/nomis51/webview2-desktop/commit/fb455f66b9ab774ea19027ce4d2fd73f18e37e76): bindings追加後もany等が残る。型の導入と契約の保証を分けて考える。
- [nomis51/webview2-desktop: dev navigation](https://github.com/nomis51/webview2-desktop/commit/06e5b9233e892bafd69c480a40887360a8c7d4e3): 開発時の遷移制限を緩める変更。開発用originを明示し、製品版へ例外を持ち込まない判断につながる。
- [Microsoft WebView2Samples: WPF menu](https://github.com/MicrosoftEdge/WebView2Samples/commit/3f4c231dd6aa1f2d69075ec6e774da590856dba4): 非同期UIとdeferralの完了経路が重要。sampleの実験APIをそのまま製品要件にしない。

## 開発事例から一般化した判断

写真管理UIの開発で得た知見を整理した。元の実案件資料は配布せず、利用者データや非公開repoへの参照を含めない。この記述はスキル適用後の実務検証結果ではない。

- 閲覧から編集への条件引継ぎと、写真送りの末尾のfocusを実操作で確かめる。
- 非表示一覧の画像要求がpreviewを待たせる場合、viewport、優先度、取消し、世代照合、cache上限を組み合わせる。
- JPEG生成時間だけで長い表示間隔を説明できない場合、UI更新と観測側の負荷も分けて測る。

個別事例のcache件数・byte数を共通の推奨値にしない。

## 追加した設計案

pendingのtimeout/dispose、重複検出履歴の寿命、revisionによる更新削減、Web用transportの差替えは、スキルに含めた設計上の選択肢。今回のアプリで全て実装・検証済みとは扱わない。

## 記述方針

短歌・俳句の観察と推敲を、具体・条件・判断の選択に用いた。定型、詩的な句読点、比喩をUIラベルや技術契約へ強制しない。短さより意味の保存を優先する。

## 改善基準の出所

2026-11-09の所有者指示に基づき、1秒以上の遅延、取消し後の再入力、切断後の継続を対象アプリの改善・検証基準とした。これはWebView2の公式性能保証でも、スキルの比較評価指標でもない。元案件の合意を他案件へ暗黙適用しない。他案件では観察観点として使い、合否と追加実装は案件のAC・scopeに従う。適用条件と未達を記録し、安全な保存と整合性を短縮のために省かない。

## 通常起動の検証からの引継ぎ

同じ論理パスでも検証用packageと通常プロセスが異なる管理記録を参照し、再インストールではなく通常側の再接続で解決した事例を確認した。この事例から、配布物・起動条件・実際の参照先を分けて確かめる手順を追加した。環境差が全てのWPFアプリで生じるとは扱わない。
