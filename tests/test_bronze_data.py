"""Integration tests against the ingested bronze tables.

These require Databricks authentication and a completed bronze ingestion run.
Run them explicitly with:

    DATABRICKS_TESTS=1 uv run pytest tests/test_bronze_data.py
"""

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("DATABRICKS_TESTS") != "1",
    reason="set DATABRICKS_TESTS=1 to test the Databricks workspace",
)


def test_projetos_contract(spark):
    projetos = spark.table("lakehouse_vertice.bronze.projetos")
    assert projetos.count() == 60
    # The course data deliberately misspells the same three tools in eight ways.
    assert projetos.select("ferramenta").distinct().count() == 8


def test_custos_use_decimal_comma(spark):
    count = spark.sql(
        "SELECT COUNT(*) FROM lakehouse_vertice.bronze.custos WHERE valor LIKE '%,%'"
    ).collect()[0][0]
    assert count == 671


def test_feriados_keep_one_capture_per_run(spark):
    feriados = spark.table("lakehouse_vertice.bronze.feriados")
    assert feriados.count() > 0
    assert feriados.select("arquivo").distinct().count() == feriados.select("arquivo", "coletado_em").distinct().count()
