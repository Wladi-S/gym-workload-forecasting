# gym-scraper

Scraping-Logik für die konfigurierten Studios in Rheinland-Pfalz.

**Distribution-Name:** `gym-scraper` (Bindestrich, in `pyproject.toml`)
**Import-Name:** `gym_scraper` (Unterstrich, Python-Modul)

Naming-Konvention: siehe [`docs/decisions/`](../../docs/decisions/).

## Laufzeitverhalten

Der Scraper ruft die Workload-Werte der konfigurierten Studios beim Aidoo-Portal ab und
schreibt erfolgreiche Messungen in die lokale PostgreSQL-Datenbank.

Ein fehlgeschlagener Studio-Request, eine fehlerhafte Antwort oder ein ungültiger
`numval`-Wert stoppt den Lauf nicht. Das betroffene Studio wird übersprungen, alle
anderen Studios werden weiter verarbeitet.

Der M1-Betriebsmodus ist Postgres-only. Supabase-Mirroring wird in einem späteren
Milestone wieder bewusst eingeführt.

## Konfiguration

Secrets dürfen nicht im Code stehen. Die Werte kommen zur Laufzeit aus Environment
Variables. Die nicht-geheimen Variablennamen sind in [`.env.example`](../../.env.example)
dokumentiert.

Wichtige Gruppen:

- `SCRAPER_MANDANT`
- `POSTGRES_BIND_ADDR`
- `POSTGRES_HOST_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

## Ausführung

```bash
# for production runs
uv run --env-file .env gym-scraper

# for local development
uv run --env-file .env.dev gym-scraper
```

Für Produktionsläufe dieselbe CLI mit der passenden Env-Datei oder einer vom
Prozessmanager gesetzten Umgebung ausführen.

## Lokale Checks

```bash
uv run pytest -q
uv run ruff check libs tests
uv run mypy libs tests
uv run ruff format --check libs tests
```
