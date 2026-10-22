"""Pytest configuration and shared fixtures.

The local test suite does not need Databricks. Tests that touch data request the
`spark` fixture, which lazily opens a Databricks Connect session. See
tests/test_bronze_data.py and set DATABRICKS_TESTS=1 to run those tests.
"""

import csv
import json
import os
import pathlib

try:
    import pytest
    from databricks.connect import DatabricksSession
    from databricks.sdk import WorkspaceClient
    from pyspark.sql import SparkSession
except ImportError:
    raise ImportError(
        "Test dependencies not found.\n\nRun tests using 'uv run pytest'. See http://docs.astral.sh/uv to learn more about uv."
    )


def _enable_fallback_compute():
    """Use serverless compute when no cluster is configured."""
    conf = WorkspaceClient().config
    if conf.serverless_compute_id or conf.cluster_id or os.environ.get("SPARK_REMOTE"):
        return

    print("☁️ no compute specified, falling back to serverless compute")
    os.environ["DATABRICKS_SERVERLESS_COMPUTE_ID"] = "auto"


@pytest.fixture()
def spark() -> SparkSession:
    """Provide a Databricks Connect SparkSession for integration tests."""
    _enable_fallback_compute()
    return DatabricksSession.builder.getOrCreate()


@pytest.fixture()
def load_fixture(spark: SparkSession):
    """Load a JSON or CSV file from fixtures/ into a Spark DataFrame."""

    def _loader(filename: str):
        path = pathlib.Path(__file__).parent.parent / "fixtures" / filename
        suffix = path.suffix.lower()
        if suffix == ".json":
            rows = json.loads(path.read_text())
            return spark.createDataFrame(rows)
        if suffix == ".csv":
            with path.open(newline="") as f:
                rows = list(csv.DictReader(f))
            return spark.createDataFrame(rows)
        raise ValueError(f"Unsupported fixture type for: {filename}")

    return _loader
