# Runbook: Production Database

## Scope

M1 runs PostgreSQL locally on the new VPS through Docker Compose. Postgres is bound to
localhost by default and is not publicly reachable.

## Required Environment

Set these variables on the VPS before starting Postgres:

```bash
export POSTGRES_DB=gym_workload
export POSTGRES_USER=gym_workload
export POSTGRES_BIND_ADDR=127.0.0.1
export POSTGRES_HOST_PORT=5432
```

Also set `POSTGRES_PASSWORD` in the VPS shell or service environment before starting
Postgres. Do not commit the password.

## Start

```bash
uv run just db-prod-up
uv run just db-prod-health
uv run just db-prod-ps
```

## Inspect

```bash
uv run just db-prod-psql
```

Useful read-only checks:

```sql
SELECT count(*) FROM public.gym;
SELECT count(*) FROM public.data;
SELECT max(recorded_at) FROM public.data;
```

## Stop

```bash
uv run just db-prod-down
```

This stops the container without deleting the Docker volume.

## Schema

The schema is initialized from `infra/db/init/001_create_gym_data.sql` on first volume
creation. The `gym` table is seeded with the 14 real studios. The `data` table starts
empty and receives raw scraper measurements.
