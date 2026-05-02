# Gym Workload Forecasting — Product Requirements Document

| | |
|---|---|
| **Datum** | 2026-05-02 |
| **Status** | Draft |
| **Domain** | wladis.de |
| **Repo** | github.com/Wladi-S/gym-workload-forecasting |
| **Bundesland** | Rheinland-Pfalz (alle 13 Studios) |
| **TOS** | Erlaubnis erteilt Daten zu sammeln und zu veröffentlichen |

## 1. Overview

End-to-End-MLOps-Plattform für die 13 Fitnessstudios in Rheinland-Pfalz. Die Plattform baut auf einem seit Januar 2023 laufenden Scraper (~3 Mio. Datenpunkte) auf und ergänzt ihn um Datenvalidierung, Anreicherung, Modell-Training und öffentliche Bereitstellung via API und Dashboard.

**Doppelter Zweck:**
1. **Portfolio + Lerneffekt** (primär): Das Repo ist das eigentliche Produkt. Lernen moderner MLOps-Tools (Docker, PostgreSQL, Dagster, MLflow, Polars, GitHub Actions) hat Top-Priorität. Markdown-Doku dient als Arbeitskontext, ADR-Sammlung und Claude-Code-Kontext — keine eigene Doku-Site.
2. **Echtes Tool** (Konsequenz): Nutzbares Werkzeug für 100–200 Studio-Member. Dashboard adressiert primär Author und Reviewer.

**Architektur-Kernaussage (gilt für das gesamte Dokument):** Selbst betriebene PostgreSQL auf dem VPS ist die **Source of Truth** für Rohdaten, Features, Modell-Metadaten und Predictions. Supabase bleibt nur als Legacy-Quelle während der Migration und optional als best-effort Offsite-Mirror; sie ist **nicht** im kritischen Serving-Pfad und ersetzt **kein** versioniertes Backup.

## 2. Problem

- **Studio-Member** (~100–200 aktive Nutzer) haben heute keine zuverlässige Möglichkeit, die Auslastung für ihren geplanten Trainingszeitpunkt einzuschätzen — Trainingsplanung läuft per Bauchgefühl oder Live-Vor-Ort-Check.
- **Author** braucht ein substantielles, öffentlich einsehbares Senior-Niveau-MLOps-Projekt im Portfolio. Die seit 2023 gesammelten Rohdaten bieten dafür eine ideale, realistische Basis.
- **Hiring Manager / Reviewer** wollen Engineering-Praxis ohne lokales Setup beurteilen — direkt im Browser via Live-API, Dashboard, README, CI-Status.
- **Architekturproblem:** Eine reine BaaS-Datenablage reicht für ein MLOps-Portfolio nicht. Das Projekt soll Datenbankbetrieb, Migrationen, Backfills, Backup/Restore, Datenqualität und Serving im Zusammenspiel zeigen.

## 3. Goals

| # | Goal | Messbar durch |
|---|---|---|
| **G1** | Hohe Verfügbarkeit der Public API mit aktuellen und historischen Daten | UptimeRobot ≥ 99.5 % im Monatsmittel |
| **G2** | Forecasting-Modell schlägt naive Baseline reproduzierbar | MAE Modell < MAE Naive auf Holdout-Window |
| **G3** | Modell-Qualität erreicht in M4 empirisch festgelegte absolute Schwelle | MAE < Schwellwert auf Rolling-30-Tage-Holdout |
| **G4** | Vollautomatisierte Kette (Scrape → Postgres → Features → Modell → Predictions → API) | Kein manueller Eingriff über ≥ 30 zusammenhängende Tage |
| **G5** | Repo entspricht „Senior-MLOps"-Niveau | Grüne CI, README mit Architektur-Skizze + Live-Links |
| **G6** | Reproduzierbares Setup auf neuem System | Fresh-Clone-Runbook funktioniert; `just setup`/`up`/`test`/`health` arbeiten; `.env.example` vollständig; Migrations reproduzierbar |
| **G7** | PostgreSQL ist die kanonische operative Datenbank | API/Dagster/Training lesen aus Postgres; Supabase-Ausfall ist nicht kritisch; Backup/Restore-Runbook getestet |

## 4. Non-Goals

**Architektur & Betrieb**
- Kein Auth-Layer, User-Management, Multi-Tenancy, kein API-Key (Daten nicht personenbezogen, nur Read)
- Keine Mobile-App, kein Native-Frontend
- Kein Real-Time-Streaming (täglicher Batch reicht)
- Keine Multi-Region- / HA-Setup, kein Staging — manueller Rollback akzeptabel
- Keine atomaren Multi-DB-Transaktionen — Postgres gewinnt, Supabase-Mirroring best-effort und retrybar
- Supabase nicht als langfristige Source of Truth für API/Pipeline/Training
- Keine Reimplementierung des Scrapers in M0 — bleibt Black-Box bis zur Dagster-Integration in M3

**ML & Pipeline**
- Kein Online-Learning (tägliches Retraining genügt)
- Kein Bake-off mehrerer ML-Frameworks — bewusst ein Modell
- Keine parallelen Forecast-Strategien (z.B. hourly + daily) — ein Pre-Compute-Pfad
- Auto-Promotion mit MAE-Schwellen, Confidence-Intervalle, Drift-Detection-Tooling → Backlog

**Doku, Hardening, Sonstiges**
- Keine veröffentlichte Doku-Site (kein MkDocs/GitHub Pages); `docs/` lebt nur im Repo als Arbeits- und Claude-Code-Kontext
- Kein Container-Signing, SBOM, Distroless-Images → Backlog
- Keine Kommerzialisierung — kein Pricing, Billing, SLA gegenüber Nutzern

## 5. Target Users

| Gruppe | Beschreibung | Größe | Touchpoints |
|---|---|---|---|
| **Studio-Member** | Endnutzer der 13 RLP-Studios, planen Training nach erwarteter Auslastung | ~100–200 | Public API |
| **Hiring Manager / Reviewer** | Bewerten Engineering-Praxis und Portfolio-Qualität | offen | Repo, README, Live-Dashboard, Live-API |
| **Author** | Solo-Entwickler; Self-Monitoring der Modell-Qualität, Tool-Lerneffekt | 1 | Dashboard, MLflow-UI, Dagster-UI (intern) |

**Bewusst nicht-Zielgruppe:** Studio-Betreiber (kein B2B), Massenpublikum außerhalb RLP, andere Solo-Entwickler die das Projekt forken oder als Service nutzen wollen.

## 6. Core Features

### 6.1 Public Workload API
REST-Service unter eigener Subdomain mit Auto-TLS. Liefert für alle 13 Studios aktuelle, historische und prognostizierte Werte. **Liest ausschließlich aus der lokalen PostgreSQL** — Supabase liegt nicht im kritischen Request-Pfad. Externes Monitoring (UptimeRobot), Error-Tracking (Sentry), Rate-Limiting pro IP, gesetzliche Pflicht-Seiten (Impressum, Datenschutz nach DSGVO).

### 6.2 Automatisierte Daten-Pipeline (Dagster)
Tägliche orchestrierte Pipeline: Resampling der Roh-Scrapes aus PostgreSQL auf einheitliches Zeitraster, Anreicherung mit **Wetter** (Open-Meteo), **Feiertagen** (`holidays`-PyPI), **Schulferien** (mecodia-API), Datenqualität via **Pandera** mit zweistufigen Schwellen (weiche Warning, harte Stop-Schwelle für Modell-Training). Backfill-fähig über die volle Historie ab 2023. Supabase ist optional als Migrations-/Mirror-Quelle, **keine Voraussetzung** für tägliche Pipeline-Läufe.

### 6.3 ML-Training, Versionierung & Predictions
Tägliches **XGBoost**-Retraining außerhalb der Studio-Öffnungszeiten. Tracking via **MLflow**. Eine **Naive Baseline** (Wochentag-Stunde-Median) dient zugleich als Vergleichs-Champion und als Fallback bei Modell-Versagen — Wechsel Modell ↔ Naive **ohne Code-Change** steuerbar. Pre-Computed Predictions werden für ein definiertes Zukunftsfenster nach jedem erfolgreichen Training in PostgreSQL geschrieben.

### 6.4 Public Dashboard (Streamlit)
Öffentlich erreichbar, ohne Auth. Zwei Bereiche: (1) Live-Übersicht mit Heatmap aller 13 Studios und Modell-Performance über Zeit; (2) interaktive Vorhersage-Seite mit Datums-Range-Auswahl und On-Demand-Inferenz gegen das aktive Production-Modell. Read-only — keine Schreibwege.

### 6.5 Repo-Doku & Claude-Code-Kontext
Keine separat veröffentlichte Doku-Site. Doku bleibt als Markdown im Repo, pragmatisch auf Arbeitsfähigkeit, Reviewer-Kontext und Claude-Code-Nutzung ausgerichtet. Im Repo gepflegt:
- README mit Projektüberblick, Architektur-Skizze, Live-Links, Setup-Hinweisen
- Architecture Decision Records (u.a. „PostgreSQL als Source of Truth, Supabase als Mirror")
- Runbooks für Setup, Tests, Backup/Restore, Deployment
- Arbeitsnotizen, die Claude Code ausreichend Kontext für Implementierungen geben

### 6.6 CI/CD & Engineering-Praxis
Auf jedem PR/Push laufen Linting (Ruff), Type-Check (mypy), Tests (pytest + Coverage), Security-Scan (Trivy). **Lokale Pre-Commit-Hooks sind ausdrücklich unerwünscht** — sie bremsen häufiges Committen; lokale Checks bleiben freiwillig, die verbindliche Qualitätskontrolle liegt in GitHub Actions. **Conventional Commits** via Commitizen. Tag-basierte Releases via release-please (kein Staging). Branch Protection auf `main` (lineare Historie, grüne CI Voraussetzung), Container-Hardening (Non-root, Read-only-FS, Multi-Stage), GHCR als Registry, Dependabot.

### 6.7 Observability & Alerting
Bewusste Trennung der Alerting-Kanäle nach Domäne:
- **API-Errors** → Sentry (Stack-Trace-UI, Performance-Monitoring)
- **Pipeline-Failures** → Discord-Webhook (passend für Batch-Jobs)
- **API-Uptime** → UptimeRobot (5-Min-Ping, Discord/E-Mail-Alert)
- **DB-Health, Backup-Erfolg, Mirror-Lag** → eigene Checks

### 6.8 Reproducible Environment & Deployment
Repo enthält alle nicht-geheimen Bausteine: Lockfile, Dockerfiles, docker-compose, PostgreSQL-Service, `.env.example`, Migrations, Healthchecks, Bootstrap-/Deploy-Scripts, Runbooks. Standardisierte Kommandos via `just`/Makefile: `setup`, `test`, `up`, `down`, `logs`, `health`, `db-migrate`, `db-backup`, `db-restore-check`, `deploy`. **Reproduzierbar = Umgebung + Services + Schema + Abläufe**, nicht produktive Daten/Secrets — die kommen über Backup/Restore.

### 6.9 Database Ownership, Mirroring & Backups
PostgreSQL auf dem VPS enthält:
- Rohdaten aus dem Scraper (`raw_scrapes`)
- bereinigte und resampelte Beobachtungen
- angereicherte Feature-Tabellen
- Modell- und Batch-Metadaten
- Pre-Computed Predictions für die API

Supabase nach Migration: best-effort Mirror für Rohdaten (externe Kopie der nicht reproduzierbaren Scrapes). Mirror-Fehler **stoppen den Scraper nicht**; sie werden geloggt und retrybar gemacht.

**Backups ≠ Mirroring.** Zielbild: ≥ 1 versionierter, extern gespeicherter `pg_dump` + dokumentierter und mind. einmal getesteter Restore-Prozess. Der Restore-Prozess ist wichtiger als das bloße Vorhandensein eines Dumps.

## 7. Erfolgskriterien

### 7.1 Funktionale Metriken

| Metrik | Ziel | Messung |
|---|---|---|
| API Uptime | ≥ 99.5 % | UptimeRobot, monatlich |
| Pipeline Success Rate | ≥ 98 % im Rolling-30-Tage-Fenster | Dagster UI |
| PostgreSQL = Source of Truth | Supabase-Ausfall nicht kritisch | Konfig + Integration Tests + Runbook |
| Backup Restoreability | Restore mind. 1× erfolgreich getestet | Restore-Check-Runbook |
| Supabase Mirror Lag | Sichtbar gemacht, nicht-blockierend | Täglicher Row-Count-/Timestamp-Check |
| Modell-MAE (gemittelt) | < M4-Schwelle | MLflow, Rolling-30-Tage-Holdout |
| Modell schlägt Naive | Relative MAE-Verbesserung | MLflow-Vergleichs-Run |

### 7.2 Portfolio-Metriken (qualitativ)
Grüner CI-Badge + Coverage-Badge. README mit Architektur-Skizze, Live-Demo-Links, Setup-Guide und Hinweisen auf relevante interne Markdown-Dokumente. Commits durchgehend nach Conventional Commits.

## 8. Roadmap

**Konvention:** Pro Milestone nur das, was er braucht (YAGNI auf Tooling). Keine Zeitachse — fertig ist, wenn fertig ist. Kein separater Doku-Foundation-Milestone; Markdown wird opportunistisch gepflegt. **Reihenfolge:** Repo (M0) → DB-Fundament (M1) → Public API (M2) → Cutover & Hardening (M2.5) → Pipeline (M3) → ML (M4) → Predictions in API (M5) → Dashboard (M6).

### M0 — Repo-Foundation & laufender Scraper

**Outcome:** Public Repo live. Bestehender Scraper läuft unverändert im Minutentakt auf dem VPS und schreibt nach Supabase. Reproduzierbares Python-Setup, grüne CI mit Linting/Type-Checking/Tests, GitHub-Hygiene, leichte Markdown-Doku. Erste Test-Coverage gegen extrahierbare Scraper-Logik.

| Aspekt | Inhalt |
|---|---|
| **Eingeführt** | uv, Ruff, mypy, pytest, pytest-cov, Conventional Commits + Commitizen, GitHub Actions, Dependabot, Branch Protection, gitleaks, `just`/Makefile, LICENSE, PR/Issue-Template |
| **Optional / später** | Bandit, pip-audit, Codecov, VS Code Settings, `direnv`, `act` |
| **Weglassen** | Docker, FastAPI, Dagster, MLflow, Streamlit, PostgreSQL-Migration, MkDocs |
| **Begründung** | Nur technisches Fundament. Scraper bleibt produktiv unverändert; DB-Migration kommt bewusst nach der Foundation. |
| **Lernfokus** | Modernes Python-Projektsetup, CI/CD-Grundlagen, GitHub-Workflow, Security-Grundlagen, schrittweise Migration produktiver Logik |

### M1 — Local Postgres Foundation

**Outcome:** Eigene PostgreSQL auf VPS enthält die volle Historie aus Supabase. Schema via Alembic versioniert, idempotente Upserts mit deterministischen Unique Keys. Scraper schreibt **dual** (Supabase = kanonisch, Postgres = parallel best-effort, Postgres-Fehler stoppen den Scraper nicht). Noch nichts public.

| Aspekt | Inhalt |
|---|---|
| **Eingeführt** | Docker, docker-compose, PostgreSQL-Container (Volume + Healthcheck), Alembic, Unique Key (`source`, `studio_id`, `observed_at`), idempotente Upserts, Dual-Write-Pattern, lokale `pg_dump`/`pg_restore`-Smoke-Tests |
| **Übernehmen** | `raw_scrapes`-Tabelle, Backfill-Skript Supabase → Postgres ab 2023, Dual-Write-Patch, manuelles Diff-Skript Row-Count/Timestamp |
| **Optional / später** | Automatischer Diff-Report, Backfill-Resume-Logik, Materialized Views für häufige Aggregationen |
| **Weglassen** | FastAPI, Caddy, TLS, Public-Deployment, externe Backups (M2.5), Cutover (M2.5) |
| **Begründung** | Schema-Design ist Einbahnstraße — falsche Unique Keys/Indizes/Typen schleppen sich durch alle weiteren Milestones. Vor API-Launch isolieren. Dual-Write hält Scraper unangetastet; Cutover erfolgt erst in M2.5, nachdem Postgres mehrere Tage als parallele Senke gelaufen ist. Vermeidet API auf stale Backfill-Snapshot in M2. |
| **Lernfokus** | PostgreSQL-Betrieb, Schema-Design, Alembic-Migrations, idempotente Schreibwege, Backfill-Strategien, Dual-Write-Pattern, Risiko-Isolation in produktiven Pipelines |

### M2 — Public API v1: Historie & aktuelle Werte

**Outcome:** API live unter eigener Subdomain. Liefert aktuelle und historische Auslastung der 13 Studios aus lokaler PostgreSQL (in M1 befüllt + per Dual-Write aktuell). Auto-TLS, Pflicht-Seiten, Rate-Limiting pro IP, externes Monitoring, tag-basierte Releases.

| Aspekt | Inhalt |
|---|---|
| **Eingeführt** | FastAPI, Pydantic, pydantic-settings, Caddy + Auto-TLS, slowapi, Sentry, UptimeRobot, Trivy, release-please, GHCR, Tag-getriggerter Production-Deploy-Workflow, /health, /studios, /current, /history |
| **Übernehmen** | API-Dockerfile, Uvicorn, psycopg, SQLAlchemy Core, `httpx`, pytest-asyncio, Compose-Healthchecks für API + DB |
| **Optional / später** | Schemathesis, CodeQL, structlog, Watchtower |
| **Weglassen** | Dagster, MLflow, Streamlit, Supabase im Read-Pfad, Schema-Änderungen (steht aus M1) |
| **Begründung** | Schema steht aus M1 — M2 fokussiert nur auf API-Surface (HTTP, TLS, Reverse Proxy, Observability, Rate-Limiting, Release-Pipeline). FastAPI/Pydantic erzeugen automatisch OpenAPI-Docs. Read-Pfad bleibt auf bewährter lokaler Postgres — kein Supabase im Serving. |
| **Lernfokus** | REST-API, HTTP, DB-Zugriff, Deployment, TLS, Monitoring, API-Tests, Release-Pipelines |

### M2.5 — Cutover, Backups & Deployment Hardening

**Outcome:** Scraper schreibt **kanonisch** in Postgres; Supabase wird auf best-effort Raw-Mirror umgewidmet. Supabase-Ausfälle stoppen den Scraper nicht. Versionierte externe Backups, Restore-Tests, Secret-Handling, Firewall, VPS-Betrieb dokumentiert und mind. einmal validiert. **Mit dem Cutover ist G7 vollständig erfüllt.**

| Aspekt | Inhalt |
|---|---|
| **Eingeführt** | Externe Backup-Senke (Backblaze/S3/Hetzner Storage Box), Restore-Runbook, UFW/Firewall-Konfiguration, Secret-Handling-Konvention, Mirror-Lag-Monitoring, Retry-/Dead-Letter-Mechanismus für fehlgeschlagene Mirror-Writes |
| **Übernehmen** | Cutover-Plan (Postgres = Primär-Schreibziel, Supabase = best-effort Mirror), versionierte `pg_dump`-Backups mit Rotation, dokumentierter Restore-Test, Healthcheck-Scripts, Mirror-Lag-Report (Row-Count + Timestamp Supabase ↔ Postgres) |
| **Optional / später** | Automatischer Restore-Test im separaten Container, täglicher Mirror-Diff-Report, vollständiges VPS-Runbook, systemd-Härtung |
| **Weglassen** | Kubernetes, Prometheus/Grafana, Ansible, echte verteilte Transaktionen Postgres ↔ Supabase |
| **Begründung** | DB-Story abschließen, bevor Pipeline-Schicht (M3) drauf aufsetzt. Cutover ist kontrolliert, weil Postgres seit M1 als parallele Senke und seit M2 unter API-Last lebt — kein Sprung ins Kalte. Backups ≠ Mirror — eigener Betriebsprozess mit Restore-Validierung. |
| **Lernfokus** | DB-Cutover-Strategien, externe Backups, Restore-Validierung, Dead-Letter-Queues für Mirror-Writes, Server-Härtung, Secrets, Mirror-Lag-Beobachtung |

### M3 — Daten-Pipeline mit Dagster

**Outcome:** Dagster-orchestrierte Pipeline übernimmt den bestehenden Scraper perspektivisch als Scheduled Asset, resampled Roh-Scrapes aus Postgres täglich auf einheitliches Zeitraster, reichert mit Wetter/Feiertagen/Schulferien an, validiert in 2 Stufen via Pandera. Backfill ab 2023 abgeschlossen. Pipeline-Failures → Discord.

| Aspekt | Inhalt |
|---|---|
| **Eingeführt** | Polars, Dagster (Assets, Schedules, Backfills), Pandera, Open-Meteo Free, `holidays`-PyPI, mecodia Ferien-API, Discord-Webhook für Pipeline-Alerts |
| **Übernehmen** | Parquet-Snapshots, DuckDB (lokales Debugging + reproduzierbare Feature-Snapshots), `httpx`, `tenacity`, `respx`, Postgres-I/O-Assets |
| **Optional / später** | hypothesis, pytest-xdist, ydata-profiling, Typer |
| **Weglassen** | MLflow Registry, SHAP, Evidently, DVC, Supabase als Pipeline-Read-Dependency |
| **Begründung** | Zentraler Data-Engineering-Milestone. Postgres ist kanonische Quelle (seit M2.5 auch im Schreibpfad); Supabase darf keine Voraussetzung für Backfills oder Pipeline-Läufe sein. Pandera validiert Datenqualität, Parquet/DuckDB helfen lokalem Debugging. |
| **Lernfokus** | Data Engineering, Orchestrierung, Backfills, Datenqualität, API-Retries, lokale Analyse |

### M4 — ML-Pipeline mit MLflow

**Outcome:** Tägliches XGBoost-Retraining außerhalb der Öffnungszeiten. Naive Baseline als MLflow-Run für Vergleich und Fallback. Pre-Computed Predictions für ein definiertes Zukunftsfenster werden nach jedem erfolgreichen Training in Postgres geschrieben.

| Aspekt | Inhalt |
|---|---|
| **Eingeführt** | MLflow Tracking, XGBoost-Trainings-Pipeline, Naive-Baseline als MLflow-Run |
| **Übernehmen** | scikit-learn Pipeline + Metriken, TimeSeriesSplit oder Rolling-Origin-Backtesting, Basic Feature Importance, Prediction-Tabellen in Postgres |
| **Optional / später** | Typer für `train`/`evaluate`, Optuna, MLflow Dataset/Input/System Logging |
| **Weglassen** | Prophet, statsforecast als zweite Haupt-Baseline, sktime, Darts, SHAP-Vollausbau, Evidently, Prediction-Auslieferung aus Supabase |
| **Begründung** | Eigentlicher MLOps-Kern — nicht nur Training, sondern Experiment Tracking, Baseline-Vergleich, Modellversionierung, Vorbereitung der Predictions. Kein Framework-Bake-off (siehe Non-Goals). |
| **Lernfokus** | ML Engineering, Experiment Tracking, Modellversionierung, Baselines, Backtesting |

### M5 — Public API v2: Predictions

**Outcome:** API liefert zusätzlich Forecasts für die nächsten Stunden aus Postgres. Modell-Info-Endpoint zeigt aktive Version und Holdout-MAE. Naive-Fallback ohne Code-Change steuerbar.

| Aspekt | Inhalt |
|---|---|
| **Eingeführt** | (keine neuen Tools — Erweiterung des M2-Stacks) |
| **Übernehmen** | FastAPI-Stack, Pydantic-Schemas, MLflow Client, Modell-Lade-Logik, Prediction-Tabellen aus M4, Model-Info-Endpoint, Fallback-Switch, API-Contract- und Smoke-Tests |
| **Optional / später** | Schemathesis für neue Endpoints, einfacher Load-Test, Typer-Command für Fallback-Toggle |
| **Weglassen** | FastAPI-cache2, neues Dashboard-Tooling, komplexes Monitoring, Supabase im Serving-Pfad |
| **Begründung** | Verbindet M2 + M4 ohne neue Technologie. Neue Tools würden den Milestone unnötig aufblähen. |
| **Lernfokus** | Model Serving, API-Erweiterung, Fallback-Design, Contract Testing, robuste Auslieferung |

### M6 — Public Dashboard

**Outcome:** Streamlit-Dashboard unter eigener Subdomain ohne Auth. Live-Übersicht (Heatmap aller 13 Studios + Modell-Performance über Zeit) und interaktive Vorhersage-Seite mit On-Demand-Inferenz gegen das aktive Production-Modell.

| Aspekt | Inhalt |
|---|---|
| **Eingeführt** | Streamlit |
| **Übernehmen** | Plotly, Modell-Metriken aus API/MLflow, Forecast-Visualisierung, Heatmaps, einfache Performance-Charts |
| **Optional / später** | SHAP-Visualisierung, Altair statt Plotly |
| **Weglassen** | Grafana, Prometheus, große BI-Lösung, Dashboard-Zugriffe direkt auf Supabase |
| **Begründung** | Streamlit ist Python-first und liefert schnell sichtbare Demo. Plotly reicht als Visualisierungsstack. Grafana ist Systemmonitoring, nicht das Nutzer-Dashboard. Dashboard arbeitet wie die API gegen die kontrollierte Plattform-Schicht. |
| **Lernfokus** | Interaktive Dashboards, Visualisierung, Produktdemo, Storytelling für Reviewer |

## 9. Tooling-Einführungs-Reihenfolge

| Milestone | Neu eingeführt |
|---|---|
| M0 | uv, Ruff, mypy, pytest, pytest-cov, Conventional Commits + Commitizen, GitHub Actions, Dependabot, Branch Protection, gitleaks, `just`/Makefile |
| M1 | Docker, docker-compose, PostgreSQL, Alembic, idempotente Upserts, deterministische Unique Keys, Dual-Write, lokaler `pg_dump`/`pg_restore`-Smoke-Test |
| M2 | FastAPI, Pydantic, pydantic-settings, Caddy + Auto-TLS, slowapi, Sentry, UptimeRobot, Trivy, release-please, GHCR, Tag-Releases |
| M2.5 | Externe `pg_dump`-Backup-Senke, Restore-Runbook, Mirror-Lag-Monitoring, UFW/Firewall, Secret-Hardening, Dead-Letter für Mirror-Writes |
| M3 | Polars, Dagster, Pandera, Open-Meteo, `holidays`, mecodia, Discord-Webhook |
| M4 | MLflow, XGBoost, Naive-Baseline-Logging |
| M5 | (Erweiterung M2-Stack) |
| M6 | Streamlit |

## 10. Top-Level-Layout

```
gym-workload-forecasting/
├── .github/                     ← Workflows, Templates, Dependabot
│   ├── workflows/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── dependabot.yml
├── apps/                        ← Deploybare Services (jeder mit Dockerfile)
│   ├── api/
│   ├── dashboard/
│   └── pipeline/
├── libs/                        ← Geteilter Code (KEIN Dockerfile)
│   ├── common/
│   ├── scraper/
│   ├── db/
│   ├── schemas/
│   ├── features/
│   └── training/
├── docs/                        ← Interne Markdown-Doku / Claude-Code-Kontext
│   ├── prd.md
│   ├── adr/
│   ├── architecture/
│   ├── runbooks/
│   └── notes/
├── infra/                       ← Operational-Layer (kein App-Code)
│   ├── compose/
│   ├── caddy/
│   ├── migrations/
│   ├── db/
│   │   ├── init/
│   │   └── backup/
│   └── scripts/
├── notebooks/                   ← Exploration, kein CI-Code
├── tests/
│   └── scraper/
├── .env.example
├── .gitignore
├── justfile
├── pyproject.toml               ← uv-Workspace-Root
├── uv.lock
├── README.md
└── LICENSE
```

## 11. Inspiration & Referenzen
- Cookiecutter Template: https://github.com/fmind/cookiecutter-mlops-package/tree/main