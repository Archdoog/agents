pre-pr:
    uv run --locked ruff check skills tests
    uv run --locked ruff format --check skills tests
    uv run --locked python -m unittest discover -s tests -v
    git diff --check
