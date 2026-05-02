## Summary

<!-- 1-2 Sätze: Art des PRs? Was tut dieser PR? Warum? -->

## Tests

<!-- Welche Tests wurden hinzugefügt? Was prüfen sie konkret? -->
- Hinzugefügte Tests:
  - `tests/<modul>/test_<name>.py::test_<case>` — prüft, dass ...
- Ausgelassene Test-Fälle (mit Begründung): ...

## Test plan

<!-- Wie wurde das verifiziert? -->
- [ ] `uv run just check` lokal grün
- [ ] CI grün (`checks` + `gitleaks`)
- [ ] Manuell getestet: ...
- [ ] ...

## Checklist

- [ ] Conventional-Commits-Format
- [ ] Doku aktualisiert (README / runbooks/ decisions), wenn relevant
- [ ] Keine Secrets im Diff
- [ ] ...
