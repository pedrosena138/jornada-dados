"""Offline checks for the Databricks bundle and notebook sources."""

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _jobs():
    for resource in sorted((ROOT / "resources").glob("*.yml")):
        config = yaml.safe_load(resource.read_text())
        for job in config.get("resources", {}).get("jobs", {}).values():
            yield resource, job


def test_bundle_includes_every_resource_file():
    bundle = yaml.safe_load((ROOT / "databricks.yml").read_text())
    assert "resources/*.yml" in bundle["include"]


def test_every_notebook_task_points_to_an_existing_file():
    missing = []
    for resource, job in _jobs():
        for task in job.get("tasks", []):
            notebook_path = task.get("notebook_task", {}).get("notebook_path")
            if notebook_path and not (resource.parent / notebook_path).resolve().is_file():
                missing.append(f"{resource.name}:{task['task_key']} -> {notebook_path}")

    assert not missing, "notebook_path does not exist:\n" + "\n".join(missing)


def test_every_notebook_task_targets_a_databricks_notebook():
    for resource, job in _jobs():
        for task in job.get("tasks", []):
            notebook_path = task.get("notebook_task", {}).get("notebook_path")
            if not notebook_path:
                continue
            target = (resource.parent / notebook_path).resolve()
            if target.suffix == ".py":
                first_line = target.read_text().splitlines()[0]
                assert first_line == "# Databricks notebook source", target
            elif target.suffix == ".ipynb":
                assert json.loads(target.read_text()).get("nbformat") == 4, target


def test_notebook_sources_are_valid():
    notebooks = sorted(
        [
            *((ROOT / "src").rglob("*.py")),
            *((ROOT / "src").rglob("*.ipynb")),
        ]
    )
    assert notebooks, "no notebooks found under src/"
    for notebook in notebooks:
        if notebook.suffix == ".py":
            text = notebook.read_text()
            assert text.startswith("# Databricks notebook source"), notebook
            assert "# COMMAND ----------" in text, notebook
        else:
            contents = json.loads(notebook.read_text())
            assert contents.get("nbformat") == 4, notebook
            assert contents.get("cells"), notebook


def test_env_file_is_gitignored():
    ignored = {line.strip() for line in (ROOT / ".gitignore").read_text().splitlines()}
    assert ".env" in ignored
