# UI Review Checklist

## フローと状態

- 誰が何を完了したいか、最初の一手は明確か。
- empty、loading、active、success、errorと必要な例外状態に、理解可能な次の行動があるか。
- disabled、処理中、完了の表示が実際の状態と一致するか。
- errorから再試行、修正、取消、支援へ戻れるか。

## 構造と操作

- 関連情報と操作が近接・整列し、主目的が対比で分かるか。
- primary、secondary、destructive commandが競合していないか。
- controlは操作可能であることを示し、labelと結果が予測可能か。
- 自動選択やfallbackが利用者の選択を黙って置き換えていないか。

## アクセシビリティと検証

- キーボードだけで主要controlに到達・操作でき、focusが見えるか。
- label、error、statusは色だけに依存しないか。
- 最小viewportと拡大時に主タスクを完了できるか。
- screenshotだけで結論にせず、少なくとも一つの主要操作と状態変化をruntimeで確認するか。
