# Runtime Evidence

実装後は対象appを通常の起動経路で開き、主要フローを一つ以上完了する。静的markup、unit test、screenshotは補助証拠であり、それだけでUI評価を完了しない。

確認する内容は変更範囲に合わせて選ぶ。

- 初期状態と主要controlが表示され、keyboard focusで到達できる。
- primary commandを実行し、activeからsuccessまたはerrorまでの表示が内部結果と一致する。
- errorまたはdestructive operationでは、利用者の意図を保持した復帰または確認がある。
- 最小viewportまたは指定された拡大率で、主タスクに必要な情報と操作が利用できる。

記録には起動方法、操作、期待結果、観測結果、未確認の状態を含める。失敗時は再現条件と画面証拠を残し、実装または設計へ戻す。
