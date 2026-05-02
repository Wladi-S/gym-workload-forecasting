# Runbook: GitHub-Setup

Einmalige Setup-Schritte für das Repository nach Fresh-Clone oder bei Setup eines neuen Repos. Reihenfolge ist wichtig.

## 0. Voraussetzungen

- `gh` CLI installiert und authentifiziert (`gh auth login`)
- Lokale Entwicklung läuft (`uv run just install` und `uv run just check` grün)

## 1. Codecov-Account und Token

**Reihenfolge ist kritisch — Codecov muss konfiguriert sein, BEVOR die erste CI-Welle läuft, sonst fehlt der Coverage-Upload.**

1. Browser: <https://codecov.io> → "Login with GitHub"
2. Repository hinzufügen / aktivieren: `Wladi-S/gym-workload-forecasting`
3. Token kopieren (Settings → Repository Upload Token)
4. Token als Repo-Secret setzen:
   ```bash
   gh secret set CODECOV_TOKEN --body "<token>"
   ```
5. Verifiziere:
   ```bash
   gh secret list
   ```
   Erwartet: `CODECOV_TOKEN` ist gelistet.

`fail_ci_if_error` im `check.yml` ist auf `false` gesetzt — Codecov-Outage blockiert keine Merges, aber ohne Token fehlt der Coverage-Upload. Der Token sollte trotzdem da sein.

## 2. GitHub Rulesets importieren

Nach erfolgreichem Codecov-Setup und nachdem mindestens **ein** PR die CI grün durchlaufen hat (sonst kennt GitHub die Status-Check-Namen nicht):

```bash
uv run just install-rulesets
```

Output: HTTP 201 + JSON des erstellten Rulesets.

**Falls 422 "ruleset already exists":** Ruleset wurde schon importiert. Manuell in GitHub-UI prüfen oder löschen und neu importieren.

## 3. Rulesets-Verifikation

Drei manuelle Tests.

### 3.1 UI-Check

GitHub-UI: `Settings → Rules → Rulesets → main`

Erwartet:
- Status: **Active**
- Targeting: `Default branch (main)`
- Required status checks: `checks` und `gitleaks`

### 3.2 Force-Push-Test

```bash
git push --force-with-lease origin main
```

Erwartet: Fehler `protected branch hook declined ... non-fast-forward updates not allowed`.

### 3.3 Direct-Push-Test

```bash
git checkout main
git pull
echo "# test" > test-direct.md
git add test-direct.md
git commit -m "test: should be blocked"
git push origin main
```

Erwartet: Fehler `protected branch hook declined ... pull request required`.

Cleanup:
```bash
git reset --hard origin/main
rm -f test-direct.md
```

## 4. Branch-Protection-Drift

Kein automatisierter Drift-Check. Wenn das Ruleset über die UI manuell editiert wurde, divergiert es vom committeten JSON. Resync nach Edit:

1. Aktuellen Stand aus der UI exportieren (manuell nach JSON kopieren).
2. Mit committet'em `.github/rulesets/main.json` vergleichen.
3. Bei Bedarf JSON updaten und re-importieren via `uv run just install-rulesets`.

Im Solo-Setup praktisch kein Problem, weil nur ein Maintainer Settings ändert.
