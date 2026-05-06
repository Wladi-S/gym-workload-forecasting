# local and production database tasks

test_compose := "infra/compose/postgres.test.yml"
prod_compose := "infra/compose/postgres.yml"
docker_compose := env_var_or_default("DOCKER_COMPOSE", "docker compose")

# run DB integration tests against a clean local test database
[group('check')]
check-db-integration:
    #!/usr/bin/env bash
    set -euo pipefail
    cleanup() {
      {{docker_compose}} -f {{test_compose}} down --volumes --remove-orphans
    }
    trap cleanup EXIT
    just db-test-reset
    uv run pytest -o addopts="--strict-markers --strict-config -ra" -m db {{TESTS}}

# run DB integration tests and keep the test database running for debugging
[group('check')]
check-db-integration-keep: db-test-reset
    uv run pytest -o addopts="--strict-markers --strict-config -ra" -m db {{TESTS}}

# start local test PostgreSQL
[group('db')]
db-test-up:
    {{docker_compose}} -f {{test_compose}} up -d

# stop local test PostgreSQL without deleting the volume
[group('db')]
db-test-down:
    {{docker_compose}} -f {{test_compose}} down --remove-orphans

# recreate local test PostgreSQL from committed init SQL
[group('db')]
db-test-reset:
    {{docker_compose}} -f {{test_compose}} down --volumes --remove-orphans
    {{docker_compose}} -f {{test_compose}} up -d
    just db-test-health

# wait until local test PostgreSQL accepts connections
[group('db')]
db-test-health:
    #!/usr/bin/env bash
    set -euo pipefail
    for attempt in {1..30}; do
      if {{docker_compose}} -f {{test_compose}} exec -T postgres-test pg_isready -U gym_workload_test -d gym_workload_test >/dev/null 2>&1; then
        exit 0
      fi
      sleep 1
    done
    {{docker_compose}} -f {{test_compose}} ps
    exit 1

# open psql inside local test PostgreSQL
[group('db')]
db-test-psql:
    {{docker_compose}} -f {{test_compose}} exec postgres-test psql -U gym_workload_test -d gym_workload_test

# start production PostgreSQL on the VPS
[group('db')]
db-prod-up:
    {{docker_compose}} -f {{prod_compose}} up -d

# stop production PostgreSQL on the VPS without deleting the volume
[group('db')]
db-prod-down:
    {{docker_compose}} -f {{prod_compose}} down --remove-orphans

# show production PostgreSQL container status
[group('db')]
db-prod-ps:
    {{docker_compose}} -f {{prod_compose}} ps

# verify production PostgreSQL accepts connections
[group('db')]
db-prod-health:
    {{docker_compose}} -f {{prod_compose}} exec -T postgres sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'

# open psql inside production PostgreSQL
[group('db')]
db-prod-psql:
    {{docker_compose}} -f {{prod_compose}} exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
