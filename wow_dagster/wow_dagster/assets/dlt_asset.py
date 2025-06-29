# wow_dagster/assets/dlt_assets.py
from pathlib import Path

from dagster import AssetExecutionContext
from dagster_dlt import dlt_assets, DagsterDltResource
import dlt

from wow_api_dlt.pipeline import wow_api_source  

DB_PATH = (
    Path(__file__).resolve().parents[3] /
    "wow_api_dbt" / "wow_api_data.duckdb"
)

my_pipeline = dlt.pipeline(
    pipeline_name="wow_api_data",
    destination=dlt.destinations.duckdb(str(DB_PATH)),
    dataset_name="raw",
    progress="log",
)

@dlt_assets(
    dlt_source=wow_api_source(),
    dlt_pipeline=my_pipeline,
    name="raw_wow_data",
    group_name="raw",
)
def raw_wow_assets(
    context: AssetExecutionContext,
    dlt: DagsterDltResource,          
):
    """Kör DLT-hämtningen när du själv triggar den."""
    yield from dlt.run(context=context)
