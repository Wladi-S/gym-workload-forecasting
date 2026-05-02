# run check tasks (Format zuerst — schnellster Fail-Pfad)
[group('check')]
check: check-format check-code check-type check-security check-coverage

# check code quality (Lint)
[group('check')]
check-code:
    uv run ruff check {{SOURCES}} {{TESTS}}

# check code coverage (Threshold 50% in M0)
[group('check')]
check-coverage numprocesses="auto" cov_fail_under="50":
    uv run pytest --numprocesses={{numprocesses}} --cov={{SOURCES}} \
                  --cov-fail-under={{cov_fail_under}} \
                  --cov-report=xml --cov-report=term {{TESTS}}

# check code format
[group('check')]
check-format:
    uv run ruff format --check {{SOURCES}} {{TESTS}}

# check code security (Ruff S-Ruleset, kein Bandit)
[group('check')]
check-security:
    uv run ruff check --select=S {{SOURCES}}

# check unit tests (ohne Coverage, schnell)
[group('check')]
check-test numprocesses="auto":
    uv run pytest --numprocesses={{numprocesses}} {{TESTS}}

# check code typing
[group('check')]
check-type:
    uv run mypy {{SOURCES}} {{TESTS}}
