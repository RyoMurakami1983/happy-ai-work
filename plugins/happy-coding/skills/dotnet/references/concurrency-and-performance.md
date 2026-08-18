# Concurrency and performance

## 並行性

- 共有可変状態を減らし、所有者とcancel／shutdown境界を明示する。
- 単発I/Oは`async`／`await`、producer-consumerは`Channel<T>`等、独立状態機械はactor系など、問題形状に合わせる。
- retry、timeout、idempotency、orderingを別々の契約として扱う。
- fire-and-forgetは例外とlifetimeを観測できる所有者がいる場合だけ使う。

## 性能

- 推測で型やallocationを最適化せず、代表的入力と計測方法を固定する。
- hot path以外の可読性を犠牲にしない。
- `struct`化、pooling、Span系API、並列化は、計測で支配要因と確認できた場合に限定する。
- 変更後は正しさのテストと性能計測を分離して両方残す。
