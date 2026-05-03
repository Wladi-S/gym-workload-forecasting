# gym-scraper

Scraping-Logik für die konfigurierten Studios in Rheinland-Pfalz.

**Distribution-Name:** `gym-scraper` (Bindestrich, in `pyproject.toml`)
**Import-Name:** `gym_scraper` (Unterstrich, Python-Modul)

Naming-Konvention: siehe [`docs/decisions/`](../../docs/decisions/).

## Laufzeitverhalten

Der Scraper ruft die Workload-Werte der konfigurierten Studios beim Aidoo-Portal ab und
schreibt erfolgreiche Messungen in zwei Datenbanken:

- lokale PostgreSQL-Datenbank
- Supabase als zusätzliche Absicherung

Ein fehlgeschlagener Studio-Request, eine fehlerhafte Antwort oder ein ungültiger
`numval`-Wert stoppt den Lauf nicht. Das betroffene Studio wird übersprungen, alle
anderen Studios werden weiter verarbeitet.

Die Datenbank-Writes werden ebenfalls getrennt versucht. Wenn ein Write-Ziel fehlschlägt,
wird das andere trotzdem ausgeführt. Der Scraper wirft eine Exception, wenn keine
Messungen gesammelt wurden oder wenn beide Datenbank-Writes fehlschlagen.

## Konfiguration

Secrets dürfen nicht im Code stehen. Die Werte kommen zur Laufzeit aus Environment
Variables. Die nicht-geheimen Variablennamen sind in [`.env.example`](../../.env.example)
dokumentiert.

Wichtige Gruppen:

- `SCRAPER_MANDANT`
- `SCRAPER_LOCAL_DB__*`
- `SCRAPER_SUPABASE_DB__*`

## Lokale Checks

```bash
uv run pytest -q
uv run ruff check libs tests
uv run mypy libs tests
uv run ruff format --check libs tests
```
