# Windows sandbox and uv

Windows sandboxでは、`uv`自体がPATHにあっても、cache、managed Python、既存venvのbase interpreterがsandbox外にあり、process起動だけが失敗することがある。cache pathの変更を繰り返す前に、実行入口とpath境界を一度だけ確認する。

## Preflight

repoの`pyproject.toml`、lockfile、README、CIを確認した後、次を読む。

```powershell
Get-Command python -ErrorAction SilentlyContinue
Get-Command uv -ErrorAction SilentlyContinue
Get-Command uvx -ErrorAction SilentlyContinue
if (Test-Path -LiteralPath '.venv\pyvenv.cfg') {
    Get-Content -LiteralPath '.venv\pyvenv.cfg'
}
```

Codexから提供されたwritable rootと、`uv`のcache、managed Python、`.venv\pyvenv.cfg`の`home`を比較する。実行fileが存在することと、sandbox内でそのbase interpreterを起動できることを分けて判断する。

## 実行入口を選ぶ

- repo既定のrunnerと環境がsandbox内で起動できる場合は、その契約を維持する。
- `.venv`のbase interpreterやuv managed Pythonがsandbox外にあり、検証が必要な場合は、同じ失敗をcache変更で再試行しない。既存venvのPythonなど、必要なcommandとpathに限定して権限昇格を求める。
- sandbox制限を避ける目的だけで`UV_CACHE_DIR`をrepo内へ変更しない。uvのproject discoveryによってcache、`.venv`、`uv.lock`などを生成し、worktreeを汚す可能性がある。
- repoがuv projectとしてlockfileを管理している場合は、その既定commandとlock契約を使う。単発toolやproject化されていないrepoでは、必要に応じて`uvx <tool>`または`uv run --no-project --with <dependency> python <script>`を使い、project metadataを生成しない。downloadやsandbox外cacheが必要なら、そのcommandに限定して権限昇格する。
- UTF-8のMarkdownやYAMLをWindows locale依存のscriptで読む際にencoding errorが観測された場合だけ、対象processへ`PYTHONUTF8=1`を渡す。一般的な失敗をUTF-8 modeで隠さない。

失敗後と検証後に`git status --short`で生成物を確認する。意図しないcache、lockfile、venvがあれば、今回生成したものだと確認できた対象だけを片付ける。必要な検証が成功したら、実行command、権限昇格の理由、repoに残したartifactを報告する。
