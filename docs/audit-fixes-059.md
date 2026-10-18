# Workflow監査修正 #59

2026-10-18 / baseline: `f1c8b2a` / [Issue #59](https://github.com/RyoMurakami1983/happy-ai-work/issues/59)

## 目的と採用範囲

既存contractの矛盾、限定fleet経路でのmetadata消失、統合後の更新確認漏れ、任意plugin依存を小さく修正する。Constitution、保存必須条件、着手承認、評価基準は変更しない。

- interview-with-docs / to-prd / technical-designのconversation-only判定を、既存のWORK_ARTIFACTSへ委譲する。議論を知らない利用者も同じ保存例外を参照できる配置とする
- interview-with-docsはinterview-meがなければ直接必要事項を聞く。coding単独利用で導入待ちを作らず、用語整理・合意・保存責務を保つ
- 更新確認は統合planningの選択filesと廃止entrypointの不在を確認する。全installed treeや実session loadの証明にはしない
- contract verificationはon-disk frontmatterの未知metadataと本文を保持し、対応するchecksumだけを更新する。変更不要なら書込みをしない。対象はmulti-repo fleetのroot plan.mdであり通常のdocs/planとは別
- happy-codingを0.6.0から0.6.1へ更新する

## 独立した指示・場面レビュー

変更意図の説明を渡さず、関連skillsと4つの場面を別reviewerがread-onlyで確認した。これは指示の整合性確認であり、実タスクを遂行するbehavior benchmarkやblind gradingではない。

| 場面 | 確認した判断 |
| --- | --- |
| codingのみ、interview-meなし | 資料を読み、直接質問する。domain-modeling / html-questionnaireはcoding内に存在し、core導入待ちは不要 |
| 独立した低riskの2 slices、後続判断記録不要 | conversation-onlyが可能。具体的exception reasonを残し、実装許可は別に確認 |
| 文書不要指定とmulti-repo/public-contract migration | 保存必須条件との競合だけを確認。例外を黙って選ばず、設計・ADR・計画を保存 |
| 1 sliceだがlong-lived structureと後続判断記録あり | one-sliceを理由に省略せず、構造判断・ADR・計画を残す |

レビューで見つかったto-prdの「必ず保存」と例外の文字どおりの緊張は、既存共通例外を除く旨に修正した。CONTEXT.mdの既存作成・更新責務は今回変更しない。

## 検証記録

- `uv run --script scripts/validate_quality.py`: Python 3.14.8、166 tests（約20秒）、repo validator、Ruff 0.16.3、ty 0.0.74、diff check PASS。既存143 testsを維持し23 tests追加
- 独立コードレビューPASS、別reviewerが36 focused testsを再実行してPASS。metadata・本文・no-op保持、planning fileだけが古い場合、廃止entrypoint残存、path非開示を確認
- 新しいcontract回帰suiteをbaselineへ適用し、metadata消失・no-op書込み・本文保持等の失敗を再現
- 3つの変更skillは公式quick_validateでPASS。remote Constitution checkはhealthy
- 初回aggregateではtest fixtureの型推論とloop closureのlintが失敗し、同時編集も検出された。修正・編集停止後に上記全件を再実行してPASS

checksumが変わる保存ではYAMLの整形・コメントは正規化され得る。metadataの意味とMarkdown本文は保持し、no-opでは元bytesを保持する。初回CIではUbuntuとsecret-scanが成功し、Windowsでdangling symlinkの拒否理由名がLinuxと異なりtestが1件失敗した（`present`想定に対し`outside_root`）。いずれも安全な不一致判定であり、productionの判定は変更せずtestで許す拒否状態を明示した。再実行するCIの対象commitと結果はPRに記録する。

実利用者のinstalled plugin更新やfresh session loadはこの修正の検証対象外。テストの選択的整理と実behavior比較は[Issue #60](https://github.com/RyoMurakami1983/happy-ai-work/issues/60)と既存[Draft PR #54](https://github.com/RyoMurakami1983/happy-ai-work/pull/54)で別に追う。新framework・大規模agent評価・性能改善の主張は追加しない。
