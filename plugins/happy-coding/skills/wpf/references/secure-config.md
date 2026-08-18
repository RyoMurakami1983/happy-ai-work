# Secure configuration

1. 保存対象をsecret、個人設定、cache、再取得可能dataに分類する。
2. 攻撃者モデルを決める。別userから守るのか、同一userの平文露出を避けるのか、端末紛失まで扱うのかを区別する。
3. Windows提供の保護機構、Credential Manager、組織標準のsecret storeを優先し、暗号鍵をapplicationと同じ場所へ置かない。
4. ViewModelはsecret値を長時間保持せず、service境界へ渡す。log、exception、telemetryへ値を出さない。
5. 破損、資格情報失効、user／machine変更時の復旧UXを設計する。
6. testでは実secretを使わず、保存・取得・削除・破損時の振る舞いをservice境界で確認する。

保護方式の変更は既存data migrationを伴う。読み取り互換、移行後の削除、rollback可否を明示する。
