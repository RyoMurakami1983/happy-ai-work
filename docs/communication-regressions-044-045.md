# Communicationの局所改善 #44 / #45

2026-10-22 / baseline: `55a8878` / happy-coding 0.6.2、happy-preview 0.4.1

## 変更と境界

既存の[communication基準2.0.0](../plugins/happy-core/skills/skill-eval/references/prompt-evaluation.md)で求める情報保持・適切な通知時点を、実行時に使う箇所へ具体化した。新たな評価軸・Critical gate・固定回答templateは追加しない。

| 困りごとの一般形 | 変更箇所と維持する境界 |
| --- | --- |
| 最終報告がtest件数に偏り、主要関心が落ちる | implementのcompletionから共通報告referenceへ接続。利用者の優先順で対応状況を示し、検証は根拠として添える |
| 設定versionと成果物の現在地が混ざる | 共通報告referenceとYohakuで、関係する生成・配置・起動確認を区別。無関係な状態欄は増やさない |
| 一覧へ詳細証拠を詰め込む | Yohakuの既存補足ルールを置換。指定列を優先し、理解・判断・実行に必要な条件は主表示に残す |
| 候補探索へ採用時の証明を要求する | technical-designの入力境界で、候補の存在と意味・由来・適用範囲の検証を分ける。採用・実装前の整合性確認は省かない |
| 条件が計画だけにあり、直前通知にない | 共通referenceとimplement内planningを接続。通知自体に目的・区分・外部接続・見込み/上限を含める |
| 共有出力がlockされ、検証できない | .NET project contractで同じ出力先を使う場合だけ競合を確認。無断終了や必要な回帰省略は認めない |

strict TDD、独立レビュー、HITL、権限境界、短い通常testの扱いは変更しない。AGENTS.mdやhome設定に通知規約を追加せず、自動Yohaku開始にも依存しない。依頼された範囲の既存承認を聞き直さず、新課金・認証変更・許可外の負荷や本番操作は引き続き保留する。

## 公開回帰case

[cases.v2.json](../evals/communication-quality/cases.v2.json)は架空入力だけの8件。schemaと既存基準2.0.0を使い、v1 cases・fixture・過去records・snapshotsを変更していない。表現の完全一致や文字数を合否にしない。

- implement-full / debug-full: 通知の情報とrun順序。想定8分・上限10分と即時エミュレーションを区別
- implement-short: 通常短時間testへ定型通知や再承認待ちを増やさない
- completion-priorities: 複数の主要関心を優先順で残し、実端末未確認を保持
- artifact-state: 設定更新、未生成、未配置、未起動確認を区別
- candidate-overview: 指定列の一覧、候補あり/未発見と意味の未確認、採用前の確認を分離
- verification-scope-change: 新課金・許可外の外部負荷を通知だけで承認済みにしない
- learning-depth: 初心者向けの具体例・因果関係・判断基準を短縮で落とさない

これらは既知の公開回帰caseであり、未見hold-outではない。今回はcase準備と静的整合性確認までで、8件を実行したbehavior評価ではない。今後実行する際は、generatorへpromptと必要な入力だけを渡し、判定欄・他条件・過去の正解を渡さない。[評価資産の境界](EVALUATION_ASSETS.md)に従って実行前固定・役割分離・sanitize済み新recordを扱う。

## 検証

- Python 3.14.8の品質入口: repo/eval validator、既存166 unit tests、Ruff 0.16.3、ty 0.0.74、diff checkが成功。既存testの削除・緩和なし
- 変更した4 skillsの公式quick_validate成功、remote Constitution checkはhealthy
- 初回aggregateは166 tests成功後、uv tool保存先の読取専用制約でlint/type checkが未実行。保存先を一時領域へ指定して再実行し、全段階の成功を確認
- 独立した差分・privacyレビューで、Yohakuの補足移動条件が「判断」だけへ狭まった点を発見。「理解・判断・実行」へ戻し、学習・操作情報を保つ

品質入口の成功はskillの実利用効果や人の負担改善を証明しない。生成・実行によるbehavior probe、baseline/candidate比較、利用者PCへの導入、新しい会話での読込・実検証は今回未実施。CIの対象commitと結果はPRで追う。

## 残る受入確認

- [#44](https://github.com/RyoMurakami1983/happy-ai-work/issues/44): 次の自然な実案件で、更新版を新会話で読み、implement内planningから実検証へ条件と既存許可が渡ることを観測する。旧implementation-planの再導入や評価用の実耐久試験は求めない
- [#45](https://github.com/RyoMurakami1983/happy-ai-work/issues/45): 最終報告の主要関心、条件の通知時点、学習・詳細説明の深さを観測する。質問ゼロや短い回答だけで理解成功・効果を主張しない
- [#60](https://github.com/RyoMurakami1983/happy-ai-work/issues/60) / [Draft #54](https://github.com/RyoMurakami1983/happy-ai-work/pull/54): 実モデル比較・テスト削減の判断は別作業。今回のstatic checksやlock対策では完了にしない

#44 / #45 / #60をopenのまま残し、合成入力・静的確認を実案件の受入完了や変更の因果効果へ読み替えない。
