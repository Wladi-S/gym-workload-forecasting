# run check tasks (Format zuerst — schnellster Fail-Pfad)
[group('check')]
check: check-format check-code check-type check-security check-audit check-test

# check dependency vulnerabilities
[group('check')]
check-audit:
    uv run pip-audit --skip-editable

# check code quality (Lint)
[group('check')]
check-code:
    uv run ruff check {{SOURCES}} {{TESTS}}

# check code format
[group('check')]
check-format:
    uv run ruff format --check {{SOURCES}} {{TESTS}}

# check code security (Ruff S-Ruleset, kein Bandit)
[group('check')]
check-security:
    uv run ruff check --select=S {{SOURCES}}

# check unit tests
[group('check')]
check-test numprocesses="auto":
    uv run pytest --numprocesses={{numprocesses}} {{TESTS}}

# check code typing
[group('check')]
check-type:
    uv run mypy {{SOURCES}} {{TESTS}}
