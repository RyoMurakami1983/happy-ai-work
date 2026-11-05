# スキル本文の凝縮と短歌・俳句のcore移行

Date: 2026-11-05 (UTC)
Status: 所有者承認済みの変更案。PRで検証し、マージは別途判断する。

## 採用範囲

基準commitは `c2677825411b0b5810bdcd325792978de9a61839`。全35件を比較し、本文13件に限定採用の判断を行った後、所有者が短歌と俳句の短縮前後を確認した。所有者は「短縮の前の方を採用」と明示し、短縮前の本文をhappy-coreへ移すことを承認した。最終的な変更は本文短縮12件と、短縮しない短歌・俳句1件の移動である。成果物圧縮は採用0件・全35件保留のまま。

本文率はLF正規化したUnicodeコードポイントで、frontmatter閉じ行の改行後から末尾までを計数する。空行も含める。参照先への移設やtoken推定を削減へ数えない。

| 採用する本文 | 元→採用（字） | 削減率 |
| --- | ---: | ---: |
| `home-bootstrap` | 1325→1067 | 19.47% |
| `interview-me` | 3293→1181 | 64.14% |
| `workspace-bootstrap` | 1353→1095 | 19.07% |
| `ci-debug` | 534→439 | 17.79% |
| `deep-review` | 786→668 | 15.01% |
| `domain-modeling` | 2980→2215 | 25.67% |
| `implement` | 8404→6228 | 25.89% |
| `nuget-local` | 851→721 | 15.28% |
| `python` | 1226→1069 | 12.81% |
| `repo-onboarding` | 1206→939 | 22.14% |
| `rust` | 826→723 | 12.47% |
| `technical-feasibility-research` | 2020→1628 | 19.41% |

これらは文章を静的に凝縮したもの。`tanka-to-haiku`を実行時に読む工程や共通の成果物圧縮処理は追加していない。同スキルの将来更新は、短縮済みの12本文へ自動伝播しない。

## 評価根拠と限界

- 初期420出力は35件の探索比較。複数技能のcontext共有等があり、個別採用の実行根拠にはしない。
- CI、python、rust、技術実現性調査、repo-onboarding、domain-modelingは対象を分離した固定通常・境界課題を各2反復で比較し、別の盲検AIが採点した。rustは後に実1.70.0でもdebug/releaseを確認した。
- home/workspace-bootstrapはtemp環境のbackup・再適用・復旧を含む24実行で比較。interview-me旧B1はAIユーザーとの固定2課題×各2反復を比較し、重要な既存問題と候補追加差を区別した。
- deep-reviewはB3の16レビュー・実コード操作、nuget-localは8回の実pack/consume、implementはB2の12評価workflowで比較した。候補hashを照合し、評価後に別の文章へ置き換えていない。
- 旧版にもある欠勤時権限の未確認、handoffのbackup path説明、reviewのscope説明等の失敗は残る。旧絶対FAILをPASSへ変更せず、候補による重要な追加劣化が観測されなかった範囲で採用した。
- 全状況の同等性、素のモデルに対する追加価値、人間の理解時間、自動選択、利用者環境での読込は証明していない。未完了は成功へ数えていない。別のinterview-me B2は不採用で、反映しない。
- 成果物側は完成範囲・品質保持・反復ごとの10%以上削減が揃わなかった。本文短縮の成果物長変化と、圧縮指示単独の効果も区別する。

詳細評価と元のローカル保存commitは非公開の作業記録として保持する。PRにはこの要約と必要なコード・テストを含め、生成対話・大量の評価JSON・個人用Spaceリンク・生ログを含めない。公開物だけでは過去の全採点を再実行できない。

## 短歌と俳句の移動

`happy-preview/skills/tanka-to-haiku`を`happy-core/skills/tanka-to-haiku`へ移動する。本文は基準commitと完全一致させ、frontmatterのPreview表示とUIの「試用版」表示だけを除く。名前とdefault promptは維持する。旧短縮案の「一景で届くなら」「意味を立ち上げる」の省略を採用しない。

この通常配布は所有者の明示判断による。[ADR 0004](../adr/0004-preview-plugin-distribution.md)が求める異なる実案件での複数回有用性確認を、新たに完了したとは主張しない。[初版時点の記録](../tanka-to-haiku-preview.md)も保持する。品質の普遍的優位を主張する昇格ではない。

| plugin | 基準版→今回 |
| --- | --- |
| happy-core | 0.4.0→0.5.0（skill追加） |
| happy-coding | 0.7.0→0.7.1（本文凝縮） |
| happy-preview | 0.6.0→0.6.1（移動による削除と本文凝縮） |

manifestは`./skills/`を読むため個別登録を増やさず、marketplaceの3登録と任意導入policyを維持する。source上はcoreに1件だけ置き、previewに互換stubや重複copyを残さない。

## 既存利用者の移行

1. [plugin更新の確認手順](../plugin-update-verification.md)でmarketplaceを対象commitへ更新し、happy-coreを導入・更新する。preview版を使っていた場合はhappy-previewも更新する。previewのみの利用者へcoreが自動導入されるとは仮定しない。
2. 旧plugin namespaceを含む明示呼出しはhappy-coreへ変更する。skill名`tanka-to-haiku`自体は変えない。旧namespaceのaliasは提供しない。
3. 実際に返されたinstalledPathの内容を照合する。coreの本文/UI設定の一致とpreview旧directoryの不在を別々に確認する。空directoryやdangling symlinkも旧登録の残存として不一致にする。
4. 旧登録が残れば、対象を確認して旧skillを無効化・削除する。他のpreview skill利用中はplugin全体を無効化しない。cacheを無差別に削除しない。
5. 新しい会話で利用可能性・読込元を確認する。repo編集、version増加、hash一致だけで読込成功とはしない。既存会話や実homeへ自動反映されるとは仮定しない。

このPR作業は利用者PCへの導入・再導入・削除を実施しない。移行検査は隔離した合成plugin copyを用い、実インストールと会話読込は未確認として残す。

## 今回の統合検証

- 基準commitの短歌・俳句本文とのbyte一致、採用済み12件の評価候補SHA-256一致、全35件の一意性（core9・coding21・preview5）を確認。
- `uv run --script scripts/validate_quality.py`でrepo validator、212 unit tests、Ruff 0.16.3、ty 0.0.74、diff checkが成功。既存workspace/repo-onboardingの25文字列assert変更は表現追従で、テスト構造・判定ロジックは変更しない。
- 更新照合の合成copy試験ではcore本文/UIの古さ・欠落、preview旧directory/entrypointの残存を検出し、除去後のsample一致を確認。実cache自動更新や会話読込の実測ではない。
- ローカルの`validate_constitution.py --check-remote`はAPI接続403で判定不能。検査を迂回せず、PR CIで別途確認する。判定不能のままrelease/mergeしない。
