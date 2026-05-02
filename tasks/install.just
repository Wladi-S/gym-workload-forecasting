[group('install')]
install: install-project

[group('install')]
install-hooks:
    uv run pre-commit install --hook-type=pre-push
    uv run pre-commit install --hook-type=commit-msg

[group('install')]
install-project:
    uv sync --all-groups

[group('install')]
install-rulesets:
    #!/usr/bin/env bash
    set -euo pipefail
    repo=$(gh repo view --json=name --jq=.name)
    owner=$(gh repo view --json=owner --jq=.owner.login)
    gh api --method POST -H "Accept: application/vnd.github+json" \
      "/repos/$owner/$repo/rulesets" --input=".github/rulesets/main.json"
