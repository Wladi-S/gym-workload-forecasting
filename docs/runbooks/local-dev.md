# Runbook: Local Development

## Voraussetzungen

- macOS oder Linux
- `uv` installiert (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- `git` installiert

## Fresh-Clone-Setup

```bash
git clone git@github.com:Wladi-S/gym-workload-forecasting.git
cd gym-workload-forecasting
uv run just install
```

`just install` führt aus:
1. `uv sync --all-groups` — installiert alle dependency-groups (`check`, `commit`, `dev`)
2. `uv run pre-commit install --hook-type=pre-push`
3. `uv run pre-commit install --hook-type=commit-msg`

Nicht in `just install` enthalten und einmalig vom Maintainer auszuführen:
- Rulesets importieren (`uv run just install-rulesets`, siehe [`github-setup.md`](github-setup.md))

## Tägliches Arbeiten

```bash
uv run just format    # Auto-Fix Imports + Formatting
uv run just check     # Voll-Check: format, code, type, security, dependency audit, tests
```

Alle Targets via `uv run just --list`.

## Dagster lokal ausführen

Das Dagster-Projekt wird über seine Paket-CLI ausgeführt, nicht über direkte Dateipfade:

```bash
uv --directory apps/pipeline run --package pipeline dg check defs
uv --directory apps/pipeline run --package pipeline dg dev
```

Eine IDE-Run-Configuration kann denselben Weg nutzen oder die gleiche Umgebung explizit
setzen. Den Play-Button auf einer Python-Datei nur verwenden, wenn die Configuration die
benötigten Environment-Variablen setzt.

## Testing

```bash
uv run just check-test                       # Tests ohne DB-Integration (parallel)
```

Vollständiger lokaler Prüfpfad:

```bash
uv run just check
uv run just check-db-integration
```

`just check` deckt Format, Linting, Typing, Security, Dependency-Audit und Tests ab.
`check-db-integration` startet eine frische Testdatenbank und führt die DB-Tests aus.

**Test-Layout:** Tests leben unter Root-`tests/<modul>/`, nicht in Member-Unterordnern.

**Konventionen:**
- Pure-Function-Tests für Parsing/Transformation.
- Fixtures als JSON-Dateien unter `tests/<modul>/fixtures/`.
- Keine Network-Tests (mocken oder Network-I/O-Funktionen meiden).

## Pre-Commit-Hooks

Konfiguration in `.pre-commit-config.yaml`:
- **`pre-push`**: Ruff-Lint + Ruff-Format vor jedem `git push`. Failed → Push blockiert.
- **`commit-msg`**: aktuell ohne aktive Hooks (Wrapper installiert, Conventional-Commits-Prüfung kommt später).

Umgehen mit `git push --no-verify` — nur in dokumentierten Notfällen verwenden, die CI prüft ohnehin alles.

## Pull-Requests

Nach Push auf einen Feature-Branch:
1. PR auf `main` öffnen (`gh pr create`).
2. CI muss grün sein (`checks` + `gitleaks`).
3. Conventional-Commit-Title (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`, `style:`, `perf:`, `ci:`).
4. **Default-Merge: `gh pr merge --merge`** (Merge-Commit) — Branch-Name und WIP-Historie bleiben im Tree.
5. Branch nach Merge **nicht löschen** — Tree bleibt vollständig als Doku-Ebene.

**Branch-Naming-Konvention** (matcht Conventional-Commit-Prefix):

| Prefix | Beispiel |
|---|---|
| `feat/<topic>` | `feat/scraper-import` |
| `fix/<topic>` | `fix/dagster-config` |
| `chore/<topic>` | `chore/update-ruff-0.10` |
| `docs/<topic>` | `docs/architecture-diagram` |
| `refactor/<topic>` | `refactor/scraper-pure-functions` |
| `test/<topic>` | `test/scraper-edge-cases` |
| `style/<topic>` | `style/format-justfile` |
| `perf/<topic>` | `perf/parser-batch-size` |
| `ci/<topic>` | `ci/upgrade-actions` |

**Sonderfälle:** `--squash` für triviale 1-Liner-PRs (z.B. Typo-Fix), `--rebase` für linear-saubere Sequenzen. Default bleibt `--merge`.

## Lokale Testdatenbank

Die lokale Testdatenbank nutzt Docker Compose und enthält nur Schema + `gym`-Seed-Daten.
Produktive Rohdaten werden nicht lokal kopiert.

```bash
uv run just db-test-up
uv run just db-test-health
uv run just db-test-psql
```

Falls Docker Desktop installiert ist, aber `docker compose` nicht im Terminal verfügbar
ist, kann der Compose-Pfad explizit gesetzt werden:

```bash
DOCKER_COMPOSE=/Applications/Docker.app/Contents/Resources/cli-plugins/docker-compose \
  uv run just check-db-integration
```

Frisch zurücksetzen:

```bash
uv run just db-test-reset
```

DB-Integrationstests sind pytest-Tests mit Marker:

```python
@pytest.mark.db
```

Normale Checks schließen diese Tests aus. Der dedizierte DB-Pfad startet eine frische
Testdatenbank, führt nur DB-Tests aus und stoppt die Testdatenbank danach wieder:

```bash
uv run just check-db-integration
```

Zum Debuggen kann dieselbe Teststrecke ohne automatisches Aufräumen laufen:

```bash
uv run just check-db-integration-keep
uv run just db-test-psql
uv run just db-test-down
```

`check-db-integration-keep` lässt Container und Volume bewusst stehen, damit der
DB-Zustand nach einem Testfehler inspiziert werden kann.

## Troubleshooting

### `pre-commit run` failed wiederholt
→ Hooks sind autofix-fähig (Ruff, end-of-file-fixer). Nach erstem Lauf: `git add -u` und erneut commit/push.
