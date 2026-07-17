# pipeline

Dagster-Projekt und einzige Code Location für Scraping, Datenvalidierung, Features und
Modelltraining.

## Installation

Dependencies werden über den uv-Workspace im Repository-Root installiert:

```bash
uv sync --all-packages --all-groups
```

## Lokale Entwicklung

```bash
uv --directory apps/pipeline run --package pipeline dg check toml
uv --directory apps/pipeline run --package pipeline dg check defs
uv --directory apps/pipeline run --package pipeline dg check yaml
uv --directory apps/pipeline run --package pipeline dg dev
```

Die Dagster-UI ist anschließend unter <http://localhost:3000> erreichbar.

Tests liegen zentral unter `tests/` und die vollständigen Repository-Checks laufen mit:

```bash
uv run just check
```
