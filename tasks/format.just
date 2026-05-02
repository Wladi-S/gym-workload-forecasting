[group('format')]
format: format-import format-source

[group('format')]
format-import:
    uv run ruff check --select=I --fix {{SOURCES}} {{TESTS}}

[group('format')]
format-source:
    uv run ruff format {{SOURCES}} {{TESTS}}
