# jornada-dados

Databricks Declarative Automation Bundle for a Portuguese-language data course (fictional consultancy "Vértice"). The real work is in Databricks notebooks; the Python package scaffolding in `README.md` is stale template output.

## Before Databricks work
- Load the `databricks-core` skill first, then the matching product skill (`databricks-dabs`, `databricks-data-discovery`, `databricks-jobs`, ...). For data questions, prefer `databricks experimental aitools tools query` over manual catalog browsing.
- Never auto-select a CLI profile; ask which one to use. The `dev` target pins workspace `dbc-d2553c90-8b45.cloud.databricks.com`.
- If the Databricks AI skills are missing, install with `databricks aitools install`.

## Current repo facts
- Only a `dev` target exists; README's `--target prod` flow is stale.
- `databricks.yml` declares `catalog`/`schema` but assigns no values, so bundle commands need `--var catalog=... --var schema=...`.
- `resources/bronze_ingestion.job.yml` deploys the exported `.py` notebooks in `src/day02/`; the `.ipynb` files are the editing sources. Re-export after editing so both stay in sync. `databricks bundle validate` passes with the current paths.
- `pyproject.toml` is `package = false`; `uv sync --dev` works and `uv run pytest` runs the offline checks. `tests/test_bronze_data.py` is skipped unless `DATABRICKS_TESTS=1`.
- Ruff cannot lint the notebook sources: `%sql` cells in `.ipynb` look like syntax errors and Databricks globals (`spark`, `dbutils`) are undefined in exported `.py`. Run `uv run ruff check tests` instead.
- `.env` holds the Supabase/AWS credentials and is gitignored; never commit it. `dados/` is also gitignored.

## Layout
- `src/dayNN/*.ipynb` — Databricks source notebooks; cells separated by `# COMMAND ----------`, SQL cells start with `%sql`. Paths contain spaces and brackets: quote them.
- `src/day02/*.py` — Databricks notebook exports referenced by the job. They start with `# Databricks notebook source` and use `# MAGIC` for markdown/SQL cells.
- `resources/*.yml` — DAB resources; job key `bronze_ingestion` with tasks `holidays_ingestion` and `supabase_ingestion`.
- `tests/` — offline bundle/notebook checks plus opt-in bronze data tests. `fixtures/` is available to the `load_fixture` pytest fixture.
- `dados/` — gitignored local copy of the Supabase `bronze` bucket. Notebooks do **not** read it: they read `/Volumes/lakehouse_vertice/bronze/raw/<source>/` and write `lakehouse_vertice.bronze.*` tables. A fresh clone has no `dados/`.

## Commands
- Install deps: `uv sync --dev`
- Validate: `databricks bundle validate --var catalog=lakehouse_vertice --var schema=bronze`
- Deploy dev: `databricks bundle deploy --target dev --var catalog=lakehouse_vertice --var schema=bronze`
- Run job: `databricks bundle run bronze_ingestion --target dev` (use the job key, not the display name)
- All local tests: `uv run pytest`
- Single test: `uv run pytest tests/test_bundle.py::test_every_notebook_task_points_to_an_existing_file`
- Integration tests (requires auth and ingested data): `DATABRICKS_TESTS=1 uv run pytest tests/test_bronze_data.py`
- Lint: `uv run ruff check tests`

## Notebook quirks
- Keep the Portuguese teaching narrative: comments state the business question, intentional errors, and expected results. Don't "clean up" deliberate mistakes.
- `supabase_ingestion` is destructive: it drops all listed `lakehouse_vertice.bronze.*` tables and deletes raw folders before reloading from S3. Never run it casually.
- Supabase ingestion requires `S3_ENDPOINT`, `AWS_DEFAULT_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`; the job supplies only the first two via `base_parameters`. Never commit credentials.
- Holidays ingestion appends a timestamped JSON file per run; the table intentionally keeps every capture (one row set per `arquivo`/`coletado_em`).
