[group('clean')]
clean: clean-coverage clean-mypy clean-pytest clean-python clean-ruff

[group('clean')]
clean-coverage:
    rm -rf .coverage*
    rm -rf coverage.xml
    rm -rf htmlcov/

[group('clean')]
clean-mypy:
    rm -rf .mypy_cache/

[group('clean')]
clean-pytest:
    rm -rf .pytest_cache/

[group('clean')]
clean-python:
    find . -type f -name '*.py[co]' -delete
    find . -type d -name __pycache__ -exec rm -r {} \+

[group('clean')]
clean-ruff:
    rm -rf .ruff_cache/

[confirm]
[group('clean')]
clean-venv:
    rm -rf .venv/
