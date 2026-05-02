# gym-workload-forecasting

[![check](https://github.com/Wladi-S/gym-workload-forecasting/actions/workflows/check.yml/badge.svg)](https://github.com/Wladi-S/gym-workload-forecasting/actions/workflows/check.yml)
[![gitleaks](https://github.com/Wladi-S/gym-workload-forecasting/actions/workflows/gitleaks.yml/badge.svg)](https://github.com/Wladi-S/gym-workload-forecasting/actions/workflows/gitleaks.yml)
[![security](https://github.com/Wladi-S/gym-workload-forecasting/actions/workflows/security.yml/badge.svg)](https://github.com/Wladi-S/gym-workload-forecasting/actions/workflows/security.yml)
[![license](https://img.shields.io/github/license/Wladi-S/gym-workload-forecasting)](LICENSE)
[![python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)

End-to-End-MLOps-Plattform für die Workload-Prognose von 13 Fitnessstudios in Rheinland-Pfalz. Aufbauend auf einem seit Januar 2023 laufenden Scraper (~3 Mio. Datenpunkte) entstehen Datenvalidierung, Anreicherung, Modell-Training und öffentliche Bereitstellung über API und Dashboard.

## Quickstart

```bash
git clone git@github.com:Wladi-S/gym-workload-forecasting.git
cd gym-workload-forecasting
uv run just install
uv run just check
```

Komplette Target-Liste: `uv run just --list`.

## Repo-Struktur

```
gym-workload-forecasting/
├── apps/                ← Deploybare Services (api, dashboard, pipeline)
├── libs/                ← Workspace-Members (scraper, common, db, schemas, features, training)
├── infra/               ← Operational-Layer (compose, caddy, migrations, db, scripts)
├── docs/                ← PRD, Architektur, Runbooks
├── notebooks/           ← Exploration
├── tasks/               ← Just-Task-Module
└── tests/               ← Tests (Root-Layout, gespiegelt zu libs/apps)
```

## Lizenz

Apache-2.0 — siehe [LICENSE](LICENSE).
