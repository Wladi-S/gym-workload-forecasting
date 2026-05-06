# Architektur — gym-workload-forecasting

End-to-End-MLOps-Plattform für die Workload-Prognose von 14 Fitnessstudios in Rheinland-Pfalz.

## Komponenten (Ist-Stand)

- **Scraper:** Sammelt seit Januar 2023 minutengenaue Workload-Daten der 14 Studios und schreibt nach Supabase. Läuft extern auf einem VPS. Code liegt als Read-only-Kopie in `libs/scraper/`.
- **uv-Workspace:** Monorepo-Root verwaltet Tool-Konfiguration und Dependencies; ausführbare Code-Module liegen in Workspace-Members unter `libs/` und `apps/`.

## Komponenten (geplant)

- **PostgreSQL** als Source of Truth für Rohdaten, Features, Modell-Metadaten und Predictions; Supabase wird nach Cutover zum best-effort Mirror.
- **FastAPI-Service** liefert aktuelle, historische und prognostizierte Workload-Werte über eine öffentliche API.
- **Daten-Pipeline (Dagster)** für tägliches Resampling, Anreicherung und Validierung.
- **ML-Pipeline (XGBoost + MLflow)** mit täglichem Retraining gegen eine Naive-Baseline.
- **Streamlit-Dashboard** mit Heatmap und Prognose-Seite.

Die konkrete Reihenfolge der Ausbaustufen ist im PRD dokumentiert.

## Referenzen

- PRD: [`docs/prd.md`](prd.md)
- Decisions: [`docs/decisions/`](decisions/)
- Runbooks: [`docs/runbooks/`](runbooks/)
