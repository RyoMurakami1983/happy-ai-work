#!/bin/bash
# Isolated real-host smoke test; needs noninteractive sudo docker access.
# Local bind mounts only: this does not test SMB/NFS or a production app.
set -euo pipefail
stage=preflight
work=''
trap 'rc=$?; printf "FAIL stage=%s exit=%s artifacts=%s\n" "$stage" "$rc" "$work" >&2; exit "$rc"' ERR
sudo -n docker version --format '{{.Server.Version}}'
sudo -n docker compose version
work=$(mktemp -d /tmp/happy-compose-smoke.XXXXXXXX)
project="happy-smoke-$(basename "$work" | tr '[:upper:].' '[:lower:]-')"
cd "$work"
exec > >(tee results.log) 2>&1
printf 'PROJECT=%s\nARTIFACTS=%s\n' "$project" "$work"
dc() { sudo -n docker compose -p "$project" -f "$work/compose.yaml" "$@"; }
expect_failure() {
  local rc=0 label=$1
  shift
  "$@" || rc=$?
  [ "$rc" -ne 0 ] || { echo "Unexpected success: $label"; return 1; }
  printf 'EXPECTED_FAILURE=%s exit=%s\n' "$label" "$rc"
}
stage=fixtures
mkdir source sibling data restore
printf 'fixture-source\n' > source/known.txt
printf 'outside-sentinel\n' > sibling/private.txt
printf 'persistent-sentinel\n' > data/keep.txt
chmod 755 source sibling data restore
uid=$(id -u)
gid=$(id -g)
cat > app.sh <<'APP'
#!/bin/sh
set -eu
test "$(cat /source/known.txt)" = fixture-source
if [ "$MODE" = broken ]; then
  echo 'stage=startup reason=injected-update-failure exit=42' >&2
  exit 42
fi
test -f /data/index.html || printf 'healthy-v1\n' > /data/index.html
exec httpd -f -p 8080 -h /data
APP
chmod 644 app.sh
stage=images
sudo -n docker pull busybox:1.37
base=$(sudo -n docker image inspect busybox:1.37 --format '{{index .RepoDigests 0}}')
printf 'BASE_IMAGE=%s\n' "$base"
cat > Dockerfile <<DOCKERFILE
FROM $base
ARG MODE=good
ENV MODE=\$MODE
COPY app.sh /app.sh
CMD ["sh", "/app.sh"]
DOCKERFILE
sudo -n docker build --network none -t "$project:v1" --build-arg MODE=good .
sudo -n docker build --network none -t "$project:broken-v2" --build-arg MODE=broken .
cat > compose.yaml <<YAML
services:
  app:
    image: \${TEST_IMAGE}
    user: "$uid:$gid"
    network_mode: none
    read_only: true
    cap_drop: [ALL]
    security_opt: [no-new-privileges:true]
    mem_limit: 64m
    pids_limit: 32
    healthcheck:
      test: [CMD, wget, -q, -O, /dev/null, http://127.0.0.1:8080/]
      interval: 1s
      timeout: 1s
      retries: 3
    volumes:
      - type: bind
        source: ./source
        target: /source
        read_only: true
        bind:
          create_host_path: false
      - type: bind
        source: ./data
        target: /data
        bind:
          create_host_path: false
YAML
printf 'TEST_IMAGE=%s:v1\n' "$project" > .env
stage=first-deploy
dc config --quiet
config_hash=$(sha256sum compose.yaml .env)
dc up --wait --wait-timeout 20
first_id=$(dc ps -q app)
dc exec -T app sh -ec 'test "$(id -u)" != 0; test "$(cat /source/known.txt)" = fixture-source; test ! -e /sibling/private.txt; test ! -e /source/../sibling/private.txt; printf "saved-by-app\n" > /data/saved.txt'
test "$(cat data/saved.txt)" = saved-by-app
expect_failure readonly-source dc exec -T app sh -c 'echo forbidden > /source/probe.txt'
test ! -e source/probe.txt
test "$(cat data/keep.txt)" = persistent-sentinel
stage=same-config-rerun
dc up --wait --wait-timeout 20
test "$first_id" = "$(dc ps -q app)"
test "$config_hash" = "$(sha256sum compose.yaml .env)"
echo 'PASS first-deploy same-config-rerun access-contract'
stage=missing-local-bind
dc down --timeout 2
mv source source-held
expect_failure missing-local-bind dc up --wait --wait-timeout 10
test ! -e source
mv source-held source
dc up --wait --wait-timeout 20
echo 'PASS missing-local-bind recovery'
stage=permission-denied
chmod 000 source/known.txt
expect_failure source-permission dc exec -T app cat /source/known.txt
chmod 644 source/known.txt
dc exec -T app cat /source/known.txt
echo 'PASS permission-denied recovery'
stage=backup
tar -cf backup.tar -C data .
before=$(sha256sum data/*)
stage=failed-update
printf 'TEST_IMAGE=%s:broken-v2\n' "$project" > .env
expect_failure failed-update dc up --wait --wait-timeout 15
failed_id=$(dc ps -a -q app)
test "$(sudo -n docker inspect "$failed_id" --format '{{.State.ExitCode}}')" = 42
dc logs --no-color --tail 5 app
test "$before" = "$(sha256sum data/*)"
stage=rollback
printf 'TEST_IMAGE=%s:v1\n' "$project" > .env
dc up --wait --wait-timeout 20
test "$before" = "$(sha256sum data/*)"
echo 'PASS failed-update exit=42 image-rollback data-preserved'
stage=restore
tar -xf backup.tar -C restore
diff -r data restore
sudo -n docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges:true --user "$uid:$gid" --mount "type=bind,src=$work/restore,dst=/restored,readonly" --entrypoint sh "$project:v1" -ec 'test "$(cat /restored/keep.txt)" = persistent-sentinel; test "$(cat /restored/saved.txt)" = saved-by-app'
test "$before" = "$(sha256sum data/*)"
echo 'PASS separate-restore readable-as-app-user original-unchanged'
stage=cleanup
dc down --timeout 2
test -z "$(sudo -n docker ps -a -q --filter "label=com.docker.compose.project=$project")"
sudo -n docker image rm "$project:v1" "$project:broken-v2"
echo 'PASS cleanup; test data and logs retained; base image retained'
echo 'SUCCESS: local-bind Compose smoke test; SMB/NFS and Ubuntu untested'
