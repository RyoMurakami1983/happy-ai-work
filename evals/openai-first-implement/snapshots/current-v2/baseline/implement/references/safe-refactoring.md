# Safe refactoring

独立skillにはせず、実装中のrefactor modeとして使う。

1. 対象の責務と、絶対に変えない外部振る舞いを一文で固定する。
2. 重複削減、命名、関数分割、条件整理、依存明確化、I/O分離など、今回の変更理由を一つに絞る。
3. 既存test、characterization test、before／after出力、dry-run等の比較手段を先に用意する。
4. 一つの関心事だけを変更し、同じ確認を実行する。無関係なformatや全面renameを混ぜない。
5. 公開API、serialization、data、timing、exception、performanceが本当に不変か確認する。
6. 同じ振る舞いと改善された点を別々に説明する。

確認手段がなく広範囲を動かす必要がある場合は、refactorを始めず`technical-design`または`debug-and-fix`へ戻る。
