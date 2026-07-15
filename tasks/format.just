[group('format')]
format: format-import format-source

[group('format')]
format-import:
    uv run --all-packages ruff check --select=I --fix {{SOURCES}} {{TESTS}}

[group('format')]
format-source:
    uv run --all-packages ruff format {{SOURCES}} {{TESTS}}
